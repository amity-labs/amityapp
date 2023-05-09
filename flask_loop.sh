#!/bin/sh

python3 -m pip install -r requirements.txt

while true
do
    echo "🚀 Starting AMITY..."
    python3 amityapp/app.py
    echo "💥 AMITY crashed. Restarting in 3 seconds..."
    sleep 3
done
