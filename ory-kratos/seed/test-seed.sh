#!/bin/sh

# May need to update this to get it from the .env file
KRATOS_ADMIN_URL="http://localhost:4434"

for row in $(jq -c '.[]' users.json); do
    curl -X POST "$KRATOS_ADMIN_URL/admin/identities" \
        -H "Content-Type: application/json" \
        -d "$row"
done

echo "User seeding has completed."
