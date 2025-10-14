#!/usr/bin/env python3
"""Test script to verify JWT token generation and validation."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.security import create_access_token, decode_access_token
from app.config import settings

print("🔐 Testing JWT Token Generation and Validation\n")

# Test data
test_user_id = "123e4567-e89b-12d3-a456-426614174000"

print(f"📋 Configuration:")
print(f"  JWT Secret: {settings.jwt_secret[:20]}...")
print(f"  JWT Algorithm: {settings.jwt_algorithm}")
print(f"  JWT Expiration: {settings.jwt_expiration} seconds\n")

# Generate token
print(f"1️⃣ Creating token for user: {test_user_id}")
token = create_access_token(test_user_id)
print(f"✅ Token generated: {token[:50]}...\n")

# Decode token
print("2️⃣ Decoding token...")
decoded_user_id = decode_access_token(token)

if decoded_user_id:
    print(f"✅ Token decoded successfully!")
    print(f"   Extracted user_id: {decoded_user_id}")

    if decoded_user_id == test_user_id:
        print("✅ User ID matches! Token validation is working correctly.\n")
    else:
        print(f"❌ User ID mismatch!")
        print(f"   Expected: {test_user_id}")
        print(f"   Got: {decoded_user_id}\n")
else:
    print("❌ Failed to decode token\n")

# Test with invalid token
print("3️⃣ Testing with invalid token...")
invalid_token = "invalid.token.here"
result = decode_access_token(invalid_token)
if result is None:
    print("✅ Invalid token correctly rejected\n")
else:
    print(f"❌ Invalid token was accepted: {result}\n")

print("✅ All tests completed!")
