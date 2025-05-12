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

from PySide6.QtWidgets import QWidget, QLabel, QProgressBar, QHBoxLayout
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPainter, QPen, QFont, QColor

from src.utils import theme_manager


class OutlinedProgressBar(QProgressBar):
    """
    Custom QProgressBar with outlined text for better readability
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._text_color = Qt.white
        self._outline_color = Qt.black
        
    def setTextColor(self, color):
        self._text_color = color
        
    def setOutlineColor(self, color):
        self._outline_color = color
    
    def paintEvent(self, event):
        # First, let the progress bar draw itself normally
        super().paintEvent(event)
        
        # Then, overlay our custom text with an outline
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create the font
        font = QFont(self.font())
        font.setBold(True)
        painter.setFont(font)
        
        # Get the text to display
        text = self.text()
        
        # Draw the text with an outline
        rect = self.rect()
        
        # Draw the outline (stroke)
        painter.setPen(QPen(self._outline_color, 1.5))
        painter.drawText(rect.adjusted(-1, -1, -1, -1), Qt.AlignCenter, text)
        painter.drawText(rect.adjusted(1, -1, 1, -1), Qt.AlignCenter, text)
        painter.drawText(rect.adjusted(-1, 1, -1, 1), Qt.AlignCenter, text)
        painter.drawText(rect.adjusted(1, 1, 1, 1), Qt.AlignCenter, text)
        
        # Draw the main text (fill)
        painter.setPen(QPen(self._text_color, 1))
        painter.drawText(rect, Qt.AlignCenter, text)


class PerformanceBar(QWidget):
    """
    Custom widget that displays a visual bar for performance metrics (longevity, sillage)
    with values from 1-5 in increments of 1
    """
    def __init__(self, metric_name="Longevity", rating=3, parent=None):
        super().__init__(parent)
        
        self._metric_name = metric_name
        self._rating = rating
        self._setup_ui()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._update_styling)
        
        # Apply initial styling
        self._update_styling()
    
    def _setup_ui(self):
        """Set up the user interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Metric label
        self._metric_label = QLabel(f"{self._metric_name}:")
        self._metric_label.setFixedWidth(70)
        
        # Progress bar for visual representation
        self._progress_bar = OutlinedProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat(f"{self._rating}/5")
        self._progress_bar.setValue(int((self._rating - 1) / 4 * 100))
        
        layout.addWidget(self._metric_label)
        layout.addWidget(self._progress_bar)
    
    @Slot()
    def _update_styling(self):
        """Update styling based on the current theme"""
        current_theme = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme]
        
        # Get colors from theme
        bg_color = theme_data["palette"]["background"].name()
        bg_alt_color = theme_data["palette"]["background_alt"].name()
        primary_color = theme_data["palette"]["primary"].name()
        text_color = theme_data["palette"]["foreground"].name()
        
        # Basic styling with border
        border_style = f"border: 1px solid {primary_color};"
        height = "16px"
        
        # Set colors for the progress bar text and outline
        self._progress_bar.setTextColor(QColor(bg_color))
        self._progress_bar.setOutlineColor(QColor(primary_color))
        
        # Apply styling
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                {border_style}
                border-radius: 4px;
                background-color: {bg_alt_color};
                text-align: center;
                height: {height};
                font-weight: bold;
            }}
            
            QProgressBar::chunk {{
                background-color: {primary_color};
                border-radius: 4px;
            }}
        """)
        
        # Simple bold styling for metric label without background
        self._metric_label.setStyleSheet(f"""
            color: {text_color};
            font-weight: bold;
        """)
    
    def set_rating(self, rating):
        """Update the rating value"""
        self._rating = max(1, min(5, rating))
        self._progress_bar.setValue(int((self._rating - 1) / 4 * 100))
        self._progress_bar.setFormat(f"{self._rating}/5")
    
    def get_rating(self):
        """Get the current rating"""
        return self._rating 