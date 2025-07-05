#!/bin/bash
# Simple entrypoint for Flask application

set -e

echo "=== Flask Chatbot Application Startup ==="

# Wait a moment for any dependencies
sleep 5

# Start the application directly
echo "Starting Flask application..."
exec "$@"
