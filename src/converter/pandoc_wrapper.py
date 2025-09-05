# -*- coding: utf-8 -*-
import subprocess
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from enum import Enum
import logging
from utils.i18n_manager import t

class PandocError(Exception):
    """Pandoc related error"""
    pass

class ConversionQuality(Enum):
    """Conversion quality presets"""
    SIMPLE = "simple"      # Simple conversion, fastest
    STANDARD = "standard"  # Standard conversion, balanced quality and speed
    HIGH = "high"          # High quality conversion, slower

class PandocWrapper:
    """Pandoc command-line tool wrapper"""
    
    def __init__(self):
        self.pandoc_path = self._find_pandoc()
        self.logger = logging.getLogger(__name__)
        
        # Default conversion arguments
        self.default_args = [
            '--from', 'markdown',
            '--to', 'docx',
            '--standalone'
        ]
        
        # Quality preset arguments will be built dynamically based on version
        # This will be populated in get_quality_args method
        self.quality_presets = None
    
    def _find_pandoc(self) -> Optional[str]:
        """Find pandoc executable"""
        pandoc_path = shutil.which('pandoc')
        if pandoc_path:
            return pandoc_path
        
        # Search in common locations
        common_paths = [
            '/usr/local/bin/pandoc',
            '/usr/bin/pandoc',
            '/opt/homebrew/bin/pandoc',
            'C:\\Program Files\\Pandoc\\pandoc.exe',
            'C:\\Program Files (x86)\\Pandoc\\pandoc.exe'
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        
        return None
    
    def is_pandoc_available(self) -> bool:
        """Check if pandoc is available"""
        return self.pandoc_path is not None
    
    def get_pandoc_version(self) -> Optional[str]:
        """Get pandoc version information"""
        if not self.is_pandoc_available():
            return None
        
        try:
            result = subprocess.run(
                [self.pandoc_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse version information
                lines = result.stdout.split('\n')
                if lines:
                    version_line = lines[0]
                    if 'pandoc' in version_line.lower():
                        return version_line.strip()
            
            return None
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
            return None
    
    def get_pandoc_version_tuple(self) -> Optional[Tuple[int, int, int]]:
        """Get pandoc version as tuple (major, minor, patch)"""
        version_str = self.get_pandoc_version()
        if not version_str:
            return None
        
        try:
            # Extract version number from string like "pandoc 3.7.0.2" or "pandoc.EXE 3.7.0.2"
            import re
            match = re.search(r'pandoc(?:\.exe)?\s+(\d+)\.(\d+)(?:\.(\d+))?(?:\.(\d+))?', version_str.lower())
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                patch = int(match.group(3)) if match.group(3) else 0
                # 忽略第四个数字，只使用前三位进行版本比较
                return (major, minor, patch)
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def is_version_at_least(self, major: int, minor: int = 0, patch: int = 0) -> bool:
        """Check if pandoc version is at least the specified version"""
        current_version = self.get_pandoc_version_tuple()
        if not current_version:
            return False
        
        target_version = (major, minor, patch)
        return current_version >= target_version
    
    def get_quality_args(self, quality: ConversionQuality) -> List[str]:
        """Get quality-specific arguments based on pandoc version"""
        args = []
        
        if quality == ConversionQuality.SIMPLE:
            return args
        
        # Add citation processing only for modern pandoc versions
        if self.is_version_at_least(2, 11):
            # Pandoc >= 2.11 uses built-in citeproc
            args.append('--citeproc')
        # For older versions, don't add citeproc to avoid external dependency
        # User will be notified to upgrade for full functionality
        
        # Remove --number-sections to let template control numbering
        # args.append('--number-sections')  # Commented out per requirement
        
        if quality == ConversionQuality.HIGH:
            args.extend([
                '--table-of-contents',
                '--toc-depth=3'
            ])
        
        return args
    
    def get_version_warning(self) -> Optional[str]:
        """Get version warning message if pandoc version is too old"""
        if not self.is_pandoc_available():
            return t("validation.pandoc_not_installed")
        
        if not self.is_version_at_least(2, 11):
            version_str = self.get_pandoc_version()
            warning_parts = [
                t("pandoc.version.old_version", version=version_str),
                t("pandoc.version.limited_features"),
                t("pandoc.version.upgrade_recommendation")
            ]
            return " ".join(warning_parts)
        
        return None
    
    def convert_file(self, 
                    input_file: Path, 
                    output_file: Path,
                    template_file: Optional[Path] = None,
                    quality: ConversionQuality = ConversionQuality.STANDARD,
                    custom_args: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Convert single Markdown file to DOCX
        
        Args:
            input_file: Input Markdown file
            output_file: Output DOCX file
            template_file: DOCX template file
            quality: Conversion quality preset
            custom_args: Custom pandoc arguments
            
        Returns:
            (success_flag, error_message_or_success_message)
        """
        if not self.is_pandoc_available():
            return False, t("validation.pandoc_not_available")
        
        if not input_file.exists():
            return False, t("validation.file_not_exist", path=str(input_file))
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Build pandoc command
        cmd = [self.pandoc_path] + self.default_args.copy()
        
        # Add quality-specific arguments based on version
        quality_args = self.get_quality_args(quality)
        cmd.extend(quality_args)
        
        # Add template arguments
        if template_file and template_file.exists():
            cmd.extend(['--reference-doc', str(template_file)])
        
        # Add custom arguments
        if custom_args:
            cmd.extend(custom_args)
        
        # Add input output files
        cmd.extend([str(input_file), '-o', str(output_file)])
        
        try:
            # Execute conversion
            self.logger.debug(f"Executing command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=input_file.parent  # Execute in input file directory
            )
            
            if result.returncode == 0:
                if output_file.exists():
                    return True, t("conversion.success", input=input_file.name, output=output_file.name)
                else:
                    return False, t("conversion.no_output")
            else:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                return False, t("conversion.failed", error=error_msg)
                
        except subprocess.TimeoutExpired:
            return False, t("conversion.timeout")
        except subprocess.SubprocessError as e:
            return False, t("conversion.pandoc_error", error=str(e))
        except OSError as e:
            return False, t("conversion.system_error", error=str(e))
    
    
    def validate_template(self, template_file: Path) -> Tuple[bool, str]:
        """
        Validate DOCX template file availability
        
        Args:
            template_file: Template file path
            
        Returns:
            (valid_flag, validation_message)
        """
        if not template_file.exists():
            return False, t("templates_extended.does_not_exist")
        
        if template_file.suffix.lower() != '.docx':
            return False, t("templates_extended.must_be_docx")
        
        # Create temporary Markdown file for testing
        import tempfile
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_md:
                tmp_md.write("# Test Title\n\nThis is a test document.")
                tmp_md_path = Path(tmp_md.name)
            
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_docx:
                tmp_docx_path = Path(tmp_docx.name)
            
            # Try to convert using template
            success, message = self.convert_file(
                tmp_md_path, 
                tmp_docx_path, 
                template_file,
                ConversionQuality.SIMPLE
            )
            
            # Clean up temporary files
            if tmp_md_path.exists():
                tmp_md_path.unlink()
            if tmp_docx_path.exists():
                tmp_docx_path.unlink()
            
            if success:
                return True, t("templates_extended.validation_passed")
            else:
                return False, t("templates_extended.test_failed", error=message)
                
        except Exception as e:
            return False, t("templates_extended.validation_error", error=str(e))
    
    
    
    def get_installation_help(self) -> str:
        """Get pandoc installation help information"""
        # Build internationalized installation guide
        guide_parts = [
            t("pandoc.installation.guide_intro"),
            "",
            t("pandoc.installation.version_requirement"),
            "",
            t("pandoc.installation.macos_title"),
            f"  {t('pandoc.installation.macos_homebrew')}",
            f"  {t('pandoc.installation.macos_homebrew_command')}",
            f"  {t('pandoc.installation.macos_download')}",
            f"  {t('pandoc.installation.download_url')}",
            "",
            t("pandoc.installation.windows_title"),
            f"  {t('pandoc.installation.windows_download')}",
            f"  {t('pandoc.installation.download_url')}",
            f"  {t('pandoc.installation.windows_chocolatey')}",
            f"  {t('pandoc.installation.windows_chocolatey_command')}",
            f"  {t('pandoc.installation.windows_scoop')}",
            f"  {t('pandoc.installation.windows_scoop_command')}",
            "",
            t("pandoc.installation.linux_title"),
            f"  {t('pandoc.installation.linux_ubuntu')}",
            f"  {t('pandoc.installation.linux_ubuntu_command')}",
            f"  {t('pandoc.installation.linux_centos')}",
            f"  {t('pandoc.installation.linux_centos_command')}",
            "",
            t("pandoc.installation.compatibility_note"),
            "",
            t("pandoc.installation.after_installation")
        ]
        
        return "\n".join(guide_parts)

# Global pandoc instance
pandoc = PandocWrapper()