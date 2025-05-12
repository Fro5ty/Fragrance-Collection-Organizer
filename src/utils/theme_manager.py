#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2025 Fragrance Collection Organizer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PySide6.QtGui import QPalette, QColor, QFont
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QObject, Signal, QSettings

class ThemeManager(QObject):
    """
    Manages application themes and allows switching between them
    """
    theme_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        self._current_theme = "dark"  # Default theme
        self._themes = {}
        
        # Initialize themes
        self._initialize_themes()
        
        # Load saved theme if any
        self._load_theme_preference()
    
    def _initialize_themes(self):
        """Initialize all available themes"""
        # Dark theme (default)
        self._themes["dark"] = {
            "name": "Dark Elegance",
            "palette": {
                "background": QColor(22, 22, 25),
                "background_alt": QColor(30, 30, 35),
                "foreground": QColor(230, 230, 235),
                "primary": QColor(156, 136, 255),
                "secondary": QColor(219, 166, 130)
            },
            "stylesheet": self._get_dark_stylesheet
        }
        
        # Light theme
        self._themes["light"] = {
            "name": "Light Elegance",
            "palette": {
                "background": QColor(245, 245, 247),
                "background_alt": QColor(230, 230, 235),
                "foreground": QColor(35, 35, 40),
                "primary": QColor(130, 110, 229),
                "secondary": QColor(219, 123, 80)
            },
            "stylesheet": self._get_light_stylesheet
        }
        
        # Nature theme
        self._themes["nature"] = {
            "name": "Emerald Veil",
            "palette": {
                "background": QColor(35, 42, 37),
                "background_alt": QColor(45, 55, 48),
                "foreground": QColor(220, 230, 220),
                "primary": QColor(120, 180, 120),
                "secondary": QColor(200, 180, 120)
            },
            "stylesheet": self._get_nature_stylesheet
        }
        
        # Midnight theme
        self._themes["midnight"] = {
            "name": "Midnight Blue",
            "palette": {
                "background": QColor(15, 22, 35),
                "background_alt": QColor(25, 35, 50),
                "foreground": QColor(220, 225, 235),
                "primary": QColor(80, 145, 230),
                "secondary": QColor(100, 195, 220)
            },
            "stylesheet": self._get_midnight_stylesheet
        }
        
        # Monochrome theme
        self._themes["monochrome"] = {
            "name": "Monochrome",
            "palette": {
                "background": QColor(18, 18, 18),
                "background_alt": QColor(30, 30, 30),
                "foreground": QColor(220, 220, 220),
                "primary": QColor(180, 180, 180),
                "secondary": QColor(150, 150, 150)
            },
            "stylesheet": self._get_monochrome_stylesheet
        }
        
        # Reverse Monochrome theme
        self._themes["reverse_monochrome"] = {
            "name": "Light Monochrome",
            "palette": {
                "background": QColor(220, 220, 220),
                "background_alt": QColor(200, 200, 200),
                "foreground": QColor(18, 18, 18),
                "primary": QColor(70, 70, 70),
                "secondary": QColor(100, 100, 100)
            },
            "stylesheet": self._get_reverse_monochrome_stylesheet
        }
        
        # Violet theme
        self._themes["violet"] = {
            "name": "Violet Dream",
            "palette": {
                "background": QColor(35, 25, 50),
                "background_alt": QColor(45, 35, 65),
                "foreground": QColor(230, 220, 240),
                "primary": QColor(180, 120, 220),
                "secondary": QColor(220, 140, 180)
            },
            "stylesheet": self._get_violet_stylesheet
        }
    
    def get_theme_names(self):
        """Get a list of available theme names in the specified order"""
        # Define the order of themes
        theme_order = ["dark", "light", "monochrome", "reverse_monochrome", "nature", "midnight", "violet"]
        
        # Return the themes in the specified order
        return [(theme_id, self._themes[theme_id]["name"]) for theme_id in theme_order if theme_id in self._themes]
    
    def get_current_theme(self):
        """Get the current theme ID"""
        return self._current_theme
    
    def apply_theme(self, app, theme_id=None):
        """
        Apply the specified theme to the application
        
        Args:
            app: QApplication instance
            theme_id: Theme ID to apply (if None, applies current theme)
        """
        if theme_id and theme_id in self._themes:
            self._current_theme = theme_id
            
        # Save theme preference
        self._save_theme_preference()
        
        # Get theme data
        theme = self._themes[self._current_theme]
        
        # Create and apply palette
        palette = self._create_palette_from_theme(theme["palette"])
        app.setPalette(palette)
        
        # Apply stylesheet
        app.setStyleSheet(theme["stylesheet"]())
        
        # Emit theme changed signal
        self.theme_changed.emit(self._current_theme)

    def _create_palette_from_theme(self, theme_colors):
        """Create a QPalette from theme colors"""
        palette = QPalette()
        
        # Extract colors
        background = theme_colors["background"]
        background_alt = theme_colors["background_alt"]
        foreground = theme_colors["foreground"]
        primary = theme_colors["primary"]
        
        # Set palette colors
        palette.setColor(QPalette.Window, background)
        palette.setColor(QPalette.WindowText, foreground)
        palette.setColor(QPalette.Base, background_alt)
        palette.setColor(QPalette.AlternateBase, background)
        palette.setColor(QPalette.Text, foreground)
        palette.setColor(QPalette.BrightText, Qt.white)
        palette.setColor(QPalette.Button, background_alt)
        palette.setColor(QPalette.ButtonText, foreground)
        palette.setColor(QPalette.Highlight, primary)
        palette.setColor(QPalette.HighlightedText, Qt.white)
        
        # Disabled state colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        
        # Tooltip
        palette.setColor(QPalette.ToolTipBase, primary)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        
        return palette
    
    def _save_theme_preference(self):
        """Save the current theme preference to settings"""
        settings = QSettings("FragranceOrg", "Fragrance Collection Organizer")
        settings.setValue("theme/current", self._current_theme)
    
    def _load_theme_preference(self):
        """Load theme preference from settings"""
        settings = QSettings("FragranceOrg", "Fragrance Collection Organizer")
        saved_theme = settings.value("theme/current", "dark")
        
        if saved_theme in self._themes:
            self._current_theme = saved_theme

    # Theme stylesheet getters
    def _get_dark_stylesheet(self):
        """Get the dark theme stylesheet"""
        return """
        /* Global */
        * {
            border-radius: 4px;
        }
        
        /* QWidget */
        QWidget {
            background-color: #16161a;
            color: #e6e6eb;
        }
        
        /* QToolBar */
        QToolBar {
            border: none;
            padding: 4px;
            spacing: 4px;
            background-color: #1e1e23;
        }
        
        /* QPushButton */
        QPushButton {
            background-color: #1e1e23;
            color: #e6e6eb;
            border: 1px solid #2e2e35;
            padding: 8px 16px;
            border-radius: 6px;
        }
        
        QPushButton:hover {
            background-color: #2a2a32;
            border: 1px solid #9c88ff;
        }
        
        QPushButton:pressed {
            background-color: #9c88ff;
            color: white;
        }
        
        /* QLineEdit */
        QLineEdit {
            background-color: #1e1e23;
            border: 1px solid #2e2e35;
            padding: 8px;
            border-radius: 6px;
        }
        
        QLineEdit:focus {
            border: 1px solid #9c88ff;
        }
        
        /* QComboBox */
        QComboBox {
            background-color: #1e1e23;
            border: 1px solid #2e2e35;
            padding: 8px;
            border-radius: 6px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #1e1e23;
            border: 1px solid #2e2e35;
            border-radius: 6px;
            selection-background-color: #9c88ff;
        }
        
        /* QTabWidget */
        QTabWidget::pane {
            border: 1px solid #2e2e35;
            background-color: #16161a;
            top: -1px;
        }
        
        QTabBar::tab {
            background-color: #1e1e23;
            border: 1px solid #2e2e35;
            padding: 8px 16px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        
        QTabBar::tab:selected {
            background-color: #16161a;
            border-bottom-color: #16161a;
        }
        
        QTabBar::tab:hover {
            background-color: #2a2a32;
        }
        
        /* QScrollBar */
        QScrollBar:vertical {
            border: none;
            background-color: #1e1e23;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #2e2e35;
            border-radius: 5px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #3e3e45;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background-color: #1e1e23;
            height: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #2e2e35;
            border-radius: 5px;
            min-width: 30px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #3e3e45;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* QTableView */
        QTableView {
            gridline-color: #2e2e35;
            background-color: #1e1e23;
            selection-background-color: #9c88ff;
            selection-color: white;
            alternate-background-color: #16161a;
        }
        
        QTableView::item {
            padding: 8px;
        }
        
        QHeaderView::section {
            background-color: #2a2a32;
            padding: 6px;
            border: none;
            font-weight: bold;
        }
        
        /* QSlider */
        QSlider::groove:horizontal {
            height: 8px;
            background-color: #1e1e23;
            border-radius: 4px;
            border: 1px solid #9c88ff;
        }
        
        QSlider::handle:horizontal {
            background-color: #9c88ff;
            border: none;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
        
        QSlider::sub-page:horizontal {
            background-color: #9c88ff;
            border-radius: 4px;
        }
        
        /* QGroupBox */
        QGroupBox {
            font-weight: bold;
            border: 1px solid #2e2e35;
            border-radius: 6px;
            margin-top: 16px;
            padding-top: 16px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* QCheckBox */
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 1px solid #2e2e35;
        }
        
        QCheckBox::indicator:checked {
            background-color: #9c88ff;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: #1e1e23;
        }
        
        /* QRadioButton */
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 1px solid #2e2e35;
        }
        
        QRadioButton::indicator:checked {
            background-color: #9c88ff;
        }
        
        QRadioButton::indicator:unchecked {
            background-color: #1e1e23;
        }
        
        /* QProgressBar */
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #1e1e23;
            text-align: center;
            color: white;
        }
        
        QProgressBar::chunk {
            background-color: #9c88ff;
            border-radius: 4px;
        }
        
        /* QSplitter */
        QSplitter::handle {
            background-color: #2e2e35;
        }
        
        /* QStatusBar */
        QStatusBar {
            background-color: #1e1e23;
            color: #e6e6eb;
        }
        """

    def _get_light_stylesheet(self):
        """Get the light theme stylesheet"""
        return """
        /* Global */
        * {
            border-radius: 4px;
        }
        
        /* QWidget */
        QWidget {
            background-color: #f5f5f7;
            color: #232328;
        }
        
        /* QToolBar */
        QToolBar {
            border: none;
            padding: 4px;
            spacing: 4px;
            background-color: #e6e6eb;
        }
        
        /* QPushButton */
        QPushButton {
            background-color: #e6e6eb;
            color: #232328;
            border: 1px solid #c5c5c8;
            padding: 8px 16px;
            border-radius: 6px;
        }
        
        QPushButton:hover {
            background-color: #d8d8df;
            border: 1px solid #826ee5;
        }
        
        QPushButton:pressed {
            background-color: #826ee5;
            color: white;
        }
        
        /* QLineEdit */
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #c5c5c8;
            padding: 8px;
            border-radius: 6px;
        }
        
        QLineEdit:focus {
            border: 1px solid #826ee5;
        }
        
        /* QComboBox */
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #c5c5c8;
            padding: 8px;
            border-radius: 6px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            border: 1px solid #c5c5c8;
            border-radius: 6px;
            selection-background-color: #826ee5;
            selection-color: white;
        }
        
        /* QTabWidget */
        QTabWidget::pane {
            border: 1px solid #c5c5c8;
            background-color: #f5f5f7;
            top: -1px;
        }
        
        QTabBar::tab {
            background-color: #e6e6eb;
            border: 1px solid #c5c5c8;
            padding: 8px 16px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        
        QTabBar::tab:selected {
            background-color: #f5f5f7;
            border-bottom-color: #f5f5f7;
        }
        
        QTabBar::tab:hover {
            background-color: #d8d8df;
        }
        
        /* QScrollBar */
        QScrollBar:vertical {
            border: none;
            background-color: #e6e6eb;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #a5a5a8;
            border-radius: 5px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #757578;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background-color: #e6e6eb;
            height: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #c5c5c8;
            border-radius: 5px;
            min-width: 30px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #a5a5a8;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* QTableView */
        QTableView {
            gridline-color: #c5c5c8;
            background-color: #ffffff;
            selection-background-color: #826ee5;
            selection-color: white;
            alternate-background-color: #f5f5f7;
        }
        
        QTableView::item {
            padding: 8px;
        }
        
        QHeaderView::section {
            background-color: #d8d8df;
            padding: 6px;
            border: none;
            font-weight: bold;
        }
        
        /* QSlider */
        QSlider::groove:horizontal {
            height: 8px;
            background-color: #e6e6eb;
            border-radius: 4px;
            border: 1px solid #826ee5;
        }
        
        QSlider::handle:horizontal {
            background-color: #826ee5;
            border: none;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
        
        QSlider::sub-page:horizontal {
            background-color: #826ee5;
            border-radius: 4px;
        }
        
        /* QGroupBox */
        QGroupBox {
            font-weight: bold;
            border: 1px solid #c5c5c8;
            border-radius: 6px;
            margin-top: 16px;
            padding-top: 16px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* QCheckBox */
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 1px solid #c5c5c8;
        }
        
        QCheckBox::indicator:checked {
            background-color: #826ee5;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: #ffffff;
        }
        
        /* QRadioButton */
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 1px solid #c5c5c8;
        }
        
        QRadioButton::indicator:checked {
            background-color: #826ee5;
        }
        
        QRadioButton::indicator:unchecked {
            background-color: #ffffff;
        }
        
        /* QProgressBar */
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #e6e6eb;
            text-align: center;
            color: #232328;
        }
        
        QProgressBar::chunk {
            background-color: #826ee5;
            border-radius: 4px;
        }
        
        /* QSplitter */
        QSplitter::handle {
            background-color: #c5c5c8;
        }
        
        /* QStatusBar */
        QStatusBar {
            background-color: #e6e6eb;
            color: #232328;
        }
        """

    def _get_nature_stylesheet(self):
        """Get the Emerald Veil theme stylesheet"""
        return """
        /* Global */
        * {
            border-radius: 4px;
        }
        
        /* QWidget */
        QWidget {
            background-color: #232a25;
            color: #dce6dc;
        }
        
        /* QToolBar */
        QToolBar {
            border: none;
            padding: 4px;
            spacing: 4px;
            background-color: #2d3730;
        }
        
        /* QPushButton */
        QPushButton {
            background-color: #2d3730;
            color: #dce6dc;
            border: 1px solid #3d4d40;
            padding: 8px 16px;
            border-radius: 6px;
        }
        
        QPushButton:hover {
            background-color: #3d4d40;
            border: 1px solid #78b478;
        }
        
        QPushButton:pressed {
            background-color: #78b478;
            color: white;
        }
        
        /* QLineEdit */
        QLineEdit {
            background-color: #2d3730;
            border: 1px solid #3d4d40;
            padding: 8px;
            border-radius: 6px;
        }
        
        QLineEdit:focus {
            border: 1px solid #78b478;
        }
        
        /* QComboBox */
        QComboBox {
            background-color: #2d3730;
            border: 1px solid #3d4d40;
            padding: 8px;
            border-radius: 6px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #2d3730;
            border: 1px solid #3d4d40;
            border-radius: 6px;
            selection-background-color: #78b478;
            selection-color: white;
        }
        
        /* QTabWidget */
        QTabWidget::pane {
            border: 1px solid #3d4d40;
            background-color: #232a25;
            top: -1px;
        }
        
        QTabBar::tab {
            background-color: #2d3730;
            border: 1px solid #3d4d40;
            padding: 8px 16px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        
        QTabBar::tab:selected {
            background-color: #232a25;
            border-bottom-color: #232a25;
        }
        
        QTabBar::tab:hover {
            background-color: #3d4d40;
        }
        
        /* QScrollBar */
        QScrollBar:vertical {
            border: none;
            background-color: #2d3730;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #3d4d40;
            border-radius: 5px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #4d6350;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background-color: #2d3730;
            height: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #3d4d40;
            border-radius: 5px;
            min-width: 30px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #4d6350;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* QTableView */
        QTableView {
            gridline-color: #3d4d40;
            background-color: #2d3730;
            selection-background-color: #78b478;
            selection-color: white;
            alternate-background-color: #232a25;
        }
        
        QTableView::item {
            padding: 8px;
        }
        
        QHeaderView::section {
            background-color: #3d4d40;
            padding: 6px;
            border: none;
            font-weight: bold;
        }
        
        /* QSlider */
        QSlider::groove:horizontal {
            height: 8px;
            background-color: #2d3730;
            border-radius: 4px;
            border: 1px solid #78b478;
        }
        
        QSlider::handle:horizontal {
            background-color: #78b478;
            border: none;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
        
        QSlider::sub-page:horizontal {
            background-color: #78b478;
            border-radius: 4px;
        }
        
        /* QGroupBox */
        QGroupBox {
            font-weight: bold;
            border: 1px solid #3d4d40;
            border-radius: 6px;
            margin-top: 16px;
            padding-top: 16px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* QCheckBox */
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 1px solid #3d4d40;
        }
        
        QCheckBox::indicator:checked {
            background-color: #78b478;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: #2d3730;
        }
        
        /* QRadioButton */
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 1px solid #3d4d40;
        }
        
        QRadioButton::indicator:checked {
            background-color: #78b478;
        }
        
        QRadioButton::indicator:unchecked {
            background-color: #2d3730;
        }
        
        /* QProgressBar */
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #2d3730;
            text-align: center;
            color: white;
        }
        
        QProgressBar::chunk {
            background-color: #78b478;
            border-radius: 4px;
        }
        
        /* QSplitter */
        QSplitter::handle {
            background-color: #3d4d40;
        }
        
        /* QStatusBar */
        QStatusBar {
            background-color: #2d3730;
            color: #dce6dc;
        }
        """

    def _get_midnight_stylesheet(self):
        """Get the midnight blue theme stylesheet"""
        return """
        /* Global */
        * {
            border-radius: 4px;
        }
        
        /* QWidget */
        QWidget {
            background-color: #0f1623;
            color: #dce1eb;
        }
        
        /* QToolBar */
        QToolBar {
            border: none;
            padding: 4px;
            spacing: 4px;
            background-color: #192332;
        }
        
        /* QPushButton */
        QPushButton {
            background-color: #192332;
            color: #dce1eb;
            border: 1px solid #293245;
            padding: 8px 16px;
            border-radius: 6px;
        }
        
        QPushButton:hover {
            background-color: #293245;
            border: 1px solid #5091e6;
        }
        
        QPushButton:pressed {
            background-color: #5091e6;
            color: white;
        }
        
        /* QLineEdit */
        QLineEdit {
            background-color: #192332;
            border: 1px solid #293245;
            padding: 8px;
            border-radius: 6px;
        }
        
        QLineEdit:focus {
            border: 1px solid #5091e6;
        }
        
        /* QComboBox */
        QComboBox {
            background-color: #192332;
            border: 1px solid #293245;
            padding: 8px;
            border-radius: 6px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #192332;
            border: 1px solid #293245;
            border-radius: 6px;
            selection-background-color: #5091e6;
            selection-color: white;
        }
        
        /* QTabWidget */
        QTabWidget::pane {
            border: 1px solid #293245;
            background-color: #0f1623;
            top: -1px;
        }
        
        QTabBar::tab {
            background-color: #192332;
            border: 1px solid #293245;
            padding: 8px 16px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        
        QTabBar::tab:selected {
            background-color: #0f1623;
            border-bottom-color: #0f1623;
        }
        
        QTabBar::tab:hover {
            background-color: #293245;
        }
        
        /* QScrollBar */
        QScrollBar:vertical {
            border: none;
            background-color: #192332;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #293245;
            border-radius: 5px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #394255;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background-color: #192332;
            height: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #293245;
            border-radius: 5px;
            min-width: 30px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #394255;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* QTableView */
        QTableView {
            gridline-color: #293245;
            background-color: #192332;
            selection-background-color: #5091e6;
            selection-color: white;
            alternate-background-color: #0f1623;
        }
        
        QTableView::item {
            padding: 8px;
        }
        
        QHeaderView::section {
            background-color: #293245;
            padding: 6px;
            border: none;
            font-weight: bold;
        }
        
        /* QSlider */
        QSlider::groove:horizontal {
            height: 8px;
            background-color: #192332;
            border-radius: 4px;
            border: 1px solid #5091e6;
        }
        
        QSlider::handle:horizontal {
            background-color: #5091e6;
            border: none;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
        
        QSlider::sub-page:horizontal {
            background-color: #5091e6;
            border-radius: 4px;
        }
        
        /* QGroupBox */
        QGroupBox {
            font-weight: bold;
            border: 1px solid #293245;
            border-radius: 6px;
            margin-top: 16px;
            padding-top: 16px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* QCheckBox */
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 1px solid #293245;
        }
        
        QCheckBox::indicator:checked {
            background-color: #5091e6;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: #192332;
        }
        
        /* QRadioButton */
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 1px solid #293245;
        }
        
        QRadioButton::indicator:checked {
            background-color: #5091e6;
        }
        
        QRadioButton::indicator:unchecked {
            background-color: #192332;
        }
        
        /* QProgressBar */
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #192332;
            text-align: center;
            color: white;
        }
        
        QProgressBar::chunk {
            background-color: #5091e6;
            border-radius: 4px;
        }
        
        /* QSplitter */
        QSplitter::handle {
            background-color: #293245;
        }
        
        /* QStatusBar */
        QStatusBar {
            background-color: #192332;
            color: #dce1eb;
        }
        """

    def _get_monochrome_stylesheet(self):
        """Get the monochrome theme stylesheet"""
        return """
        /* Global */
        * {
            border-radius: 4px;
        }
        
        /* QWidget */
        QWidget {
            background-color: #121212;
            color: #dcdcdc;
        }
        
        /* QToolBar */
        QToolBar {
            border: none;
            padding: 4px;
            spacing: 4px;
            background-color: #1e1e1e;
        }
        
        /* QPushButton */
        QPushButton {
            background-color: #1e1e1e;
            color: #dcdcdc;
            border: 1px solid #2d2d2d;
            padding: 8px 16px;
            border-radius: 6px;
        }
        
        QPushButton:hover {
            background-color: #2d2d2d;
            border: 1px solid #b4b4b4;
        }
        
        QPushButton:pressed {
            background-color: #b4b4b4;
            color: #121212;
        }
        
        /* QLineEdit */
        QLineEdit {
            background-color: #1e1e1e;
            border: 1px solid #2d2d2d;
            padding: 8px;
            border-radius: 6px;
        }
        
        QLineEdit:focus {
            border: 1px solid #b4b4b4;
        }
        
        /* QComboBox */
        QComboBox {
            background-color: #1e1e1e;
            border: 1px solid #2d2d2d;
            padding: 8px;
            border-radius: 6px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #1e1e1e;
            border: 1px solid #2d2d2d;
            border-radius: 6px;
            selection-background-color: #b4b4b4;
            selection-color: #121212;
        }
        
        /* QTabWidget */
        QTabWidget::pane {
            border: 1px solid #2d2d2d;
            background-color: #121212;
            top: -1px;
        }
        
        QTabBar::tab {
            background-color: #1e1e1e;
            border: 1px solid #2d2d2d;
            padding: 8px 16px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        
        QTabBar::tab:selected {
            background-color: #121212;
            border-bottom-color: #121212;
        }
        
        QTabBar::tab:hover {
            background-color: #2d2d2d;
        }
        
        /* QScrollBar */
        QScrollBar:vertical {
            border: none;
            background-color: #1e1e1e;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #2d2d2d;
            border-radius: 5px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #3c3c3c;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background-color: #1e1e1e;
            height: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #2d2d2d;
            border-radius: 5px;
            min-width: 30px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #3c3c3c;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* QTableView */
        QTableView {
            gridline-color: #2d2d2d;
            background-color: #1e1e1e;
            selection-background-color: #b4b4b4;
            selection-color: #121212;
            alternate-background-color: #121212;
        }
        
        QTableView::item {
            padding: 8px;
        }
        
        QHeaderView::section {
            background-color: #2d2d2d;
            padding: 6px;
            border: none;
            font-weight: bold;
        }
        
        /* QSlider */
        QSlider::groove:horizontal {
            height: 8px;
            background-color: #1e1e1e;
            border-radius: 4px;
            border: 1px solid #b4b4b4;
        }
        
        QSlider::handle:horizontal {
            background-color: #b4b4b4;
            border: none;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
        
        QSlider::sub-page:horizontal {
            background-color: #b4b4b4;
            border-radius: 4px;
        }
        
        /* QGroupBox */
        QGroupBox {
            font-weight: bold;
            border: 1px solid #2d2d2d;
            border-radius: 6px;
            margin-top: 16px;
            padding-top: 16px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* QCheckBox */
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 1px solid #2d2d2d;
        }
        
        QCheckBox::indicator:checked {
            background-color: #b4b4b4;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: #1e1e1e;
        }
        
        /* QRadioButton */
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 1px solid #2d2d2d;
        }
        
        QRadioButton::indicator:checked {
            background-color: #b4b4b4;
        }
        
        QRadioButton::indicator:unchecked {
            background-color: #1e1e1e;
        }
        
        /* QProgressBar */
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #1e1e1e;
            text-align: center;
            color: white;
        }
        
        QProgressBar::chunk {
            background-color: #b4b4b4;
            border-radius: 4px;
        }
        
        /* QSplitter */
        QSplitter::handle {
            background-color: #2d2d2d;
        }
        
        /* QStatusBar */
        QStatusBar {
            background-color: #1e1e1e;
            color: #dcdcdc;
        }
        """
    
    def _get_reverse_monochrome_stylesheet(self):
        """Get the reverse monochrome theme stylesheet"""
        return """
        /* Global */
        * {
            border-radius: 4px;
        }
        
        /* QWidget */
        QWidget {
            background-color: #dcdcdc;
            color: #121212;
        }
        
        /* QToolBar */
        QToolBar {
            border: none;
            padding: 4px;
            spacing: 4px;
            background-color: #c8c8c8;
        }
        
        /* QPushButton */
        QPushButton {
            background-color: #c8c8c8;
            color: #121212;
            border: 1px solid #a0a0a0;
            padding: 8px 16px;
            border-radius: 6px;
        }
        
        QPushButton:hover {
            background-color: #a0a0a0;
            border: 1px solid #464646;
        }
        
        QPushButton:pressed {
            background-color: #464646;
            color: #dcdcdc;
        }
        
        /* QLineEdit */
        QLineEdit {
            background-color: #c8c8c8;
            border: 1px solid #a0a0a0;
            padding: 8px;
            border-radius: 6px;
        }
        
        QLineEdit:focus {
            border: 1px solid #464646;
        }
        
        /* QComboBox */
        QComboBox {
            background-color: #c8c8c8;
            border: 1px solid #a0a0a0;
            padding: 8px;
            border-radius: 6px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #c8c8c8;
            border: 1px solid #a0a0a0;
            border-radius: 6px;
            selection-background-color: #464646;
            selection-color: #dcdcdc;
        }
        
        /* QTabWidget */
        QTabWidget::pane {
            border: 1px solid #a0a0a0;
            background-color: #dcdcdc;
            top: -1px;
        }
        
        QTabBar::tab {
            background-color: #c8c8c8;
            border: 1px solid #a0a0a0;
            padding: 8px 16px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        
        QTabBar::tab:selected {
            background-color: #dcdcdc;
            border-bottom-color: #dcdcdc;
        }
        
        QTabBar::tab:hover {
            background-color: #a0a0a0;
        }
        
        /* QScrollBar */
        QScrollBar:vertical {
            border: none;
            background-color: #c8c8c8;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #a0a0a0;
            border-radius: 5px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #808080;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background-color: #c8c8c8;
            height: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #a0a0a0;
            border-radius: 5px;
            min-width: 30px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #808080;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* QTableView */
        QTableView {
            gridline-color: #a0a0a0;
            background-color: #c8c8c8;
            selection-background-color: #464646;
            selection-color: #dcdcdc;
            alternate-background-color: #dcdcdc;
        }
        
        QTableView::item {
            padding: 8px;
        }
        
        QHeaderView::section {
            background-color: #a0a0a0;
            padding: 6px;
            border: none;
            font-weight: bold;
        }
        
        /* QSlider */
        QSlider::groove:horizontal {
            height: 8px;
            background-color: #c8c8c8;
            border-radius: 4px;
            border: 1px solid #464646;
        }
        
        QSlider::handle:horizontal {
            background-color: #464646;
            border: none;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
        
        QSlider::sub-page:horizontal {
            background-color: #464646;
            border-radius: 4px;
        }
        
        /* QGroupBox */
        QGroupBox {
            font-weight: bold;
            border: 1px solid #a0a0a0;
            border-radius: 6px;
            margin-top: 16px;
            padding-top: 16px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* QCheckBox */
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 1px solid #a0a0a0;
        }
        
        QCheckBox::indicator:checked {
            background-color: #464646;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: #c8c8c8;
        }
        
        /* QRadioButton */
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 1px solid #a0a0a0;
        }
        
        QRadioButton::indicator:checked {
            background-color: #464646;
        }
        
        QRadioButton::indicator:unchecked {
            background-color: #c8c8c8;
        }
        
        /* QProgressBar */
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #c8c8c8;
            text-align: center;
            color: #121212;
        }
        
        QProgressBar::chunk {
            background-color: #464646;
            border-radius: 4px;
        }
        
        /* QSplitter */
        QSplitter::handle {
            background-color: #a0a0a0;
        }
        
        /* QStatusBar */
        QStatusBar {
            background-color: #c8c8c8;
            color: #121212;
        }
        """

    def _get_violet_stylesheet(self):
        """Get the violet theme stylesheet"""
        return """
        /* Global */
        * {
            border-radius: 4px;
        }
        
        /* QWidget */
        QWidget {
            background-color: #231932;
            color: #e6dcf0;
        }
        
        /* QToolBar */
        QToolBar {
            border: none;
            padding: 4px;
            spacing: 4px;
            background-color: #2d2341;
        }
        
        /* QPushButton */
        QPushButton {
            background-color: #2d2341;
            color: #e6dcf0;
            border: 1px solid #3d3355;
            padding: 8px 16px;
            border-radius: 6px;
        }
        
        QPushButton:hover {
            background-color: #3d3355;
            border: 1px solid #b478dc;
        }
        
        QPushButton:pressed {
            background-color: #b478dc;
            color: white;
        }
        
        /* QLineEdit */
        QLineEdit {
            background-color: #2d2341;
            border: 1px solid #3d3355;
            padding: 8px;
            border-radius: 6px;
        }
        
        QLineEdit:focus {
            border: 1px solid #b478dc;
        }
        
        /* QComboBox */
        QComboBox {
            background-color: #2d2341;
            border: 1px solid #3d3355;
            padding: 8px;
            border-radius: 6px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #2d2341;
            border: 1px solid #3d3355;
            border-radius: 6px;
            selection-background-color: #b478dc;
            selection-color: white;
        }
        
        /* QTabWidget */
        QTabWidget::pane {
            border: 1px solid #3d3355;
            background-color: #231932;
            top: -1px;
        }
        
        QTabBar::tab {
            background-color: #2d2341;
            border: 1px solid #3d3355;
            padding: 8px 16px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        
        QTabBar::tab:selected {
            background-color: #231932;
            border-bottom-color: #231932;
        }
        
        QTabBar::tab:hover {
            background-color: #3d3355;
        }
        
        /* QScrollBar */
        QScrollBar:vertical {
            border: none;
            background-color: #2d2341;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #3d3355;
            border-radius: 5px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #4d4365;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background-color: #2d2341;
            height: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #3d3355;
            border-radius: 5px;
            min-width: 30px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #4d4365;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* QTableView */
        QTableView {
            gridline-color: #3d3355;
            background-color: #2d2341;
            selection-background-color: #b478dc;
            selection-color: white;
            alternate-background-color: #231932;
        }
        
        QTableView::item {
            padding: 8px;
        }
        
        QHeaderView::section {
            background-color: #3d3355;
            padding: 6px;
            border: none;
            font-weight: bold;
        }
        
        /* QSlider */
        QSlider::groove:horizontal {
            height: 8px;
            background-color: #2d2341;
            border-radius: 4px;
            border: 1px solid #b478dc;
        }
        
        QSlider::handle:horizontal {
            background-color: #b478dc;
            border: none;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
        
        QSlider::sub-page:horizontal {
            background-color: #b478dc;
            border-radius: 4px;
        }
        
        /* QGroupBox */
        QGroupBox {
            font-weight: bold;
            border: 1px solid #3d3355;
            border-radius: 6px;
            margin-top: 16px;
            padding-top: 16px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* QCheckBox */
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 1px solid #3d3355;
        }
        
        QCheckBox::indicator:checked {
            background-color: #b478dc;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: #2d2341;
        }
        
        /* QRadioButton */
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 1px solid #3d3355;
        }
        
        QRadioButton::indicator:checked {
            background-color: #b478dc;
        }
        
        QRadioButton::indicator:unchecked {
            background-color: #2d2341;
        }
        
        /* QProgressBar */
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #2d2341;
            text-align: center;
            color: white;
        }
        
        QProgressBar::chunk {
            background-color: #b478dc;
            border-radius: 4px;
        }
        
        /* QSplitter */
        QSplitter::handle {
            background-color: #3d3355;
        }
        
        /* QStatusBar */
        QStatusBar {
            background-color: #2d2341;
            color: #e6dcf0;
        }
        """

# Create a singleton instance
theme_manager = ThemeManager() 