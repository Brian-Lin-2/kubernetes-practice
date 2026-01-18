#!/bin/sh
# This script creates a new todo pointing to a random Wikipedia article

# Backend URL (change if needed)
BACKEND_URL="http://todo-server-svc:3001/todos"

# Generate random Wikipedia URL
RANDOM_WIKI="https://en.wikipedia.org/wiki/Special:Random"

# Create the todo via POST request
curl -s -X POST "$BACKEND_URL" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Read $RANDOM_WIKI\", \"done\": false}" \
  || echo "Failed to create todo"

