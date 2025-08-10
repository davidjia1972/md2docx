# Developer Guide

This document provides comprehensive guidance for developers working with the md2docx project - a Python GUI application for converting Markdown files to DOCX documents.

## Project Overview

This is a Python GUI application for converting Markdown files to DOCX documents using pandoc and PySide6. The application features a simple, Google-like interface with drag-and-drop functionality, batch conversion, template management, and smart file naming.

## Project Naming Strategy

The project uses a layered naming approach:

- **Project Name**: `md2docx` - Used for repository name, executable files, and package distribution
- **Window Title**: `Markdown to Word` - Fixed English title displayed in window title bar, task bar, and system dialogs
- **Interface Title**: Multi-language translated title displayed within the application interface using the i18n system

This strategy provides:
- Technical clarity for developers and command-line usage (`md2docx`)
- Global compatibility for system-level identification (`Markdown to Word`)
- Localized user experience for interface elements (translated titles)

**Important**: The window title is intentionally NOT part of the translation system and should remain fixed as "Markdown to Word" for consistency across all language versions.

## Quick Start Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py

# Run from project root
cd src && python main.py
```

### Testing Commands
```bash
# Test pandoc availability (run in Python)
python -c "from src.converter.pandoc_wrapper import pandoc; print('Pandoc available:', pandoc.is_pandoc_available())"

# Test file scanning
python -c "from src.utils.file_scanner import quick_scan; print(quick_scan(['.'], recursive=True))"

# Test emoji processing (requires emoji package)
python -c "from src.utils.emoji_processor import emoji_processor; print('Emoji processor available:', emoji_processor.is_available())"
```

## Architecture Overview

### Core Components

1. **Configuration System** (`src/utils/config_manager.py`)
   - JSON-based settings persistence
   - User preferences and template management
   - Window state and UI settings

2. **Template Management** (`src/templates/template_manager.py`)
   - Built-in and user-defined DOCX templates
   - Template validation and copying
   - Smart template selection and remembering

3. **File Processing Pipeline**
   - `file_scanner.py`: Recursive Markdown file discovery
   - `file_namer.py`: Smart output naming with conflict resolution
   - `emoji_processor.py`: Emoji removal and temporary file management
   - `pandoc_wrapper.py`: Pandoc command-line interface
   - `batch_converter.py`: Multi-threaded conversion engine

4. **UI Layer** (`src/ui/main_window.py`)
   - Drag-and-drop file selection
   - Template picker with user additions
   - File naming strategy controls
   - Emoji removal option toggle
   - Real-time progress tracking

### Key Design Patterns

- **Signal-Slot Architecture**: Qt signals for UI updates and progress tracking
- **Thread Separation**: Background conversion threads to prevent UI blocking
- **Strategy Pattern**: File naming strategies (timestamp vs. increment)
- **Template Method**: Batch conversion with progress callbacks

## File Structure Logic

```
src/
├── main.py                    # Application entry point
├── ui/                        # User interface components
│   └── main_window.py         # Main application window
├── converter/                 # Core conversion logic
│   ├── pandoc_wrapper.py      # Pandoc command interface
│   ├── batch_converter.py     # Multi-file conversion engine
│   ├── progress_tracker.py    # Progress monitoring system  
│   └── file_namer.py          # Output file naming logic
├── utils/                     # Utility modules
│   ├── config_manager.py      # Configuration management
│   ├── emoji_processor.py     # Emoji removal and temp file handling
│   └── file_scanner.py        # Markdown file discovery
└── templates/                 # Template management
    └── template_manager.py    # DOCX template handling
