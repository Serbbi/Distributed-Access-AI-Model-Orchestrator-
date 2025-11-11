#!/bin/sh

# May need to update this to get it from the .env file
KETO_WRITE_URL="http://localhost:4467"

for row in $(jq -c '.[]' relations.json); do
    curl -X PUT "$KETO_WRITE_URL/admin/relation-tuples" \
        -H "Content-Type: application/json" \
        -d "$row"
done

echo "Permission seeding has completed."
