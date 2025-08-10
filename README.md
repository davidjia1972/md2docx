# md2docx - Markdown to DOCX Converter

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://pypi.org/project/PySide6/)

> **English** | [简体中文](README_zh_CN.md)

A modern, user-friendly GUI application for converting Markdown files to DOCX documents using Pandoc. Designed with a clean, Google-like interface and powerful batch processing capabilities.

![Application Screenshot](assets/screenshot.png)

## ✨ Features

- **Intuitive Drag & Drop Interface** - Simply drag files or folders into the application
- **Batch Conversion** - Process multiple Markdown files simultaneously
- **Template Support** - Use custom DOCX templates for consistent formatting
- **Smart File Naming** - Automatic naming with conflict resolution (timestamp/increment)
- **Emoji Removal** - Optional emoji filtering for professional documents
- **Multi-language Support** - Available in 11 languages
- **Real-time Progress Tracking** - Monitor conversion progress with detailed feedback
- **Recursive Folder Scanning** - Automatically find Markdown files in subdirectories

## 🌍 Supported Languages

- **English** (en_US)
- **简体中文** (zh_CN) 
- **繁體中文** (zh_TW)
- **Français** (fr_FR)
- **Español** (es_ES) 
- **Deutsch** (de_DE)
- **Português** (pt_PT)
- **Русский** (ru_RU)
- **Italiano** (it_IT)
- **日本語** (ja_JP)
- **한국어** (ko_KR)

## 📋 Requirements

- **Python 3.8+** - Core runtime
- **PySide6** - GUI framework (installed via requirements.txt)
- **Pandoc** - Document conversion engine (must be installed separately)
- **emoji** - Emoji processing library (installed via requirements.txt)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/md2docx.git
cd md2docx
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Pandoc

**macOS:**
```bash
# Using Homebrew (recommended)
brew install pandoc

# Or download from official website
# https://pandoc.org/installing.html
```

**Windows:**
```bash
# Using Chocolatey
choco install pandoc

# Using Scoop
scoop install pandoc

# Or download installer from https://pandoc.org/installing.html
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install pandoc
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install pandoc
# or
sudo dnf install pandoc
```

### 4. Run the Application
```bash
python src/main.py
```

## 📖 Usage

### Basic Conversion
1. Launch the application
2. Drag and drop Markdown files or folders into the interface
3. Select conversion options (template, file naming, emoji removal)
4. Click "Start" to begin conversion

### Template Management
- **Built-in Templates**: Use the default template for standard formatting
- **Custom Templates**: Add your own DOCX templates by:
  - Copying `.docx` files to the `templates/user/` directory
  - Using the "Browse..." button to select template files
  - Templates should contain desired styles, fonts, and page layouts

### File Naming Options
- **Overwrite**: Replace existing files with the same name
- **Auto Rename**: Add timestamps or incremental numbers to avoid conflicts

### Emoji Processing
- **Remove Emoji Characters**: Automatically strip emoji from Markdown before conversion
- Useful for professional documents and formal documentation
- Creates temporary cleaned files without modifying originals

## 🏗️ Project Structure

```
md2docx/
├── src/
│   ├── main.py                    # Application entry point
│   ├── ui/                        # User interface components
│   │   ├── main_window.py         # Main application window
│   │   ├── drag_drop_area.py      # Drag and drop functionality
│   │   ├── file_list_widget.py    # File list management
│   │   ├── output_settings.py     # Conversion settings panel
│   │   └── progress_dialog.py     # Progress tracking dialog
│   ├── converter/                 # Core conversion logic
│   │   ├── pandoc_wrapper.py      # Pandoc command interface
│   │   ├── batch_converter.py     # Multi-file conversion engine
│   │   ├── progress_tracker.py    # Progress monitoring system
│   │   └── file_namer.py          # Output file naming logic
│   ├── utils/                     # Utility modules
│   │   ├── config_manager.py      # Configuration management
│   │   ├── emoji_processor.py     # Emoji removal and temp file handling
│   │   ├── file_scanner.py        # Markdown file discovery
│   │   ├── i18n_manager.py        # Internationalization system
│   │   └── icon_manager.py        # Application icons
│   └── templates/                 # Template management
│       └── template_manager.py    # DOCX template handling
├── locales/                       # Translation files
│   ├── en_US/messages.json        # English translations
│   ├── zh_CN/messages.json        # Chinese (Simplified)
│   └── [other languages]/         # Additional language packs
├── templates/                     # DOCX template storage
│   ├── default.docx               # Built-in template
│   └── user/                      # User custom templates
├── config/                        # Configuration files
├── assets/                        # Application assets
│   └── icons/                     # Application icons
└── requirements.txt               # Python dependencies
```

