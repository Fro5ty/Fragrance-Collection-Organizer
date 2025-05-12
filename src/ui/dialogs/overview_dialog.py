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

from PySide6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QPushButton, QScrollArea, QWidget, QTextEdit, QApplication
)
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QFont

from src.models import collection_manager
from src.db import db_manager
from src.utils import theme_manager


class OverviewDialog(QDialog):
    """
    Dialog that displays an overview of the fragrance collection statistics
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Collection Overview")
        self.setMinimumSize(600, 500)
        
        self._setup_ui()
        self._load_statistics()
    
    def _setup_ui(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container for all content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header_label = QLabel("Fragrance Collection Overview")
        header_label.setAlignment(Qt.AlignCenter)
        font = header_label.font()
        font.setPointSize(16)
        font.setBold(True)
        header_label.setFont(font)
        content_layout.addWidget(header_label)
        
        # Basic Stats Group
        basic_stats_group = QGroupBox("Collection Statistics")
        basic_stats_layout = QVBoxLayout(basic_stats_group)
        basic_stats_layout.setSpacing(10)
        basic_stats_layout.setContentsMargins(15, 15, 15, 15)
        
        self._total_fragrances_label = QLabel("Total Fragrances: Loading...")
        self._total_houses_label = QLabel("Total Houses: Loading...")
        
        basic_stats_layout.addWidget(self._total_fragrances_label)
        basic_stats_layout.addWidget(self._total_houses_label)
        
        content_layout.addWidget(basic_stats_group)
        
        # Popular Houses Group
        houses_group = QGroupBox("Most Common Houses")
        houses_layout = QVBoxLayout(houses_group)
        houses_layout.setSpacing(10)
        houses_layout.setContentsMargins(15, 15, 15, 15)
        
        self._houses_list = QLabel("Loading house data...")
        self._houses_list.setTextFormat(Qt.RichText)
        houses_layout.addWidget(self._houses_list)
        
        content_layout.addWidget(houses_group)
        
        # Popular Notes Group
        notes_group = QGroupBox("Top 10 Most Common Notes")
        notes_layout = QVBoxLayout(notes_group)
        notes_layout.setSpacing(10)
        notes_layout.setContentsMargins(15, 15, 15, 15)
        
        self._notes_list = QLabel("Loading notes data...")
        self._notes_list.setWordWrap(True)
        self._notes_list.setTextFormat(Qt.RichText)
        notes_layout.addWidget(self._notes_list)
        
        content_layout.addWidget(notes_group)
        
        # Favorite Notes Group
        favorite_notes_group = QGroupBox("Top 10 Notes in Favorite Fragrances")
        favorite_notes_layout = QVBoxLayout(favorite_notes_group)
        favorite_notes_layout.setSpacing(10)
        favorite_notes_layout.setContentsMargins(15, 15, 15, 15)
        
        self._favorite_notes_list = QLabel("Loading favorite notes data...")
        self._favorite_notes_list.setWordWrap(True)
        self._favorite_notes_list.setTextFormat(Qt.RichText)
        favorite_notes_layout.addWidget(self._favorite_notes_list)
        
        content_layout.addWidget(favorite_notes_group)
        
        # Seasonal Preference Group
        seasons_group = QGroupBox("Seasonal Preferences")
        seasons_layout = QVBoxLayout(seasons_group)
        seasons_layout.setSpacing(10)
        seasons_layout.setContentsMargins(15, 15, 15, 15)
        
        self._seasons_list = QLabel("Loading seasonal data...")
        self._seasons_list.setTextFormat(Qt.RichText)
        seasons_layout.addWidget(self._seasons_list)
        
        content_layout.addWidget(seasons_group)
        
        # Text representation for copying
        copy_group = QGroupBox("Copy to Clipboard")
        copy_layout = QVBoxLayout(copy_group)
        copy_layout.setSpacing(10)
        copy_layout.setContentsMargins(15, 15, 15, 15)
        
        self._text_representation = QTextEdit()
        self._text_representation.setReadOnly(True)
        self._text_representation.setPlaceholderText("Statistics will appear here for copying")
        self._text_representation.setMinimumHeight(120)
        
        # Copy button
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.setObjectName("copyButton")
        copy_button.clicked.connect(self._copy_to_clipboard)
        
        # Status label for copy action feedback
        self._copy_status = QLabel("")
        self._copy_status.setAlignment(Qt.AlignRight)
        
        copy_layout.addWidget(self._text_representation)
        copy_status_layout = QHBoxLayout()
        copy_status_layout.addWidget(self._copy_status, 1)
        copy_status_layout.addWidget(copy_button)
        copy_layout.addLayout(copy_status_layout)
        
        content_layout.addWidget(copy_group)
        
        # Set the scroll area widget
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        refresh_button = QPushButton("Refresh Data")
        refresh_button.clicked.connect(self._load_statistics)
        
        button_layout.addWidget(refresh_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._update_styling)
        
        # Initial styling
        self._update_styling()
    
    def _load_statistics(self):
        """Load and display collection statistics"""
        # Basic stats
        stats = collection_manager.get_collection_stats()
        total_fragrances = stats.get('total_fragrances', 0)
        total_houses = stats.get('house_count', 0)
        
        self._total_fragrances_label.setText(f"<b>Total Fragrances:</b> {total_fragrances}")
        self._total_houses_label.setText(f"<b>Total Houses:</b> {total_houses}")
        
        # Get top houses (use database manager to get more specific stats)
        top_houses = db_manager.get_top_houses(limit=3)
        houses_text = ""
        
        if top_houses:
            for i, (house, count) in enumerate(top_houses, 1):
                houses_text += f"<b>{i}.</b> {house} <i>({count} fragrances)</i><br>"
        else:
            houses_text = "No house data available"
        
        self._houses_list.setText(houses_text)
        
        # Get top notes
        top_notes = db_manager.get_top_notes(limit=10)
        notes_text = ""
        
        if top_notes:
            for i, (note, count) in enumerate(top_notes, 1):
                notes_text += f"<b>{i}.</b> {note} <i>({count} occurrences)</i><br>"
        else:
            notes_text = "No notes data available"
        
        self._notes_list.setText(notes_text)
        
        # Get top notes from favorites
        top_favorite_notes = db_manager.get_top_notes_from_favorites(limit=10)
        favorite_notes_text = ""
        
        if top_favorite_notes:
            for i, (note, count) in enumerate(top_favorite_notes, 1):
                favorite_notes_text += f"<b>{i}.</b> {note} <i>({count} occurrences)</i><br>"
        else:
            favorite_notes_text = "No favorited fragrances found or no notes data available"
        
        self._favorite_notes_list.setText(favorite_notes_text)
        
        # Get seasonal averages and preference counts
        seasonal_stats = db_manager.get_seasonal_averages()
        seasonal_preferences = db_manager.get_seasonal_preferences()
        
        if seasonal_stats and seasonal_preferences:
            # Sort seasons by rating (highest to lowest)
            sorted_seasons = sorted(
                [('Winter', seasonal_stats.get('winter_avg', 0), seasonal_preferences.get('winter_count', 0)),
                 ('Spring', seasonal_stats.get('spring_avg', 0), seasonal_preferences.get('spring_count', 0)),
                 ('Summer', seasonal_stats.get('summer_avg', 0), seasonal_preferences.get('summer_count', 0)),
                 ('Fall', seasonal_stats.get('fall_avg', 0), seasonal_preferences.get('fall_count', 0))],
                key=lambda x: x[1], reverse=True
            )
            
            seasons_text = "<b>Seasons ranked by average rating:</b><br>"
            for i, (season, avg, count) in enumerate(sorted_seasons, 1):
                # Add color tags based on season
                if season == "Winter":
                    color = "#0072B2"  # Blue
                elif season == "Spring":
                    color = "#009E73"  # Green
                elif season == "Summer":
                    color = "#E65849"  # Red
                elif season == "Fall":
                    color = "#D55E00"  # Orange
                else:
                    color = "inherit"
                    
                # Add count of fragrances that score highest in this season
                count_text = f"({count} fragrance{'s' if count != 1 else ''})"
                seasons_text += f"<b>{i}.</b> <span style='color:{color};'>{season}</span>: <b>{avg:.2f}/5.0</b> <i>{count_text}</i><br>"
            
            # Add a note about possible ties
            seasons_text += "<br><small><i>Note: Fragrances may be counted in multiple seasons if they score equally high in more than one season.</i></small>"
        else:
            seasons_text = "No seasonal data available"
        
        self._seasons_list.setText(seasons_text)
        
        # Create text representation for copying
        text_rep = f"FRAGRANCE COLLECTION OVERVIEW\n"
        text_rep += f"============================\n\n"
        text_rep += f"Collection Statistics:\n"
        text_rep += f"- Total Fragrances: {total_fragrances}\n"
        text_rep += f"- Total Houses: {total_houses}\n\n"
        
        text_rep += f"Most Common Houses:\n"
        if top_houses:
            for i, (house, count) in enumerate(top_houses, 1):
                text_rep += f"{i}. {house} ({count} fragrances)\n"
        else:
            text_rep += "No house data available\n"
        text_rep += "\n"
        
        text_rep += f"Top 10 Most Common Notes:\n"
        if top_notes:
            for i, (note, count) in enumerate(top_notes, 1):
                text_rep += f"{i}. {note} ({count} occurrences)\n"
        else:
            text_rep += "No notes data available\n"
        text_rep += "\n"
        
        text_rep += f"Top 10 Notes in Favorite Fragrances:\n"
        if top_favorite_notes:
            for i, (note, count) in enumerate(top_favorite_notes, 1):
                text_rep += f"{i}. {note} ({count} occurrences)\n"
        else:
            text_rep += "No favorited fragrances found or no notes data available\n"
        text_rep += "\n"
        
        text_rep += f"Seasonal Preferences:\n"
        if seasonal_stats and seasonal_preferences:
            text_rep += "Seasons ranked by average rating:\n"
            for i, (season, avg, count) in enumerate(sorted_seasons, 1):
                text_rep += f"{i}. {season}: {avg:.2f}/5.0 ({count} fragrance{'s' if count != 1 else ''})\n"
            text_rep += "\nNote: Fragrances may be counted in multiple seasons if they score equally high in more than one season.\n"
        else:
            text_rep += "No seasonal data available\n"
        
        self._text_representation.setText(text_rep)
    
    def _copy_to_clipboard(self):
        """Copy the overview text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self._text_representation.toPlainText())
        
        # Get current theme colors for status message
        current_theme = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme]
        primary_color = theme_data["palette"]["primary"].name()
        
        # Show success message with theme-appropriate color
        self._copy_status.setText(f"<i style='color:{primary_color};'>Copied to clipboard!</i> ")
        
        # Clear the status message after 3 seconds
        QTimer.singleShot(3000, lambda: self._copy_status.setText(""))
    
    @Slot()
    def _update_styling(self):
        """Update styling based on the current theme"""
        current_theme = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme]
        
        # Get colors from theme
        bg_color = theme_data["palette"]["background"].name()
        bg_alt_color = theme_data["palette"]["background_alt"].name()
        text_color = theme_data["palette"]["foreground"].name()
        primary_color = theme_data["palette"]["primary"].name()
        secondary_color = theme_data["palette"]["secondary"].name()
        
        # Apply theme-based styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                color: {text_color};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {primary_color};
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: {primary_color};
            }}
            
            QLabel {{
                color: {text_color};
            }}
            
            QTextEdit {{
                background-color: {bg_alt_color};
                color: {text_color};
                border: 1px solid {primary_color};
                border-radius: 3px;
                padding: 4px;
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QPushButton {{
                background-color: {primary_color};
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }}
            
            QPushButton:hover {{
                background-color: {secondary_color};
            }}
        """) 