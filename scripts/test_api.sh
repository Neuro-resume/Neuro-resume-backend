#!/bin/bash
# Quick API test script

API_URL="http://localhost:8000/v1"

echo "🧪 Testing Neuro Resume API..."
echo ""

# Test 1: Health check
echo "1️⃣ Testing health endpoint..."
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo ""

# Test 2: Register user
echo "2️⃣ Registering new user..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser_'$(date +%s)'",
    "email": "test_'$(date +%s)'@example.com",
    "password": "test123456",
    "firstName": "Test",
    "lastName": "User"
  }')

echo "$REGISTER_RESPONSE" | python3 -m json.tool
TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Registration failed!"
    exit 1
fi

echo "✅ Registration successful!"
echo "Token: ${TOKEN:0:30}..."
echo ""
echo ""

# Test 3: Get user profile
echo "3️⃣ Getting user profile..."
curl -s -X GET "$API_URL/user/profile" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# Test 4: Create interview session
echo "4️⃣ Creating interview session..."
SESSION_RESPONSE=$(curl -s -X POST "$API_URL/interview/sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"language": "ru"}')

echo "$SESSION_RESPONSE" | python3 -m json.tool
SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
echo ""
echo ""

# Test 5: Get sessions list
echo "5️⃣ Getting sessions list..."
curl -s -X GET "$API_URL/interview/sessions" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

echo "✅ All tests completed!"
echo ""
echo "📝 Session ID: $SESSION_ID"
echo "🔑 Token: ${TOKEN:0:50}..."