```

## Development Guidelines

### When Adding Features

1. **UI Changes**: Update `main_window.py` and connect new signals
2. **Conversion Logic**: Extend `batch_converter.py` or create new converter modules
3. **File Operations**: Add utility functions to appropriate modules in `utils/`
4. **Settings**: Use `config_manager.py` for any persistent data

### Error Handling Patterns

- Use try-catch blocks with user-friendly error messages
- Log technical details while showing simple UI messages
- Validate inputs before starting long operations
- Provide recovery suggestions in error dialogs

### Signal Connections

The app uses Qt's signal-slot pattern extensively:
- Progress updates flow from `ProgressTracker` to UI
- File operations emit signals for async updates
- Template changes trigger config saves automatically

## Common Operations

### Adding a New File Format
1. Extend `file_scanner.py` to recognize the extension
2. Update `pandoc_wrapper.py` if new pandoc args needed
3. Test with validation in `batch_converter.py`

### Template System Extensions
1. Modify `template_manager.py` for new template features
2. Update UI in `main_window.py` for template controls
3. Extend config schema in `config_manager.py`

### UI Component Addition
1. Add component to `main_window.py` layout
2. Connect signals and implement handlers
3. Save relevant settings via `config_manager.py`

## Dependencies and Requirements

- **Python 3.8+**: Core runtime requirement
- **PySide6**: Qt bindings for GUI interface
- **emoji>=2.2.0**: Python package for emoji detection and removal
- **pandoc**: External binary for document conversion (must be installed separately)
- **pathlib**: Modern path handling (Python built-in)

## Known Limitations

1. **Template Creation**: Cannot generate DOCX templates programmatically - requires manual creation
2. **Progress Granularity**: Pandoc doesn't provide file-level progress, only batch progress available
3. **Large Files**: Very large Markdown files may cause UI freezing during conversion
4. **Complex Formats**: Some advanced Markdown features may not convert perfectly to DOCX

## Troubleshooting Common Issues

- **"Pandoc not found"**: User needs to install pandoc separately from https://pandoc.org
- **Template errors**: Check DOCX file validity and permissions in templates/ directory
- **Conversion failures**: Usually pandoc syntax issues - check source Markdown format
- **UI freezing**: Large batch operations - ensure background threading is working

When debugging conversion issues, check the logs directory for detailed pandoc output and error messages.

## Emoji Removal Feature

The application includes an optional emoji removal feature designed for professional document formatting. This feature addresses the common issue of AI-generated Markdown content containing excessive emoji characters that are inappropriate for formal documentation.

### Feature Overview

- **Purpose**: Automatically removes all emoji characters from Markdown files before conversion to DOCX
- **User Control**: Optional checkbox in the UI settings area (enabled by default)
- **Safe Processing**: Creates temporary cleaned files without modifying originals
- **Automatic Cleanup**: Manages temporary files throughout application lifecycle

### Technical Implementation

1. **UI Integration**: Checkbox positioned below language selector, integrated with file handling options
2. **Configuration**: Setting stored as `output_settings.remove_emoji` in config file (defaults to `true`)
3. **Processing Pipeline**: 
   - When enabled: Creates temporary cleaned files using `emoji.replace_emoji()`
   - When disabled: Uses original files directly (no change to existing logic)
4. **File Management**: Temporary files are tracked and cleaned up after each conversion and on application exit

### Key Components

- **`emoji_processor.py`**: Core module handling emoji removal and temporary file management
- **Integration in `batch_converter.py`**: Seamless integration into conversion pipeline
- **Temporary File Tracking**: Global tracking prevents file system littering
- **Error Handling**: Graceful fallback when emoji package unavailable

### Configuration Options

```json
{
  "output_settings": {
    "remove_emoji": true  // Enable/disable emoji removal
  }
}
```

### Usage Patterns

**Professional Documents**: Enable emoji removal (default) for formal business documents, technical documentation, and academic papers.

**Casual Content**: Disable emoji removal when converting personal notes, social media content, or informal documentation where emojis add value.

### Troubleshooting

- **Emoji package not found**: Feature automatically disabled, original files used
- **Temporary file issues**: Application includes comprehensive cleanup mechanisms
- **Performance impact**: Minimal - only processes files when emoji content is detected

## Internationalization (i18n) Guidelines

**CRITICAL RULE**: All user-facing text MUST use the internationalization system. No hardcoded strings are allowed in GUI code.

### Requirements

1. **No Hardcoded Strings**: All text displayed to users must use the `t()` function from the i18n system
2. **All Languages Must Be Updated**: When adding or modifying any user-facing text, ALL language resource files must be updated simultaneously
3. **Language Resource Files**: Located in `/locales/[lang_code]/messages.json`

### Supported Languages

Currently supported languages (11 total):
- 简体中文 (zh_CN)
- English (en_US)
- 繁體中文 (zh_TW)
- Français (fr_FR)
- Español (es_ES)
- Deutsch (de_DE)
- Português (pt_PT)
- Русский (ru_RU)
- Italiano (it_IT)
- 日本語 (ja_JP)
- 한국어 (ko_KR)

### Usage Examples

**Correct**:
```python
# Use translation function
label = QLabel(t("ui.labels.file_handling"))
tooltip = t("ui.tooltips.delete_from_list")
```

**Incorrect**:
```python
# Never hardcode strings
label = QLabel("文件处理:")
tooltip = "从列表中移除"
```

### Adding New Translatable Text

**CRITICAL WORKFLOW**: When adding new user-facing text, follow these mandatory steps:

1. **Update ALL Language Files**: Add the key-value pair to ALL 11 language files in `/locales/*/messages.json`
2. **Use Translation Function**: Use the `t()` function in code: `t("section.subsection.key")`
3. **Update Critical Keys List**: If the new text is essential for core functionality (buttons, error messages, main labels), add the key to `get_critical_translation_keys()` in `/src/utils/i18n_manager.py`
4. **Run Validation**: Execute `python check_translations.py --critical` to verify completeness
5. **Test Multiple Languages**: Switch between languages in the app to ensure proper display

### Language Resource Structure

```json
{
  "ui": {
    "labels": {
      "new_feature": "English text"
    },
    "tooltips": {
      "new_tooltip": "Tooltip text"
    }
  }
}
```

### Development Tools Maintenance

**IMPORTANT**: The internationalization system includes automated validation tools that must be maintained alongside the code.

#### Critical Translation Keys Management

The function `get_critical_translation_keys()` in `/src/utils/i18n_manager.py` defines keys that are essential for core application functionality. **This list MUST be updated** when adding new critical UI elements such as:

- Core navigation buttons (Start, Cancel, OK, etc.)
- Essential error messages and dialogs
- Main application labels and status messages
- File operation dialogs and confirmations

#### Examples of Critical vs Non-Critical Keys

**Critical Keys** (must update the list):
```
ui.buttons.start          # Main action button
ui.buttons.cancel         # Cancel operation
dialogs.error.title       # Error dialog titles
file_operations.save      # Core file operations
```

**Non-Critical Keys** (no need to update the list):
```
tooltips.advanced_option  # Optional tooltips
ui.labels.statistics      # Informational displays
help.documentation        # Help content
```

#### Validation Workflow

```bash
# After adding new translations
python check_translations.py --critical    # Check critical keys only
python check_translations.py --detailed    # Full completeness check
python check_translations.py --lang fr_FR  # Check specific language
```

#### Consequences of Not Following This Process

- **Broken translations**: Missing critical keys will show technical names to users
- **Failed validation**: The `check_translations.py` script will report incomplete coverage
- **Poor user experience**: Essential functionality may appear in English/technical format
- **Inconsistent interface**: Mixed languages across different parts of the application

This ensures the application maintains consistent internationalization across all supported languages.

## Project Maintenance

### Regular Maintenance Tasks

1. **Translation Updates**: Ensure all language files are complete and up-to-date
2. **Template Validation**: Verify DOCX templates are not corrupted
3. **Dependency Updates**: Keep Python packages current with security patches
4. **Pandoc Compatibility**: Test with newer Pandoc versions

### Validation Commands

```bash
# Verify translation completeness
python check_translations.py --critical

# Check icon resources
python check_icons.py

# Test core functionality
python -c "from src.converter.pandoc_wrapper import pandoc; print('Pandoc available:', pandoc.is_pandoc_available())"
```

### Project Quality Standards

**Quality Standards for Contributors**:
- ✅ Complete documentation in multiple languages
- ✅ Professional project structure and organization  
- ✅ Comprehensive multi-language support (11 languages)
- ✅ Security validation passed
- ✅ Community-friendly contribution guidelines
- ✅ Standard open-source licensing (MIT)
- ✅ Proper dependency management
- ✅ Professional issue and PR templates

### Target Audience

- Individual developers and content creators
- Small teams and organizations needing document conversion
- Multi-language environments requiring localized tools
- Users preferring GUI tools over command-line utilities

This guide ensures contributors can effectively work with the project while maintaining professional open-source standards and providing excellent user experience for the global developer community.