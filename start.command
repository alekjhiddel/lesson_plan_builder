#!/bin/bash
cd /Users/bradwell/Documents/lesson_planner
echo ""
echo "🍎 Setting up IEP Lesson Planner..."
echo ""
python3 -m venv venv 2>/dev/null
source venv/bin/activate
pip install -r requirements.txt --quiet
echo ""
echo "✅ Ready! Launching..."
echo ""
python3 app.py
