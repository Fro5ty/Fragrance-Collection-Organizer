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

from PySide6.QtWidgets import QWidget, QLabel, QProgressBar, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QColor

from src.utils import theme_manager


class SeasonRatingBar(QWidget):
    """
    Custom widget that displays a visual bar for seasonal ratings
    """
    def __init__(self, season="Winter", rating=3.0, parent=None):
        super().__init__(parent)
        
        self._season = season
        self._rating = rating
        self._setup_ui()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._update_styling)
    
    def _setup_ui(self):
        """Set up the user interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Season label
        self._season_label = QLabel(f"{self._season}:")
        self._season_label.setFixedWidth(60)
        
        # Progress bar for visual representation
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat(f"{self._rating:.2f}")
        self._progress_bar.setValue(int((self._rating - 1) / 4 * 100))
        
        layout.addWidget(self._season_label)
        layout.addWidget(self._progress_bar)
        
        # Set color based on season
        self._set_season_color()
    
    def _set_season_color(self):
        """Set color of the progress bar based on season"""
        # Define default colors for each season
        standard_season_colors = {
            "Winter": "#0072B2",
            "Spring": "#009E73",
            "Summer": "#E65849",
            "Fall": "#D55E00"
        }
        
        # Get current theme
        current_theme = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme]
        
        # Check if the theme has special season colors
        if "seasons" in theme_data:
            # Use theme-specific season colors
            self._season_color = theme_data["seasons"].get(self._season, theme_data["palette"]["primary"].name())
        else:
            # Use standard season colors
            self._season_color = standard_season_colors.get(self._season, "#9c88ff")  # Default purple if not found
        
        # Apply styling (background will be updated by theme changes)
        self._update_styling()
    
    @Slot()
    def _update_styling(self):
        """Update styling based on current theme, while preserving seasonal colors"""
        current_theme = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme]
        
        # Get colors from theme for background
        bg_color = theme_data["palette"]["background"].name()
        bg_alt_color = theme_data["palette"]["background_alt"].name()
        text_color = theme_data["palette"]["foreground"].name()
        
        # Enhance styling for different themes
        border_style = f"border: 1px solid {self._season_color};"  # Default border for all themes
        height = "16px"
        bar_text_color = text_color
        font_weight = "bold"  # Make all season labels bold
        
        # Apply styling with seasonal color for the bar
        chunk_style = f"""
        QProgressBar {{
            {border_style}
            border-radius: 4px;
            background-color: {bg_alt_color};
            text-align: center;
            color: {bar_text_color};
            height: {height};
            font-weight: {font_weight};
        }}
        
        QProgressBar::chunk {{
            background-color: {self._season_color};
            border-radius: 4px;
        }}
        """
        
        self._progress_bar.setStyleSheet(chunk_style)
        
        # Simple bold styling for season labels without background
        self._season_label.setStyleSheet(f"""
            color: {text_color};
            font-weight: bold;
        """)
    
    def set_rating(self, rating):
        """Update the rating value"""
        self._rating = max(1.0, min(5.0, rating))
        self._progress_bar.setValue(int((self._rating - 1) / 4 * 100))
        self._progress_bar.setFormat(f"{self._rating:.2f}")
    
    def set_season(self, season):
        """Update the season"""
        self._season = season
        self._season_label.setText(f"{self._season}:")
        self._set_season_color()
    
    def get_rating(self):
        """Get the current rating"""
        return self._rating


class SeasonalityPanel(QWidget):
    """
    Panel containing rating bars for all four seasons
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Create rating bars for each season
        self._winter_bar = SeasonRatingBar("Winter", 3.0)
        self._spring_bar = SeasonRatingBar("Spring", 3.0)
        self._summer_bar = SeasonRatingBar("Summer", 3.0)
        self._fall_bar = SeasonRatingBar("Fall", 3.0)
        
        layout.addWidget(self._winter_bar)
        layout.addWidget(self._spring_bar)
        layout.addWidget(self._summer_bar)
        layout.addWidget(self._fall_bar)
    
    def set_ratings(self, winter, spring, summer, fall):
        """Update all season ratings at once"""
        self._winter_bar.set_rating(winter)
        self._spring_bar.set_rating(spring)
        self._summer_bar.set_rating(summer)
        self._fall_bar.set_rating(fall)
    
    def sizeHint(self):
        """Suggest a reasonable size for the widget"""
        return QSize(200, 120) 