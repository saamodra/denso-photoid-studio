#!/bin/bash
# Launch ID Card Photo Machine with guaranteed visibility on macOS

echo "🚀 Launching ID Card Photo Machine..."

# Change to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Kill any existing instances
pkill -f "python main.py" 2>/dev/null || true
sleep 1

# Launch application in background
python main.py &
APP_PID=$!

echo "✅ Application started (PID: $APP_PID)"

# Wait a moment for the app to initialize
sleep 3

# Force the app to the foreground using AppleScript
osascript -e 'tell application "System Events"
    set pythonApps to (every process whose name contains "Python")
    repeat with pythonApp in pythonApps
        try
            set frontmost of pythonApp to true
            return "Python app brought to front"
        end try
    end repeat
end tell' > /dev/null 2>&1

echo "🎯 Application should now be visible!"
echo "   Look for 'ID Card Photo Machine' window"
echo "   If still not visible, check:"
echo "   - Dock for Python icon"
echo "   - Mission Control (F3)"
echo "   - Alt+Tab to cycle windows"

# Wait for user input to keep script alive
echo ""
echo "Press Enter to stop the application..."
read -r

# Clean shutdown
echo "🛑 Stopping application..."
kill $APP_PID 2>/dev/null || true
echo "✅ Application stopped"
