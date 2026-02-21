#!/usr/bin/env bash
# Grant admin role to a user by email address.
# Usage: ./scripts/make_admin.sh user@example.com

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <email>"
  exit 1
fi

EMAIL="$1"
DB_PATH="${DB_PATH:-backend/lessonlines.db}"

if [ ! -f "$DB_PATH" ]; then
  echo "Error: Database not found at $DB_PATH"
  echo "Set DB_PATH environment variable if using a different location."
  exit 1
fi

sqlite3 "$DB_PATH" "UPDATE users SET is_admin = 1 WHERE email = '$EMAIL';"

UPDATED=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users WHERE email = '$EMAIL' AND is_admin = 1;")
if [ "$UPDATED" -eq 1 ]; then
  echo "Admin role granted to $EMAIL"
else
  echo "Error: User with email $EMAIL not found"
  exit 1
fi
