"""Gemini-powered interview orchestration service."""

from __future__ import annotations

import asyncio
import json
import logging
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence

from app.config import settings
from app.models.session import Message, MessageRole

try:  # Optional dependency for environments without google-genai installed
    from google import genai  # type: ignore
except ImportError:  # pragma: no cover - graceful degradation when package is missing
    genai = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class GeminiTurn:
    """Structured response from the Gemini interview service."""

    ai_message: str
    progress_state: Dict[str, Any]
    completed: bool = False
    resume_markdown: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class GeminiInterviewService:
    """Coordinate interview flow with Gemini (or a deterministic fallback)."""

    _question_bank: Sequence[str] = (
        "Какую роль вы сейчас занимаете и чем гордитесь в ней?",
        "Расскажите про проект, которым особенно гордитесь: что сделали лично вы?",
        "Какие инструменты и навыки используете чаще всего на работе?",
        "Какие цели ставите перед собой на ближайший год и почему они важны?",
        "Есть ли образование или курсы, которые обязательно стоит упомянуть?",
    )

    def __init__(self) -> None:
        self._enabled = bool(settings.gemini_api_key and genai)
        self._model_name = settings.gemini_model
        self._client = None
        if self._enabled:
            try:
                self._client = genai.Client(
                    api_key=settings.gemini_api_key)  # type: ignore[call-arg]
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Failed to initialize Gemini client: %s", exc)
                self._enabled = False

    async def generate_intro(
        self,
        conversation_id: str,
        *,
        welcome_context: str,
    ) -> GeminiTurn:
        """Produce a greeting turn for a fresh conversation."""

        if self._enabled and self._client is not None:
            try:
                return await self._call_gemini(
                    conversation_id=conversation_id,
                    messages=(),
                    preface=welcome_context,
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning(
                    "Gemini intro call failed, using fallback conversation: %s",
                    exc,
                )

        return self._fallback_intro(conversation_id=conversation_id)

    async def process_turn(
        self,
        conversation_id: str,
        messages: Sequence[Message],
    ) -> GeminiTurn:
        """Generate the next AI turn based on conversation history."""

        # Attempt real Gemini call when configured, otherwise fallback.
        if self._enabled and self._client is not None:
            try:
                return await self._call_gemini(
                    conversation_id=conversation_id,
                    messages=messages,
                )
            except Exception as exc:  # pragma: no cover - fallback safety
                logger.warning(
                    "Gemini call failed, using fallback conversation: %s", exc)

        return self._fallback_turn(
            conversation_id=conversation_id,
            messages=messages,
        )

    async def _call_gemini(
        self,
        conversation_id: str,
        messages: Sequence[Message],
        *,
        preface: Optional[str] = None,
    ) -> GeminiTurn:
        """Invoke Gemini model and parse structured response."""

        prompt = self._build_prompt(
            conversation_id=conversation_id,
            messages=messages,
            preface=preface,
        )
        loop = asyncio.get_running_loop()

        def _invoke() -> Any:
            generation_config = {
                "temperature": 0.7,
                "response_mime_type": "application/json",
            }

            return self._client.models.generate_content(  # type: ignore[union-attr]
                model=self._model_name,
                contents=prompt,
                config=generation_config,
            )

        response = await loop.run_in_executor(None, _invoke)
        raw = getattr(response, "text", "") if response else ""

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Gemini returned non-JSON payload, using fallback.")
            return self._fallback_turn(
                conversation_id=conversation_id,
                messages=messages,
            )

        ai_message = payload.get(
            "assistant_message") or payload.get("question")
        resume_markdown = payload.get("resume_markdown")
        completed = bool(payload.get("completed"))
        progress_state = payload.get("progress_state") or {}
        metadata_raw = payload.get("metadata")
        if isinstance(metadata_raw, dict):
            metadata = metadata_raw
        elif isinstance(metadata_raw, str):
            # Gemini sometimes returns a plain string summary; wrap to keep schema stable.
            metadata = {"summary": metadata_raw.strip()}
        else:
            metadata = None

        if not isinstance(progress_state, dict):
            progress_state = {}
        if not ai_message:
            return self._fallback_turn(
                conversation_id=conversation_id,
                messages=messages,
            )

        progress_state = self._normalise_progress_state(
            progress_state, completed, messages)

        return GeminiTurn(
            ai_message=ai_message,
            progress_state=progress_state,
            completed=completed,
            resume_markdown=resume_markdown,
            metadata=metadata,
        )

    def _fallback_turn(
        self,
        conversation_id: str,
        messages: Sequence[Message],
    ) -> GeminiTurn:
        """Heuristic interviewer that keeps behaviour deterministic per session."""

        user_messages = [m for m in messages if self._coerce_role(
            m.role) == MessageRole.USER]
        ai_messages = [m for m in messages if self._coerce_role(
            m.role) == MessageRole.AI]
        stage = len(ai_messages)

        question = self._select_question(
            conversation_id=conversation_id,
            stage=stage,
        )
        progress_state = self._construct_progress_state(
            stage=stage, user_messages=user_messages)

        if question is not None:
            metadata = {
                "analysis": {
                    "answers_collected": len(user_messages),
                    "topics": [self._find_keywords(msg.content) for msg in user_messages],
                }
            }
            return GeminiTurn(
                ai_message=question,
                progress_state=progress_state,
                completed=False,
                metadata=metadata,
            )

        # No more questions -> synthesize resume and close interview.
        resume_markdown = self._build_resume_markdown(user_messages)
        closing_message = (
            "Спасибо! На основе ваших ответов я подготовил черновик резюме и сохранил его. "
            "Сообщите, если нужна правка."
        )
        progress_state["percentage"] = 100
        metadata = {
            "analysis": {
                "answers_collected": len(user_messages),
                "topics": [self._find_keywords(msg.content) for msg in user_messages],
            }
        }
        return GeminiTurn(
            ai_message=closing_message,
            progress_state=progress_state,
            completed=True,
            resume_markdown=resume_markdown,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _fallback_intro(self, conversation_id: str) -> GeminiTurn:
        rng = random.Random(int(conversation_id.replace("-", ""), 16))
        openers = (
            "Привет! Я карьерный ассистент NeuroResume. Давайте вместе соберём сильное резюме. Расскажите, какая роль вас интересует и чего хотите добиться?",
            "Здравствуйте! Я помогу структурировать ваш опыт и цели. С чего начнём: какую позицию или направление вы рассматриваете сейчас?",
            "Рад знакомству! Я здесь, чтобы системно оформить ваши достижения. Расскажите, на какую роль нацелены и что важно подчеркнуть?",
        )
        message = rng.choice(openers)
        return GeminiTurn(
            ai_message=message,
            progress_state={"percentage": 0},
            completed=False,
        )

    def _select_question(self, conversation_id: str, stage: int) -> Optional[str]:
        order = list(self._question_bank)
        rng = random.Random(int(conversation_id.replace("-", ""), 16))
        rng.shuffle(order)
        if stage < len(order):
            return order[stage]
        return None

    def _construct_progress_state(
        self,
        stage: int,
        user_messages: Sequence[Message],
    ) -> Dict[str, Any]:
        # Smooth saturation curve: minimal progress after first answer, max 95 before completion.
        total_questions = len(self._question_bank)
        answered = len(user_messages)
        ratio = answered / max(total_questions, 1)
        percentage = int(min(95, math.ceil(100 * ratio * 0.9 + 5 * ratio)))
        if answered <= 1:
            percentage = max(10, percentage)
        topics = [self._find_keywords(msg.content)
                  for msg in user_messages[-3:]]
        return {
            "percentage": percentage,
            "answers_collected": answered,
            "recent_topics": [topic for topic in topics if topic],
        }

    def _coerce_role(self, value: Any) -> MessageRole:
        if isinstance(value, MessageRole):
            return value
        try:
            return MessageRole(str(value))
        except ValueError:
            return MessageRole.AI

    def _normalise_progress_state(
        self,
        progress_state: Dict[str, Any],
        completed: bool,
        messages: Sequence[Message],
    ) -> Dict[str, Any]:
        value = dict(progress_state)
        pct = value.get("percentage")
        if pct is None:
            answered = len(
                [m for m in messages if self._coerce_role(m.role) == MessageRole.USER])
            value["percentage"] = min(100, answered * 20)
        else:
            value["percentage"] = max(0, min(100, int(pct)))
        if completed:
            value["percentage"] = 100
        return value

    def _find_keywords(self, text: str) -> str:
        lowered = text.lower()
        for marker in ("python", "data", "управ", "дизайн", "sales", "маркет"):
            if marker in lowered:
                return marker
        words = [w.strip(",.;:!?") for w in text.split() if len(w) > 4]
        return words[0].lower() if words else ""

    def _build_prompt(
        self,
        conversation_id: str,
        messages: Sequence[Message],
        *,
        preface: Optional[str] = None,
    ) -> str:
        history_lines: List[str] = []
        for message in messages:
            prefix = "Пользователь" if message.role == MessageRole.USER else "AI"
            history_lines.append(f"{prefix}: {message.content}")
        joined_history = "\n".join(history_lines[-20:])
        base_instruction = (
            "Ты — ассистент по карьерному интервью. "
            "Твоя задача — задавать уточняющие вопросы, собирать информацию и, когда данных достаточно,"  # noqa: E501
            " сформировать итоговое резюме.\n"
            "Всегда возвращай JSON со следующими полями:\n"
            "assistant_message: вопрос или финальное сообщение пользователю;\n"
            "completed: true/false;\n"
            "progress_state: объект с числовым полем percentage;\n"
            "resume_markdown: markdown-резюме (только если completed=true);\n"
            "metadata: краткий разбор или ключевые слова.\n"
            f"ID диалога: {conversation_id}.\n"
            "История диалога:\n"
            f"{joined_history}\n"
            "Ответь строго в JSON без пояснений."
        )
        if preface:
            return f"{preface.strip()}\n\n{base_instruction}"
        return base_instruction

    def _build_resume_markdown(self, user_messages: Sequence[Message]) -> str:
        answers = [msg.content.strip()
                   for msg in user_messages if msg.content.strip()]
        if not answers:
            answers = ["Информация будет уточнена с кандидатом дополнительно."]

        name = self._extract_name(answers)
        goals = self._extract_goal(answers)
        skills = self._extract_skills(answers)
        achievements = self._extract_achievements(answers)
        education = self._extract_education(answers)

        lines = [
            f"# {name or 'Резюме кандидата'}",
            "",
            "## Цель",
            goals or "Развитие в интересной роли с возможностью влиять на продукт.",
            "",
            "## Опыт",
        ]
        if achievements:
            lines.extend([f"- {item}" for item in achievements])
        else:
            lines.append(
                "- Опыт будет детализирован после уточнения подробностей.")

        lines.extend([
            "",
            "## Навыки",
        ])
        if skills:
            lines.append(", ".join(skills))
        else:
            lines.append(
                "Готов сотрудничать и быстро осваивать новые инструменты.")

        lines.extend([
            "",
            "## Образование",
            education or "Информация об образовании уточняется.",
        ])

        lines.extend([
            "",
            "## Дополнительно",
            "Готов к обсуждению предложений и открыт к новым вызовам.",
        ])

        return "\n".join(lines)

    # Simple heuristics for extracting fields -------------------------------------------------
    def _extract_name(self, answers: Sequence[str]) -> Optional[str]:
        for answer in answers:
            if "меня" in answer.lower() and "зовут" in answer.lower():
                raw = answer.split("зовут", 1)[-1].strip()
                return raw.split()[0:2] and " ".join(raw.split()[0:2])
        return None

    def _extract_goal(self, answers: Sequence[str]) -> Optional[str]:
        for answer in answers:
            if "цель" in answer.lower() or "хочу" in answer.lower():
                return answer
        return None

    def _extract_skills(self, answers: Sequence[str]) -> List[str]:
        skills: List[str] = []
        for answer in answers:
            lowered = answer.lower()
            if "навы" in lowered or "skill" in lowered or "уме" in lowered:
                parts = [chunk.strip().capitalize()
                         for chunk in answer.replace(";", ",").split(",")]
                skills.extend([part for part in parts if part])
        # Deduplicate while preserving order
        seen = set()
        unique: List[str] = []
        for skill in skills:
            key = skill.lower()
            if key not in seen:
                seen.add(key)
                unique.append(skill)
        return unique

    def _extract_achievements(self, answers: Sequence[str]) -> List[str]:
        achievements: List[str] = []
        for answer in answers:
            if any(marker in answer.lower() for marker in ("результ", "достиг", "улуч")):
                achievements.append(answer)
        return achievements

    def _extract_education(self, answers: Sequence[str]) -> Optional[str]:
        for answer in answers:
            if "университет" in answer.lower() or "академ" in answer.lower() or "бакалавр" in answer.lower():
                return answer
        return None


_service_instance: Optional[GeminiInterviewService] = None


def get_gemini_service() -> GeminiInterviewService:
    """Provide a singleton-like service instance for FastAPI dependencies."""

    global _service_instance
    if _service_instance is None:
        _service_instance = GeminiInterviewService()
    return _service_instance
