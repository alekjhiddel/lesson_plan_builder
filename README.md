# 🍎 IEP Lesson Planner

A privacy-first lesson plan generator for special education MSD/autism classrooms.

## What This Does

This app helps special education teachers generate personalized lesson plans using AI (ChatGPT), while keeping all student data 100% private and local.

- **Student names never leave your computer** — the app swaps names for "Child 1", "Child 2", etc. before anything goes to ChatGPT
- **Generates weekly classroom plans** with center rotations, staff assignments, and themed activities
- **Creates daily individual plans** for 1:1 aide time with each student
- **Considers IEP goals, physical needs, communication modes, and homeroom schedules**
- **Seasonal themes** built in (Christmas in December, spring in April, etc.)
- **Built-in web scraper** to save teaching resources that inform future plans

## Quick Start

### Mac
1. Double-click `start.command`
2. The first time, it will install required packages (takes ~30 seconds)
3. Your browser will open automatically to the app

### Windows
1. Double-click `start.bat`
2. The first time, it will install required packages (takes ~30 seconds)
3. Your browser will open automatically to the app

### Manual Start (any OS)
```bash
cd lesson_planner
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Requirements
- Python 3.8 or newer
- A web browser (Chrome, Safari, Firefox, Edge)
- Internet connection (only for ChatGPT interaction and web scraping)

## Privacy
- All student data is stored in the `data/` folder on your computer
- Names are NEVER sent to ChatGPT or any external service
- The app runs entirely on your computer (localhost:5000)
- No accounts, no cloud, no tracking

## How It Works
1. **Add your students** — Enter names, IEP goals, needs, homeroom schedule
2. **Generate a prompt** — The app builds a detailed prompt with anonymized names
3. **Copy to ChatGPT** — Click the copy button, paste into ChatGPT
4. **Process the response** — Paste ChatGPT's answer back, names get restored
5. **Print & use!** — View, print, or save the finished lesson plans

## Optional: API Mode
If you have an OpenAI API key, you can enable direct communication with ChatGPT (no copy/paste needed). Go to Settings to configure.

---

Made with ❤️ for special education teachers.
