#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: ./stress-test.sh <IP_ADDRESS>"
  exit 1
fi

COOKIE_JAR=$(mktemp)

IP=$1
EMAIL="admin@example.com"
PASSWORD="asdASD123!@#?"
ITERATIONS=2

echo "Starting stress test on $IP"

RESP=$(curl -s -L -c "$COOKIE_JAR" -H "Accept: application/json" "$IP/self-service/login/browser")
if [ "$RESP" == "null" ]; then
  echo "Failed to start flow."
  exit 1
fi

FLOW_ID=$(echo "$RESP" | jq -r '.id')

echo "Flow token extracted: $FLOW_ID"

CSRF_TOKEN=$(echo "$RESP" | jq -r '.ui.nodes[] | select(.attributes.name=="csrf_token") | .attributes.value')

echo "CSRF_TOKEN extracted: $CSRF_TOKEN"

# CSRF_COOKIE_VALUE=$(awk '/csrf_token_/ {print $NF}' "$COOKIE_JAR")
# echo -e "$(echo "$IP" | awk -F[/:] '{print $4}')\tFALSE\t/\tFALSE\t0\tcsrf_token\t$CSRF_COOKIE_VALUE" >> "$COOKIE_JAR"
# cat "$COOKIE_JAR"

RESP=$(curl -s -i -X POST "$IP/self-service/login?flow=$FLOW_ID" \
  -b "$COOKIE_JAR" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
  "method": "password",
  "identifier": "'"$EMAIL"'",
  "password": "'"$PASSWORD"'",
  "csrf_token": "'"$CSRF_TOKEN"'"
  }')

echo "$RESP"

SESSION_COOKIE=$(echo "$RESP" | grep 'Set-Cookie' | grep ory_kratos_session | sed -E 's/Set-Cookie: ([^;]+);.*/\1/')
if [ -z "$SESSION_COOKIE" ]; then
  echo "Failed to get cookie."
  exit 1
fi

echo "$RESP"

echo "Logged in"

for ((i = 1; i <= ITERATIONS; i++)); do
  echo "Test $i/$ATTEMPTS..."
  curl -s -X GET "$IP/api/train/execute?modelId=models:seed1&dataId=data:seed2" \
    -H "Cookie: $SESSION_COOKIE"
done

echo "Stress test complete."

# Logout flow not implemented yet. May not be needed.
# LOGOUT_RESP=$(curl -s -b "$COOKIE_JAR" -H "Accept: application/json" "$IP/self-service/logout/browser")
# if [ "$LOGOUT_RESP" == "null" ]; then
#   echo "Failed to start logout flow."
#   exit 1
# fi

# echo "$LOGOUT_RESP"

# LOGOUT_URL=$(echo "$LOGOUT_RESP" | jq -r '.logout_url')

# echo "$LOGOUT_URL"

# LOGOUT_RESULT=$(curl -s -i -b "$COOKIE_JAR" "$LOGOUT_URL")

# echo "$LOGOUT_RESULT"