## 🔧 Development

### Architecture Overview

The application follows a modular architecture with clear separation of concerns:

- **UI Layer**: PySide6-based interface with drag-and-drop support
- **Conversion Engine**: Multi-threaded batch processing using Pandoc
- **Template System**: DOCX template management and validation  
- **Configuration**: JSON-based settings persistence
- **Internationalization**: Complete i18n system with 11 languages

### Key Design Patterns

- **Signal-Slot Architecture**: Qt signals for UI updates and progress tracking
- **Thread Separation**: Background conversion threads prevent UI blocking
- **Strategy Pattern**: Configurable file naming strategies
- **Template Method**: Extensible conversion pipeline with progress callbacks

### Adding New Features

1. **UI Changes**: Update relevant components in `src/ui/`
2. **Conversion Logic**: Extend `batch_converter.py` or create new converter modules
3. **Settings**: Use `config_manager.py` for persistent configuration
4. **Translations**: Add new keys to ALL language files in `locales/`

### Testing and Validation

```bash
# Test Pandoc availability
python -c "from src.converter.pandoc_wrapper import pandoc; print('Pandoc available:', pandoc.is_pandoc_available())"

# Validate translations
python check_translations.py --critical

# Check icon resources
python check_icons.py
```

## 🌐 Internationalization

### Adding New Languages

1. Create new directory: `locales/[lang_code]/`
2. Copy `locales/en_US/messages.json` as template
3. Translate all key-value pairs
4. Update `config/languages.json` with new language entry
5. Test with `python check_translations.py --lang [lang_code]`

### Translation Guidelines

- **All UI text must use the i18n system** - No hardcoded strings allowed
- **Update ALL language files** when adding new translatable text
- **Use the `t()` function** in code: `t("ui.buttons.start")`
- **Validate completeness** with `check_translations.py`

### Critical Translation Keys

Essential keys that must be present in all language files:
- Core buttons (`ui.buttons.*`)
- Error messages (`dialogs.*.title`, `dialogs.*.message`)
- Main labels (`ui.labels.*`)
- File operations (`file_operations.*`)

## 🛠️ Maintenance

### Regular Maintenance Tasks

1. **Translation Updates**: Ensure all language files are complete and up-to-date
2. **Template Validation**: Verify DOCX templates are not corrupted
3. **Dependency Updates**: Keep Python packages current with security patches
4. **Pandoc Compatibility**: Test with newer Pandoc versions

### Debugging Common Issues

**"Pandoc not found"**:
- Ensure Pandoc is installed and in system PATH
- Restart application after Pandoc installation

**Template errors**:
- Check DOCX file validity and permissions in `templates/` directory
- Verify template files are not corrupted or password-protected

**Conversion failures**:
- Check source Markdown syntax compatibility with Pandoc
- Review logs in `logs/converter.log` for detailed error information

**UI freezing**:
- Large batch operations should run in background threads
- Check for blocking operations in main UI thread

### Log Files

Application logs are stored in `logs/converter.log` with detailed information about:
- Conversion operations and results
- Error messages and stack traces
- Pandoc command execution details
- Template validation results

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Add tests for new functionality
5. Update translations for all supported languages
6. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
7. Push to the branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

## 📞 Support

If you encounter any problems or have questions:

1. Check the [Issues](https://github.com/yourusername/md2docx/issues) page
2. Review the troubleshooting section in this README
3. Check application logs in `logs/converter.log`
4. Create a new issue with detailed information about your problem

## 🙏 Acknowledgments

- [Pandoc](https://pandoc.org/) - Universal document converter
- [PySide6](https://pypi.org/project/PySide6/) - Qt for Python
- [emoji](https://pypi.org/project/emoji/) - Emoji processing library
- All contributors and translators who helped make this project multilingual

---

**Note**: This application requires Pandoc to be installed separately. While the application will run without Pandoc, conversion functionality will not be available until Pandoc is properly installed and accessible from the system PATH.