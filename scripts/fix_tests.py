#!/usr/bin/env python3
"""
Script to update tests to match OpenAPI specification.

Changes:
1. Replace data["items"] with data["data"]
2. Replace data["total"] with data["pagination"]["total"]
3. Replace data["status"] == "active" with data["status"] == "in_progress"
4. Replace user_id with userId
5. Replace integer IDs (99999) with placeholder UUIDs
"""

import re
import uuid
from pathlib import Path

# Generate a fake UUID for "not found" tests
FAKE_UUID = str(uuid.uuid4())


def fix_test_file(filepath: Path):
    """Fix a single test file."""
    print(f"Processing {filepath}...")

    with open(filepath, "r") as f:
        content = f.read()

    original_content = content

    # Fix pagination structure
    content = re.sub(r'data\["items"\]', 'data["data"]', content)
    content = re.sub(r'data\["total"\]',
                     'data["pagination"]["total"]', content)
    content = re.sub(r'len\(data\["items"\]\)', 'len(data["data"])', content)

    # Fix status
    content = re.sub(r'data\["status"\] == "active"',
                     'data["status"] == "in_progress"', content)
    content = re.sub(r'"status": "active"', '"status": "in_progress"', content)

    # Fix camelCase fields
    content = re.sub(r'"user_id"', '"userId"', content)
    content = re.sub(r'"created_at"', '"createdAt"', content)
    content = re.sub(r'"session_id"', '"sessionId"', content)
    content = re.sub(r'"message_count"', '"messageCount"', content)

    # Fix integer IDs to UUIDs
    content = re.sub(r'/sessions/99999"', f'/sessions/{FAKE_UUID}"', content)

    # Fix message field name
    content = re.sub(r'"content":', '"message":', content)

    # Fix full_name tests - keep as-is since we added property

    if content != original_content:
        with open(filepath, "w") as f:
            f.write(content)
        print(f"  ✅ Updated {filepath}")
        return True
    else:
        print(f"  ℹ️  No changes needed for {filepath}")
        return False


def main():
    """Main entry point."""
    test_dir = Path(__file__).parent.parent / "tests"

    test_files = [
        test_dir / "test_interview.py",
        test_dir / "test_user.py",
    ]

    print("🔧 Fixing test files to match OpenAPI specification...\n")

    updated_count = 0
    for test_file in test_files:
        if test_file.exists():
            if fix_test_file(test_file):
                updated_count += 1
        else:
            print(f"  ⚠️  File not found: {test_file}")

    print(f"\n✅ Done! Updated {updated_count} file(s)")
    print(f"\n📝 Fake UUID for 'not found' tests: {FAKE_UUID}")


if __name__ == "__main__":
    main()
