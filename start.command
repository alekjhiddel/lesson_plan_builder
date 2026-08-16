#!/bin/bash
# ═══════════════════════════════════════════════════════════
# 🍎 IEP Lesson Planner — Mac Launcher
# Double-click this file to start the app!
# ═══════════════════════════════════════════════════════════

cd "$(dirname "$0")"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  🍎 IEP Lesson Planner"
echo "═══════════════════════════════════════════════════════"
echo ""

# ─── Step 1: Check for Command Line Developer Tools ───
check_dev_tools() {
    if ! xcode-select -p &>/dev/null; then
        return 1
    fi
    return 0
}

if ! check_dev_tools; then
    echo "⚠️  First-time setup: Your Mac needs Command Line Developer Tools."
    echo ""
    echo "   This is a free Apple tool that lets Python work properly."
    echo "   It's completely safe — it's made by Apple."
    echo ""
    echo "   I'm going to ask your Mac to install it now..."
    echo ""
    
    # Trigger the install dialog
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
    
    # Verify it worked
    if ! check_dev_tools; then
        echo ""
        echo "❌ Hmm, it doesn't look like it installed correctly."
        echo ""
        echo "   Try these steps:"
        echo "   1. Open 'System Preferences' → 'Software Update'"
        echo "   2. If you see an update for Command Line Tools, install it"
        echo "   3. Then come back and double-click start.command again"
        echo ""
        echo "   If that doesn't work, ask Brad for help!"
        echo ""
        read -p "Press Enter to close... "
        exit 1
    fi
    
    echo "✅ Developer Tools installed successfully!"
    echo ""
fi

# ─── Step 2: Check for Python 3 ───
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "❌ Python is not installed on this Mac."
    echo ""
    echo "   To install Python:"
    echo "   1. Go to: https://www.python.org/downloads/"
    echo "   2. Click the big yellow 'Download Python' button"
    echo "   3. Open the downloaded file and follow the installer"
    echo "   4. Then come back and double-click start.command again"
    echo ""
    read -p "Press Enter to close... "
    exit 1
fi

echo "✅ Python found: $($PYTHON --version)"

# ─── Step 3: Set up virtual environment (first time only) ───
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 First-time setup: Installing required packages..."
    echo "   (This only happens once — takes about 30 seconds)"
    echo ""
    $PYTHON -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment."
        echo "   Try running: $PYTHON -m ensurepip"
        echo "   Then double-click start.command again."
        read -p "Press Enter to close... "
        exit 1
    fi
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install packages."
        echo "   Check your internet connection and try again."
        read -p "Press Enter to close... "
        exit 1
    fi
    echo "✅ Setup complete!"
else
    source venv/bin/activate
fi

# ─── Step 4: Launch the app ───
echo ""
echo "═══════════════════════════════════════════════════════"
echo "  🌐 Opening in your browser..."
echo "  Address: http://127.0.0.1:5000"
echo ""
echo "  To STOP the app: Press Ctrl+C or close this window"
echo "═══════════════════════════════════════════════════════"
echo ""

$PYTHON app.py
