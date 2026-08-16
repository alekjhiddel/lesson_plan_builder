# 🔧 IEP Lesson Planner — Troubleshooting Guide

Having trouble? This guide covers the most common issues. Start with your problem below.

---

## Table of Contents
- [Installation Issues (Mac)](#installation-issues-mac)
- [Installation Issues (Windows)](#installation-issues-windows)
- [App Won't Start](#app-wont-start)
- [Browser Issues](#browser-issues)
- [Lesson Plan Issues](#lesson-plan-issues)
- [Knowledge Base / Scraper Issues](#knowledge-base--scraper-issues)
- [API Mode Issues](#api-mode-issues)
- [Data & Backup](#data--backup)

---

## Installation Issues (Mac)

### "No developer tools were found" / "Install requested for command line developer tools"

**What's happening:** Your Mac needs Apple's free Command Line Tools to run Python properly.

**Fix:**
1. A popup should appear asking to install — click **"Install"**
2. Click **"Agree"** to the license
3. Wait 3-5 minutes for the download (it's about 150MB)
4. When you see "Software installed" or the popup closes, double-click `start.command` again

**If no popup appeared:**
1. Open **Terminal** (search for it in Spotlight: Cmd+Space, type "Terminal")
2. Type: `xcode-select --install`
3. Press Enter
4. Click "Install" when the popup appears
5. After it finishes, double-click `start.command` again

**If it says "already installed" but still doesn't work:**
1. Open Terminal
2. Type: `sudo xcode-select --reset`
3. Enter your password (you won't see it typing — that's normal)
4. Try `start.command` again

---

### "Permission denied" when double-clicking start.command

**Fix:**
1. Open **Terminal**
2. Type: `chmod +x ` (with a space after the +x)
3. Drag the `start.command` file into the Terminal window (this pastes the path)
4. Press Enter
5. Now double-click `start.command` again

---

### "start.command can't be opened because it is from an unidentified developer"

**Fix:**
1. Right-click (or Control+click) on `start.command`
2. Select **"Open"** from the menu
3. Click **"Open"** in the dialog that appears
4. You only need to do this once — after that, double-click works

---

### "Python is not installed"

**Fix:**
1. Go to: https://www.python.org/downloads/
2. Click the big yellow **"Download Python 3.x"** button
3. Open the downloaded `.pkg` file
4. Follow the installer (just click "Continue" and "Install")
5. Restart Terminal or double-click `start.command` again

---

### "pip: command not found" or "No module named pip"

**Fix:**
1. Open Terminal
2. Type: `python3 -m ensurepip`
3. Press Enter
4. Try `start.command` again

---

## Installation Issues (Windows)

### "Python is not recognized"

**What happened:** Python wasn't added to your system PATH during installation.

**Fix (easiest):**
1. Uninstall Python (Settings → Apps → Python → Uninstall)
2. Re-download from https://www.python.org/downloads/
3. Run the installer and **CHECK THE BOX** that says **"Add Python to PATH"** ← This is the critical step!
4. Click "Install Now"
5. Double-click `start.bat` again

---

### "Access denied" errors during pip install

**Fix:**
1. Right-click `start.bat`
2. Select **"Run as administrator"**
3. After first install succeeds, you can double-click normally going forward

---

## App Won't Start

### "Address already in use" / "Port 5000 already in use"

**What happened:** The app is already running in another window, or something else is using port 5000.

**Fix:**
- Close any other Terminal/Command Prompt windows running the app
- On Mac: `lsof -i :5000` to see what's using it, then `kill <PID>`
- Or just restart your computer (easiest)

---

### "ModuleNotFoundError: No module named 'flask'"

**What happened:** The virtual environment didn't install properly.

**Fix:**
1. Delete the `venv` folder inside the lesson_plan_builder folder
2. Double-click `start.command` / `start.bat` again (it will reinstall)

---

### App starts but browser doesn't open

**Fix:** Manually open your browser and go to: **http://127.0.0.1:5000**

---

## Browser Issues

### Page shows "This site can't be reached" / "Connection refused"

**What happened:** The app isn't running.

**Fix:** Make sure the Terminal/Command Prompt window is open and shows "IEP Lesson Planner is running!"

---

### Page looks broken (no styling)

**What happened:** CSS file isn't loading.

**Fix:**
1. Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
2. If that doesn't work, clear browser cache for localhost

---

## Lesson Plan Issues

### Plans aren't using my students' real names

**What happened:** The de-anonymization step might have failed.

**Check:**
- Make sure you're pasting into the **"Process Response"** page (not just reading the raw ChatGPT output)
- The mapping depends on having the SAME students saved when you process as when you generated

---

### Plans are too generic / not personalized enough

**Fix:** Add more detail to your student profiles:
- More specific IEP goals (with criteria)
- Reinforcers (what motivates each kid)
- Communication details (not just "AAC" — which device? How many buttons?)
- Behavioral needs (what triggers them? What de-escalates?)

---

### Plans don't match my schedule

**Fix:**
1. Go to **Schedule** → **Edit Staffing Setup**
2. Make sure your time blocks, homeroom schedules, and aide info are correct
3. Regenerate the schedule
4. Then generate new lesson plans (the schedule is auto-included)

---

### ChatGPT's response is too long / gets cut off

**What happened:** ChatGPT hit its output limit.

**Fix:**
- In ChatGPT, type: "Please continue from where you left off"
- Copy BOTH responses and paste them together in the Process Response page
- Or: Generate "Daily Individual Plans Only" separately from the weekly plan

---

## Knowledge Base / Scraper Issues

### "Could not reach the website"

**Possible causes:**
- No internet connection
- The website is blocking automated access
- The URL is incorrect

**Fix:**
- Check your internet
- Make sure the URL starts with `http://` or `https://`
- Some sites (Pinterest, Facebook) block scrapers — try a different source

---

### Scraped content looks garbled

**What happened:** The site has heavy JavaScript that the scraper can't process.

**This is normal** for some sites. The app gets what it can. The summary might be imperfect but still useful as context.

---

## API Mode Issues

### "API call failed"

**Possible causes:**
- Invalid API key
- Ran out of OpenAI credits
- Internet connection issue

**Fix:**
1. Go to Settings → check your API key is correct
2. Visit https://platform.openai.com/usage to check your balance
3. Switch back to copy/paste mode while troubleshooting

---

### "openai package not installed"

**Fix:**
1. Open Terminal
2. Navigate to the lesson_plan_builder folder
3. Run: `source venv/bin/activate`
4. Run: `pip install openai`
5. Restart the app

---

## Data & Backup

### Where is my data stored?

Everything is in the `data/` folder inside the app:
```
lesson_plan_builder/
└── data/
    ├── students.json          ← All student profiles
    ├── config.json            ← App settings
    ├── schedule_config.json   ← Staffing/schedule setup
    ├── knowledge_base/        ← Scraped resources
    └── lesson_plans/          ← Generated plan history
```

### How do I back up my data?

Copy the entire `data/` folder to a USB drive or safe local location.
**Do NOT put it in cloud storage** (Google Drive, iCloud, Dropbox) — student names are in there!

### How do I move to a new computer?

1. Copy the entire `lesson_plan_builder` folder to the new machine
2. Delete the `venv` folder (it won't work on a different machine)
3. Double-click `start.command` / `start.bat` — it will set up fresh

---

## Still Stuck?

Ask Brad! Or open an issue on GitHub: https://github.com/alekjhiddel/lesson_plan_builder/issues
