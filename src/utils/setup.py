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

from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.utils.theme_manager import theme_manager


def setup_application(app):
    """
    Set up application theme and settings
    
    Args:
        app: QApplication instance
    """
    # Set application name and organization
    app.setApplicationName("Fragrance Collection Organizer")
    app.setOrganizationName("FragranceOrg")
    
    # Set global font
    font = QFont("Inter", 10)
    app.setFont(font)
    
    # Apply theme
    theme_manager.apply_theme(app)
    
    return app


def apply_elegant_theme(app):
    """
    Apply an elegant theme to the application
    
    Args:
        app: QApplication instance
    """
    # Create custom palette
    palette = QPalette()
    
    # Define colors
    background = QColor(22, 22, 25)
    background_alt = QColor(30, 30, 35)
    foreground = QColor(230, 230, 235)
    primary = QColor(156, 136, 255)
    secondary = QColor(219, 166, 130)
    
    # Dark subtle background
    palette.setColor(QPalette.Window, background)
    palette.setColor(QPalette.WindowText, foreground)
    
    # Text colors
    palette.setColor(QPalette.Text, foreground)
    palette.setColor(QPalette.BrightText, Qt.white)
    
    # Button styling
    palette.setColor(QPalette.Button, background_alt)
    palette.setColor(QPalette.ButtonText, foreground)
    
    # Highlight colors
    palette.setColor(QPalette.Highlight, primary)
    palette.setColor(QPalette.HighlightedText, Qt.white)
    
    # Disabled state colors
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    
    # Base colors
    palette.setColor(QPalette.Base, background_alt)
    palette.setColor(QPalette.AlternateBase, background)
    
    # Tooltip
    palette.setColor(QPalette.ToolTipBase, primary)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    
    # Apply palette
    app.setPalette(palette)
    
    # Set stylesheet for more control over UI elements
    stylesheet = """
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
    
    QComboBox::down-arrow {
        width: 12px;
        height: 12px;
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
        image: url(:/icons/checkmark.png);
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
        image: url(:/icons/radiomark.png);
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
    """
    
    app.setStyleSheet(stylesheet) 