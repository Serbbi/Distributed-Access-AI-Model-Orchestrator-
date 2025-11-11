#!/bin/sh

FRONTEND_IP=${1:-${FRONTEND_IP:-"localhost"}}

echo "Using FRONTEND_IP: $FRONTEND_IP"

sed -i "s|\${FRONTEND_URL}|$FRONTEND_IP|g" /etc/config/kratos.yml

