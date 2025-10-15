#!/bin/bash
# Neuro Resume API smoke tests aligned with handlers and OpenAPI specification.

set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8000}"
API_V1="${API_V1:-${API_BASE%/}/v1}"
HEALTH_URL="${HEALTH_URL:-${API_BASE%/}/health}"

log_step() {
  printf '\n== %s ==\n' "$1"
}

step_success() {
  printf '✅ %s\n' "$1"
}

require_tool() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Error: '$1' is required" >&2
    exit 1
  }
}

api_request() {
  local method="$1"
  local endpoint="$2"
  local body="${3:-}"
  local token="${4:-}"

  local url="$endpoint"
  if [[ ! "$endpoint" =~ ^https?:// ]]; then
    url="${API_V1}${endpoint}"
  fi

  local tmp="$(mktemp)"
  local args=(-sS -o "$tmp" -w "%{http_code}" -X "$method" "$url")

  if [[ -n "$body" ]]; then
    args+=(-H 'Content-Type: application/json' -d "$body")
  fi
  if [[ -n "$token" ]]; then
    args+=(-H "Authorization: Bearer $token")
  fi

  local status
  status="$(curl "${args[@]}")"

  if [[ ! "$status" =~ ^20[0-9]$ ]]; then
    echo "Request failed: $method $url (status $status)" >&2
    cat "$tmp" >&2
    rm -f "$tmp"
    exit 1
  fi

  cat "$tmp"
  rm -f "$tmp"
}

parse_json_value() {
  local json="$1"
  local expression="$2"
  JSON_INPUT="$json" python3 - "$expression" <<'PY'
import json
import os
import sys

data = json.loads(os.environ["JSON_INPUT"])
expr = sys.argv[1]
value = data

for key in expr.split('.'):
  if isinstance(value, dict):
    value = value[key]
  elif isinstance(value, list):
    value = value[int(key)]
  else:
    raise KeyError(expr)

if isinstance(value, (dict, list)):
  json.dump(value, sys.stdout)
else:
  sys.stdout.write(str(value))
PY
}

assert_json_condition() {
  local json="$1"
  local expression="$2"
  JSON_INPUT="$json" python3 - "$expression" <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["JSON_INPUT"])
expr = sys.argv[1]

if not eval(expr, {"payload": payload}):
  raise SystemExit(f"Assertion failed: {expr}\nPayload: {json.dumps(payload, indent=2)}")
PY
}

require_tool curl
require_tool python3

echo "Running Neuro Resume API smoke tests against ${API_V1}";

log_step "Health"
HEALTH_RESPONSE="$(api_request GET "$HEALTH_URL")"
assert_json_condition "$HEALTH_RESPONSE" "payload['status'] in ('healthy', 'degraded')"
step_success "Health endpoint responded"

UNIQUE="$(date +%s)"
USERNAME="cli_user_${UNIQUE}"
EMAIL="cli_user_${UNIQUE}@example.com"
PASSWORD="Test12345!"
NEW_PASSWORD="BetterPass123!"

log_step "Register"
REGISTER_PAYLOAD=$(cat <<EOF
{
  "username": "$USERNAME",
  "email": "$EMAIL",
  "password": "$PASSWORD"
}
EOF
)
REGISTER_RESPONSE="$(api_request POST "/auth/register" "$REGISTER_PAYLOAD")"
assert_json_condition "$REGISTER_RESPONSE" "'token' in payload and 'user' in payload"
step_success "Registration succeeded"

TOKEN="$(parse_json_value "$REGISTER_RESPONSE" "token")"
USER_ID="$(parse_json_value "$REGISTER_RESPONSE" "user.id")"

log_step "Login"
LOGIN_RESPONSE="$(api_request POST "/auth/login" "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")"
assert_json_condition "$LOGIN_RESPONSE" "payload['user']['id'] == '$USER_ID'"
TOKEN="$(parse_json_value "$LOGIN_RESPONSE" "token")"
step_success "Login succeeded"

log_step "Refresh token"
REFRESH_RESPONSE="$(api_request POST "/auth/refresh" "" "$TOKEN")"
assert_json_condition "$REFRESH_RESPONSE" "payload['token']"
TOKEN="$(parse_json_value "$REFRESH_RESPONSE" "token")"
step_success "Token refresh succeeded"

log_step "Fetch profile"
PROFILE_RESPONSE="$(api_request GET "/user/profile" "" "$TOKEN")"
assert_json_condition "$PROFILE_RESPONSE" "payload['id'] == '$USER_ID'"
step_success "Profile fetched"

log_step "Update profile"
UPDATE_PAYLOAD=$(cat <<EOF
{
  "username": "${USERNAME}_updated",
  "email": "updated_${EMAIL}"
}
EOF
)
UPDATED_PROFILE="$(api_request PATCH "/user/profile" "$UPDATE_PAYLOAD" "$TOKEN")"
assert_json_condition "$UPDATED_PROFILE" "payload['username'] == '${USERNAME}_updated'"
step_success "Profile updated"

USERNAME="${USERNAME}_updated"
EMAIL="updated_${EMAIL}"

log_step "Change password"
CHANGE_PAYLOAD=$(cat <<EOF
{
  "current_password": "$PASSWORD",
  "new_password": "$NEW_PASSWORD"
}
EOF
)
api_request POST "/user/change-password" "$CHANGE_PAYLOAD" "$TOKEN" >/dev/null
PASSWORD="$NEW_PASSWORD"
step_success "Password changed"

log_step "Login with new password"
LOGIN_RESPONSE="$(api_request POST "/auth/login" "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")"
TOKEN="$(parse_json_value "$LOGIN_RESPONSE" "token")"
step_success "Login with new password succeeded"

log_step "Create interview session"
SESSION_RESPONSE="$(api_request POST "/interview/sessions" '{}' "$TOKEN")"
assert_json_condition "$SESSION_RESPONSE" "payload['status'] == 'IN_PROGRESS'"
SESSION_ID="$(parse_json_value "$SESSION_RESPONSE" "id")"
step_success "Interview session created"

log_step "Get interview session"
SESSION_DETAILS="$(api_request GET "/interview/sessions/$SESSION_ID" "" "$TOKEN")"
assert_json_condition "$SESSION_DETAILS" "payload['id'] == '$SESSION_ID'"
step_success "Interview session fetched"

log_step "List interview sessions"
SESSIONS_LIST="$(api_request GET "/interview/sessions" "" "$TOKEN")"
assert_json_condition "$SESSIONS_LIST" "('data' in payload and isinstance(payload['data'], list))"
step_success "Interview sessions listed"

log_step "List session messages (expect empty)"
MESSAGES_EMPTY="$(api_request GET "/interview/sessions/$SESSION_ID/messages" "" "$TOKEN")"
assert_json_condition "$MESSAGES_EMPTY" "payload['messages'] == []"
step_success "Empty message list confirmed"

log_step "Send interview message"
MESSAGE_PAYLOAD='{"content": "I have 5 years of Python experience."}'
MESSAGE_RESPONSE="$(api_request POST "/interview/sessions/$SESSION_ID/messages" "$MESSAGE_PAYLOAD" "$TOKEN")"
assert_json_condition "$MESSAGE_RESPONSE" "payload['user_message']['role'] == 'user'"
step_success "Interview message sent"

log_step "Verify saved messages"
MESSAGES_AFTER="$(api_request GET "/interview/sessions/$SESSION_ID/messages" "" "$TOKEN")"
assert_json_condition "$MESSAGES_AFTER" "len(payload['messages']) == 2"
step_success "Message history contains user and AI messages"

log_step "Complete interview"
COMPLETE_RESPONSE="$(api_request POST "/interview/sessions/$SESSION_ID/complete" "" "$TOKEN")"
assert_json_condition "$COMPLETE_RESPONSE" "payload['resume_markdown']['content']"
RESUME_MARKDOWN="$(parse_json_value "$COMPLETE_RESPONSE" "resume_markdown.content")"
RESUME_FILENAME="$(parse_json_value "$COMPLETE_RESPONSE" "resume_markdown.filename")"
RESUME_MIME="$(parse_json_value "$COMPLETE_RESPONSE" "resume_markdown.mime_type")"
if [[ -z "$RESUME_MARKDOWN" ]]; then
  echo "Expected resume markdown content" >&2
  exit 1
fi
step_success "Interview session completed"

log_step "Download resume via dedicated endpoint"
RESUME_DOWNLOAD="$(api_request GET "/interview/sessions/$SESSION_ID/resume" "" "$TOKEN")"
if [[ -z "$RESUME_DOWNLOAD" ]]; then
  echo "Expected resume download content" >&2
  exit 1
fi
step_success "Resume endpoint returned markdown"

log_step "Delete additional session"
SECOND_SESSION="$(parse_json_value "$(api_request POST "/interview/sessions" '{}' "$TOKEN")" "id")"
api_request DELETE "/interview/sessions/$SECOND_SESSION" "" "$TOKEN" >/dev/null
step_success "Extra session deleted"

log_step "Logout"
api_request POST "/auth/logout" "" "$TOKEN" >/dev/null
step_success "Logout succeeded"

printf '\nAll smoke tests finished successfully.\n'
printf 'User: %s (%s)\n' "$USERNAME" "$EMAIL"
printf 'Session: %s\n' "$SESSION_ID"
printf 'Resume File: %s (%s)\n' "$RESUME_FILENAME" "$RESUME_MIME"
printf 'Resume Preview: %.40s...\n' "$RESUME_DOWNLOAD"
printf 'Resume Markdown (truncated): %.40s...\n' "$RESUME_MARKDOWN"
