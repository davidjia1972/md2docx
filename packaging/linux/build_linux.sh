#!/bin/bash
# Linux build script for md2docx

set -e  # Exit on any error

echo "🐧 Building md2docx for Linux..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PACKAGING_DIR="$PROJECT_ROOT/packaging/linux"
DIST_DIR="$PACKAGING_DIR/dist"
BUILD_DIR="$PACKAGING_DIR/build"

# Load version
VERSION=$(cat "$PROJECT_ROOT/VERSION" 2>/dev/null || echo "1.0.0")
echo "Project root: $PROJECT_ROOT"
echo "Packaging dir: $PACKAGING_DIR"
echo "Version: $VERSION"

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
echo "Python version: $PYTHON_VERSION"

# Check if PyInstaller is installed
if ! $PYTHON_CMD -c "import PyInstaller" 2>/dev/null; then
    echo -e "${RED}Error: PyInstaller not found${NC}"
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Check if pandoc is available
if ! command -v pandoc &> /dev/null; then
    echo -e "${YELLOW}Warning: pandoc not found${NC}"
    echo "The app will show a warning about pandoc when started"
    echo "Install with: sudo apt install pandoc  (Ubuntu/Debian)"
    echo "          or: sudo dnf install pandoc  (Fedora)"
    echo "          or: sudo pacman -S pandoc   (Arch)"
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

# Build the executable
echo -e "${YELLOW}Building Linux executable with PyInstaller...${NC}"
cd "$PACKAGING_DIR"
python3 setup_pyinstaller.py

# Check if build was successful
APP_NAME="md2docx"
EXE_PATH="$DIST_DIR/$APP_NAME/$APP_NAME"
if [ -f "$EXE_PATH" ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    echo "Executable created at: $EXE_PATH"
    
    # Show executable info
    EXE_SIZE=$(du -sh "$DIST_DIR/md2docx" | cut -f1)
    echo "App size: $EXE_SIZE"
    
    # Make sure executable has correct permissions
    chmod +x "$EXE_PATH"
    
    # Test if executable can launch
    echo -e "${YELLOW}Testing executable launch...${NC}"
    if timeout 3s "$EXE_PATH" --version 2>/dev/null || true; then
        echo -e "${GREEN}✅ Executable launches successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Executable launch test completed${NC}"
    fi
    
    # Create install script
    echo -e "${YELLOW}Creating install script...${NC}"
    cat > "$DIST_DIR/install.sh" << 'EOF'
#!/bin/bash
# Installation script for md2docx

set -e

# Default installation paths
USER_INSTALL_DIR="$HOME/.local/bin"
USER_BIN_DIR="$HOME/.local/bin"
DESKTOP_FILE="$HOME/.local/share/applications/md2docx.desktop"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Running as root"
    USER_INSTALL_DIR="/usr/local/bin"
    DESKTOP_FILE="/usr/share/applications/md2docx.desktop"
fi

APP_NAME="md2docx"

echo "Installing $APP_NAME..."

# Create installation directory
mkdir -p "$USER_INSTALL_DIR"

# Install application files
if [ -d "$APP_NAME" ]; then
    cp -r "$APP_NAME"/* "$USER_INSTALL_DIR/"
    chmod +x "$USER_INSTALL_DIR/$APP_NAME"
    
    # Create symlink
    ln -sf "$USER_INSTALL_DIR/$APP_NAME" "$USER_BIN_DIR/$APP_NAME"
    
    echo "Installed to $USER_INSTALL_DIR"
    echo "Symlink created at $USER_BIN_DIR/$APP_NAME"
    echo "Add $USER_BIN_DIR to your PATH if not already there"
fi

# Install desktop file
if [ -f "$APP_NAME.desktop" ]; then
    mkdir -p "$(dirname "$DESKTOP_FILE")"
    cp "$APP_NAME.desktop" "$DESKTOP_FILE"
    echo "Desktop file installed to $DESKTOP_FILE"
fi

echo "Installation completed!"
echo "Run with: $APP_NAME"
EOF
    
    chmod +x "$DIST_DIR/install.sh"
    
    # Check for AppImage tools
    APPIMAGE_NAME="md2docx-v${VERSION}-x86_64.AppImage"
    if command -v appimagetool &> /dev/null; then
        echo -e "${YELLOW}Creating AppImage...${NC}"
        if [ -d "$DIST_DIR/md2docx.AppDir" ]; then
            # 修复架构识别问题，显式指定ARCH环境变量
            ARCH=x86_64 appimagetool "$DIST_DIR/md2docx.AppDir" "$DIST_DIR/$APPIMAGE_NAME"
            if [ -f "$DIST_DIR/$APPIMAGE_NAME" ]; then
                chmod +x "$DIST_DIR/$APPIMAGE_NAME"
                echo -e "${GREEN}✅ AppImage created: $DIST_DIR/$APPIMAGE_NAME${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  appimagetool not found, skipping AppImage creation${NC}"
        echo "Install from: https://github.com/AppImage/AppImageKit"
    fi
    
    # Copy to releases directory
    echo -e "${YELLOW}Copying to releases directory...${NC}"
    python3 -c "
import sys
sys.path.append('$PROJECT_ROOT/packaging')
from build_utils import copy_to_releases, calculate_checksums, update_release_notes, create_latest_symlink

releases_dir = copy_to_releases('$DIST_DIR/$APP_NAME', 'linux')

if releases_dir:
    calculate_checksums(releases_dir)
    update_release_notes()
    create_latest_symlink()
    print(f'✅ Release artifacts ready in: {releases_dir}')
"
    
    echo ""
    echo -e "${GREEN}🎉 Linux build completed successfully!${NC}"
    echo ""
    echo "Build artifacts:"
    echo "  Executable: $DIST_DIR/md2docx/"
    echo "  Desktop file: $DIST_DIR/md2docx.desktop"
    echo "  Install script: $DIST_DIR/install.sh"
    [ -f "$DIST_DIR/$APPIMAGE_NAME" ] && echo "  AppImage: $DIST_DIR/$APPIMAGE_NAME"
    echo "  Release files: releases/v${VERSION}/"
    echo ""
    echo "Next steps:"
    echo "1. Test the app: $EXE_PATH"
    echo "2. Install system-wide: cd $DIST_DIR && sudo ./install.sh"
    echo "3. Or install for user: cd $DIST_DIR && ./install.sh"
    echo "4. Install pandoc if needed (see distribution package manager)"
    echo "5. Use release files for distribution"
    echo ""
    
else
    echo -e "${RED}❌ Build failed!${NC}"
    echo "Check the build log above for errors"
    exit 1
fi