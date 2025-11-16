#!/bin/bash
# Test script to start server with debug logging

cd /home/trevorfulham/Documents/github/reciever
source venv/bin/activate

export DEBUG=DEBUG

echo "===== Starting Desktop Casting Receiver with DEBUG logging ====="
echo "Press Ctrl+C to stop"
echo ""

python run.py
