#!/bin/bash
# ═══════════════════════════════════════════════════════════
# 🍎 IEP Lesson Planner — Mac Launcher
# Double-click this file to start the app!
# ═══════════════════════════════════════════════════════════

# Stay in the app's directory
cd "$(dirname "$0")"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  🍎 IEP Lesson Planner"
echo "═══════════════════════════════════════════════════════"
echo ""

# ─── Step 1: Check for Command Line Developer Tools ───
if ! xcode-select -p &>/dev/null; then
    echo "⚠️  First-time setup: Your Mac needs Command Line Developer Tools."
    echo ""
    echo "   This is a free Apple tool that lets Python work properly."
    echo "   It's completely safe — it's made by Apple."
    echo ""
    xcode-select --install 2>/dev/null
    echo "┌─────────────────────────────────────────────────┐"
    echo "│  A popup should have appeared on your screen.   │"
    echo "│                                                 │"
    echo "│  👉 Click 'Install' in that popup               │"
    echo "│  👉 Click 'Agree' to the license               │"
    echo "│  👉 Wait for it to finish (3-5 minutes)        │"
    echo "│                                                 │"
    echo "│  When it's done, come back here and press       │"
    echo "│  Enter to continue.                             │"
    echo "└─────────────────────────────────────────────────┘"
    echo ""
    read -p "Press Enter after the install finishes... "
    
    if ! xcode-select -p &>/dev/null; then
        echo ""
        echo "❌ Developer Tools didn't install correctly."
        echo "   Try: Open System Preferences → Software Update"
        echo "   Or ask Brad for help!"
        echo ""
        read -p "Press Enter to close... "
        exit 1
    fi
    echo "✅ Developer Tools installed!"
    echo ""
fi

# ─── Step 2: Find Python 3 ───
if command -v python3 &>/dev/null; then
    SYSTEM_PYTHON=python3
elif command -v python &>/dev/null; then
    SYSTEM_PYTHON=python
else
    echo "❌ Python is not installed."
    echo ""
    echo "   Install it from: https://www.python.org/downloads/"
    echo "   Then double-click start.command again."
    echo ""
    read -p "Press Enter to close... "
    exit 1
fi

echo "✅ Python found: $($SYSTEM_PYTHON --version)"

# ─── Step 3: Set up virtual environment (first time only) ───
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 First-time setup: Installing packages (about 30 seconds)..."
    echo ""
    $SYSTEM_PYTHON -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment."
        echo "   Try: $SYSTEM_PYTHON -m ensurepip"
        read -p "Press Enter to close... "
        exit 1
    fi
    ./venv/bin/pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install packages. Check your internet."
        read -p "Press Enter to close... "
        exit 1
    fi
    echo "✅ Setup complete!"
    echo ""
fi

# ─── Step 4: Launch the app using venv Python directly ───
# (This avoids "source activate" issues across Terminal sessions)
VENV_PYTHON="./venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment seems broken. Rebuilding..."
    rm -rf venv
    $SYSTEM_PYTHON -m venv venv
    ./venv/bin/pip install -r requirements.txt --quiet
    echo "✅ Rebuilt!"
    echo ""
fi

echo "═══════════════════════════════════════════════════════"
echo "  🌐 Opening in your browser..."
echo "  Address: http://127.0.0.1:5000"
echo ""
echo "  To STOP: Press Ctrl+C or close this window"
echo "═══════════════════════════════════════════════════════"
echo ""

# Run Flask using the venv's Python directly
$VENV_PYTHON app.py

# If we get here, the app exited
echo ""
echo "App stopped. Press Enter to close."
read
