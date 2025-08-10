# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- **Core Features**
  - Markdown to DOCX conversion using Pandoc
  - Intuitive drag-and-drop interface
  - Batch processing of multiple files
  - Recursive folder scanning for Markdown files

- **Template System**
  - Built-in default DOCX template
  - Support for custom user templates
  - Template validation and management
  - Easy template browsing and selection

- **File Management**
  - Smart file naming with conflict resolution
  - Timestamp and incremental naming strategies
  - Automatic overwrite protection
  - Output preview functionality

- **Emoji Processing**
  - Optional emoji removal from Markdown files
  - Safe temporary file processing
  - Automatic cleanup of processed files
  - Professional document formatting support

- **Multi-language Support**
  - Complete internationalization (i18n) system
  - 11 supported languages:
    - English (en_US)
    - 简体中文 (zh_CN)
    - 繁體中文 (zh_TW)
    - Français (fr_FR)
    - Español (es_ES)
    - Deutsch (de_DE)
    - Português (pt_PT)
    - Русский (ru_RU)
    - Italiano (it_IT)
    - 日本語 (ja_JP)
    - 한국어 (ko_KR)

- **User Interface**
  - Clean, Google-like interface design
  - Real-time progress tracking with detailed feedback
  - Configurable settings with persistence
  - Context menus and tooltips
  - Responsive layout for different screen sizes

- **Technical Features**
  - Multi-threaded conversion engine
  - Comprehensive error handling and logging
  - Configuration management with JSON persistence
  - Pandoc integration with version detection
  - Icon management system with multiple formats

- **Developer Tools**
  - Translation validation scripts
  - Icon resource checking tools
  - Debugging and development utilities
  - Comprehensive documentation (CLAUDE.md)

### Technical Details
- **Python 3.8+** compatibility
- **PySide6** Qt-based GUI framework
- **Pandoc** external dependency for document conversion
- **emoji** library for emoji processing
- Modular architecture with clear separation of concerns
- Signal-slot pattern for UI updates and progress tracking

### Dependencies
- PySide6 >= 6.0.0
- emoji >= 2.2.0
- pathlib (built-in)
- External: Pandoc (must be installed separately)

[1.0.0]: https://github.com/yourusername/md2docx/releases/tag/v1.0.0