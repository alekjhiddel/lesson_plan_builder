# 🍎 IEP Lesson Planner — User Guide

Welcome! This guide will walk you through everything you need to know to use the IEP Lesson Planner.

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Adding Your Students](#adding-your-students)
3. [Setting Up Your Schedule](#setting-up-your-schedule)
4. [Generating Lesson Plans](#generating-lesson-plans)
5. [Processing ChatGPT's Response](#processing-chatgpts-response)
6. [Using the Knowledge Base](#using-the-knowledge-base)
7. [Viewing Plan History](#viewing-plan-history)
8. [Settings](#settings)
9. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### First Launch
1. Double-click `start.command` (Mac) or `start.bat` (Windows)
2. Your browser will open automatically to the app
3. You'll see the **Setup Wizard** — fill in:
   - Your name
   - School name (optional)
   - How many students you have
   - How many aides you have
   - Whether you have a floater
   - School start/end times
4. Click "Get Started!" — you're in!

### The Dashboard
After setup, you'll land on your **Dashboard**. It shows:
- How many students you have
- This month's theme suggestions
- Quick action buttons to jump to common tasks

---

## Adding Your Students

Click **"My Students"** in the sidebar, then **"+ Add Student"**.

### What to Fill In

**Basic Info** — Name, age, grade
> 🔒 Names NEVER leave your computer. When we generate prompts for ChatGPT, names are swapped to "Child 1", "Child 2", etc.

**Communication** — How does this student communicate?
- Pick their primary mode (verbal, AAC device, PECS, sign, etc.)
- Add details (e.g., "Uses TouchChat with 32 buttons, can request 'more' and 'help'")

**Needs & Profile**
- *Cognitive*: Functioning level, learning style (e.g., "Functions at 2-3 year level, strong visual learner")
- *Physical*: Wheelchair, vision, hearing, seizures, etc. (one per line)
- *Behavioral*: BIP info, triggers, what works (e.g., "Elopes when overstimulated, use token board")
- *Sensory*: What they seek/avoid (e.g., "Needs weighted lap pad, avoids loud sounds")

**Motivators** — What makes this kid light up? What will they work for?
- This is CRUCIAL for good lesson plans! (e.g., "iPad time, bubbles, goldfish crackers")

**IEP Goals** — Copy these straight from the IEP document, one per line
- Include the full measurable goal with criteria
- Example: "Given a visual schedule, will independently transition between 3 activities with no more than 1 verbal prompt in 4/5 opportunities"

**Homeroom** — Does this student go to general ed?
- If yes: how long, what time, and does an aide need to go with them?

**Life Skills Priorities** — The BIG goals for independence
- Toileting, dressing, eating, communication, safety, etc.

**Notes** — Anything else! This grows over time.
- What works, what doesn't, parent requests, therapist ideas, breakthroughs

### Tips for Student Profiles
- **Start simple** — you can always add more later
- **Update regularly** — after an ARC meeting, when goals change, when you discover something new
- **Be specific about reinforcers** — "iPad" is okay; "iPad with YouTube nursery rhymes, 3 minutes max" is better
- **Include the prompting level** — helps generate better aide plans

---

## Setting Up Your Schedule

Click **"Schedule"** in the sidebar, then **"Set Up Staffing"**.

### What to Configure

**Your Aides**
- How many dedicated aides do you have?
- Their names (optional but makes the schedule easier to read)

**Floater**
- Do you have one? What's their name?

**Partner Teacher** (if applicable)
- Connected room? How many of their aides?
- Does the floater cover both rooms?

**Safety Rules**
- Minimum aides in your room at all times (default: 1)
- The app will NEVER create a schedule that drops below this

### Generating a Schedule
Once configured, click **"Generate Optimized Schedule"** — the computer figures out:
- Who covers what during each time block
- Who escorts kids to homeroom
- Warnings if coverage gets thin
- A printable staff grid

---

## Generating Lesson Plans

Click **"Generate Plans"** in the sidebar.

### Step 1: Choose What to Generate
- **Full Weekly Plan** — Whole classroom schedule + daily 1:1 plans for each child
- **Daily Individual Plans Only** — Just the aide plans (if you already have the classroom schedule)

### Step 2: Theme & Timing
- The app suggests a seasonal theme automatically
- You can pick a different month or enter a custom theme
- Custom themes change MATERIALS, not the skills being taught

### Step 3: Add Notes (optional)
- "Field trip Wednesday, skip afternoon centers"
- "New student starting Thursday"
- "Focus on fine motor this week"

### Step 4: Click "Generate Prompt"
- The app builds a detailed prompt with all your student info (anonymized!)
- A screen shows you the prompt with a big **"Copy to Clipboard"** button

### Step 5: Paste into ChatGPT
1. Click "Copy to Clipboard" (you'll see a ✅ confirmation)
2. Open [chat.openai.com](https://chat.openai.com)
3. Paste (Cmd+V on Mac, Ctrl+V on Windows)
4. Press Enter and wait for ChatGPT to generate your plans

---

## Processing ChatGPT's Response

After ChatGPT gives you the lesson plans:

1. Select ALL the text ChatGPT generated (Cmd+A / Ctrl+A)
2. Copy it (Cmd+C / Ctrl+C)
3. Go back to the Lesson Planner app
4. Click **"Process Response"** in the sidebar
5. Paste into the big text box
6. Click **"Process & Save Plan"**

The app will:
- Replace "Child 1" → real student names
- Save the plan to your history
- Display it nicely for viewing/printing

### Printing Plans
- Click the **🖨️ Print** button on the processed plan
- Each aide's section prints cleanly on separate pages

---

## Using the Knowledge Base

Click **"Resources"** in the sidebar.

Found a great website with teaching ideas? Save it!

1. Paste the URL in the box
2. Click **"Scrape & Save"**
3. The app fetches the key content and saves a summary

**Why this matters:** Saved resources get included as context in your ChatGPT prompts, so the AI learns from YOUR preferred teaching approaches.

Great sites to add:
- TeachersPayTeachers lesson pages
- Autism Classroom Resources blog posts
- The Autism Helper articles
- Pinterest boards with activity ideas (the text descriptions)

---

## Viewing Plan History

Click **"Plan History"** in the sidebar.

All your generated plans are saved automatically. You can:
- View any past plan
- Print old plans
- The app looks at previous plans to avoid repetition

---

## Settings

Click **"Settings"** in the sidebar.

**Classroom Info** — Update school name, aide count, schedule
**API Mode** (optional) — If you get an OpenAI API key, the app can talk to ChatGPT directly (no copy/paste needed). Usually ~$5-20/month.

---

## Tips & Best Practices

### Weekly Workflow
1. **Monday morning** (or Sunday night): Generate this week's plans
2. **Print aide plans** for each day
3. **Post center plans** at each station
4. **Friday**: Add notes to student profiles (what worked, what didn't)

### Getting Better Results from ChatGPT
- **More detail in student profiles = better plans**
- **Update IEP goals** when they change at ARC meetings
- **Add to Notes** when you discover something (e.g., "Marcus learned 'more' this week!")
- **Use the Knowledge Base** — the more resources you save, the better the plans get

### Privacy Reminders
- ✅ Student names NEVER go to ChatGPT
- ✅ All data stays on YOUR computer
- ✅ The `data/` folder is where everything is stored
- ✅ If you get a new computer, just copy the whole `lesson_plan_builder` folder
- ❌ Don't put the `data/` folder in cloud storage (Google Drive, iCloud) — that defeats the privacy purpose

---

## Need Help?

Check the **TROUBLESHOOTING.md** file for common issues, or ask Brad!
