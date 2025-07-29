#!/bin/bash

# Update Python skin database from TypeScript source
# Usage: ./update_skin_data.sh

set -e  # Exit on any error

echo "🔄 Updating ROV skin database..."
echo "📍 Converting lib/skin.ts → ai_python/lib/skin.json"

# Check if we're in the right directory
if [ ! -f "../lib/skin.ts" ]; then
    echo "❌ Error: lib/skin.ts not found. Make sure you're running this from ai_python directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment and run conversion
source venv/bin/activate

# Check if convert_skin.py exists
if [ ! -f "convert_skin.py" ]; then
    echo "❌ Error: convert_skin.py not found"
    exit 1
fi

# Run the conversion
python convert_skin.py

if [ $? -eq 0 ]; then
    echo "✅ Successfully updated skin database!"
    echo "📄 File: ai_python/lib/skin.json"
    echo "🎮 Ready for Python OCR processing"
else
    echo "❌ Failed to update skin database"
    exit 1
fi

# source venv/bin/activate && python convert_skin.py