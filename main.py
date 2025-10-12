import os
import subprocess
from google import genai

# Убедитесь, что установлены библиотеки google-genai и pandoc

# Ключ берется из переменной окружения GEMINI_API_KEY
client = genai.Client()

# Пример промпта для генерации резюме в markdown
prompt = """
Пожалуйста, сгенерируй профессиональное резюме в формате markdown по следующим данным:
ФИО: Иван Иванов
Опыт: 5 лет в разработке программного обеспечения
Навыки: Python, MCP, API-интеграция
"""

# Запрос к Gemini (модель gemini-2.5-flash)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

# Получаем markdown текст резюме
resume_markdown = response.text

# # Сохраняем в markdown файл
md_filename = "resume.md"
with open(md_filename, "w", encoding="utf-8") as f:
    f.write(resume_markdown)

print(f"Markdown резюме сохранено в файл {md_filename}")

# Конвертация markdown в PDF с помощью pandoc (должен быть установлен pandoc)
pdf_filename = "resume.pdf"
subprocess.run(["pandoc", md_filename, "-o", pdf_filename, "--pdf-engine=xelatex"], check=True)

print(f"PDF резюме создано: {pdf_filename}")
