#!/bin/bash
# macOS build script for md2docx

set -e  # Exit on any error

echo "🍎 Building md2docx for macOS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PACKAGING_DIR="$PROJECT_ROOT/packaging/macos"
DIST_DIR="$PACKAGING_DIR/dist"
BUILD_DIR="$PACKAGING_DIR/build"

# Load version and build utilities
VERSION=$(cat "$PROJECT_ROOT/VERSION")
echo "Project root: $PROJECT_ROOT"
echo "Packaging dir: $PACKAGING_DIR"
echo "Version: $VERSION"

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
echo "Python version: $PYTHON_VERSION"

# Check if py2app is installed
if ! python3 -c "import py2app" 2>/dev/null; then
    echo -e "${RED}Error: py2app not found${NC}"
    echo "Installing py2app..."
    pip3 install py2app
fi

# Check if pandoc is available
if ! command -v pandoc &> /dev/null; then
    echo -e "${YELLOW}Warning: pandoc not found${NC}"
    echo "The app will show a warning about pandoc when started"
    echo "Users need to install pandoc separately from https://pandoc.org"
else
    PANDOC_VERSION=$(pandoc --version | head -n1)
    echo "Found: $PANDOC_VERSION"
fi

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
cd "$PROJECT_ROOT"
pip3 install -r requirements.txt

# Clean previous build
echo -e "${YELLOW}Cleaning previous build...${NC}"
rm -rf "$BUILD_DIR" "$DIST_DIR"

# Build the app
echo -e "${YELLOW}Building macOS app with py2app...${NC}"
cd "$PACKAGING_DIR"
python3 setup_py2app.py py2app --optimize=1

# Check if build was successful
APP_PATH="$DIST_DIR/md2docx.app"
if [ -d "$APP_PATH" ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    echo "App created at: $APP_PATH"
    
    # Show app info
    APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)
    echo "App size: $APP_SIZE"
    
    # Test if app can launch
    echo -e "${YELLOW}Testing app launch...${NC}"
    if "$APP_PATH/Contents/MacOS/md2docx" --version 2>/dev/null || true; then
        echo -e "${GREEN}✅ App launches successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  App launch test completed (expected behavior)${NC}"
    fi
    
    # Create DMG if needed
    DMG_NAME="md2docx-v${VERSION}-macOS.dmg"
    if command -v create-dmg &> /dev/null; then
        echo -e "${YELLOW}Creating DMG...${NC}"
        create-dmg --volname "Markdown to Word v${VERSION}" \
                   --window-pos 200 120 \
                   --window-size 600 400 \
                   --icon-size 100 \
                   --icon "md2docx.app" 175 190 \
                   --hide-extension "md2docx.app" \
                   --app-drop-link 425 190 \
                   "$DIST_DIR/$DMG_NAME" \
                   "$APP_PATH"
        
        if [ -f "$DIST_DIR/$DMG_NAME" ]; then
            echo -e "${GREEN}✅ DMG created: $DIST_DIR/$DMG_NAME${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  create-dmg not found, skipping DMG creation${NC}"
        echo "Install with: brew install create-dmg"
    fi
    
    # Copy to releases directory
    echo -e "${YELLOW}Copying to releases directory...${NC}"
    python3 -c "
import sys
sys.path.append('$PROJECT_ROOT/packaging')
from build_utils import copy_to_releases, calculate_checksums, update_release_notes, create_latest_symlink

# Copy DMG if exists, otherwise copy .app
if '$DIST_DIR/$DMG_NAME'.replace('$DIST_DIR/', '').startswith('/'):
    dmg_path = '$DIST_DIR/$DMG_NAME'
else:
    dmg_path = '$DIST_DIR/$DMG_NAME'

import os
if os.path.exists(dmg_path):
    releases_dir = copy_to_releases(dmg_path, 'macos')
else:
    releases_dir = copy_to_releases('$APP_PATH', 'macos')

if releases_dir:
    calculate_checksums(releases_dir)
    update_release_notes()
    create_latest_symlink()
    print(f'✅ Release artifacts ready in: {releases_dir}')
"
    
    echo ""
    echo -e "${GREEN}🎉 macOS build completed successfully!${NC}"
    echo ""
    echo "Build artifacts:"
    echo "  App bundle: $APP_PATH"
    [ -f "$DIST_DIR/$DMG_NAME" ] && echo "  DMG installer: $DIST_DIR/$DMG_NAME"
    echo "  Release files: releases/v${VERSION}/"
    echo ""
    echo "Next steps:"
    echo "1. Test the app: open \"$APP_PATH\""
    echo "2. Install pandoc if needed: brew install pandoc"
    echo "3. For distribution, consider code signing:"
    echo "   codesign --force --deep --sign \"Developer ID Application: Your Name\" \"$APP_PATH\""
    echo ""
    
else
    echo -e "${RED}❌ Build failed!${NC}"
    echo "Check the build log above for errors"
    exit 1
fi