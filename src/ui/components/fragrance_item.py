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
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QGridLayout, QSizePolicy, QApplication,
    QScrollArea, QToolButton
)
from PySide6.QtCore import Qt, Signal, Property, QSize, Slot
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

from src.ui.widgets import SeasonalityPanel, PerformanceBar
from src.utils import theme_manager


class FragranceItem(QFrame):
    """
    Widget that displays a single fragrance in the collection view
    """
    editClicked = Signal(int)
    deleteClicked = Signal(int)
    favoriteToggled = Signal(int, bool)
    
    def __init__(self, fragrance, parent=None):
        super().__init__(parent)
        
        self._fragrance = fragrance
        self._expanded = False
        
        # Set up styling
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setAutoFillBackground(True)
        self.setObjectName("fragranceCard")
        
        self._setup_ui()
        
        # Connect to fragrance data change
        self._fragrance.dataChanged.connect(self._update_display)
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._update_styling)
        
        # Apply initial styling
        self._update_styling()
        
        # Create shadow effect for card-like appearance
        self.setContentsMargins(4, 4, 4, 4)
    
    def _setup_ui(self):
        """Set up the user interface"""
        self._main_layout = QVBoxLayout(self)
        
        # Top section with title and favorite star
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(4, 4, 4, 0)
        top_layout.setSpacing(2)  # Reduce spacing to minimize empty space
        
        # Container for the house and name labels with proper centering
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        title_layout.setAlignment(Qt.AlignCenter)
        
        # House label container to ensure consistent width
        house_container = QWidget()
        house_container.setFixedWidth(350)  # Increase width to accommodate longer house names
        house_layout = QVBoxLayout(house_container)
        house_layout.setContentsMargins(0, 0, 0, 0)
        house_layout.setSpacing(0)
        
        # House label (centered)
        self._house_label = QLabel(self._fragrance.house())
        self._house_label.setObjectName("houseLabel")
        self._house_label.setAlignment(Qt.AlignCenter)
        self._house_label.setWordWrap(True)  # Allow text wrapping for very long house names
        house_layout.addWidget(self._house_label)
        
        # Add house container to title layout
        title_layout.addWidget(house_container, 0, Qt.AlignCenter)
        
        # Name label (centered, bold, larger)
        self._name_label = QLabel(self._fragrance.name())
        self._name_label.setObjectName("nameLabel")
        self._name_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self._name_label)
        
        # Add title container to top layout
        top_layout.addWidget(title_container)
        
        # Size & concentration summary
        self._summary_label = QLabel(f"{self._fragrance.size_oz()} oz | {self._fragrance.concentration()}")
        self._summary_label.setObjectName("detailsLabel")
        self._summary_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self._summary_label)
        
        self._main_layout.addWidget(top_section)
        
        # Create favorite button separately and position it absolutely
        self._favorite_button = QToolButton(self)  # Parent directly to the main widget
        self._favorite_button.setObjectName("favoriteButton")
        self._favorite_button.setCheckable(True)
        self._favorite_button.setChecked(self._fragrance.is_favorite())
        self._favorite_button.clicked.connect(self._toggle_favorite)
        self._favorite_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._favorite_button.setText("★" if self._fragrance.is_favorite() else "☆")  # Set initial text
        self._favorite_button.raise_()  # Ensure it's above other widgets
        
        # Set a fixed size for the button to ensure proper display
        self._favorite_button.setFixedSize(30, 30)
        
        # Position star initially (will be updated in resize event)
        self._update_favorite_button_position()
        
        # Basic info summary (for condensed view)
        self._summary_layout = QVBoxLayout()
        
        # Expand button
        self._expand_button = QPushButton("Expand")
        self._expand_button.setObjectName("expandButton")
        self._expand_button.clicked.connect(self._toggle_expanded)
        self._summary_layout.addWidget(self._expand_button)
        
        self._main_layout.addLayout(self._summary_layout)
        
        # Container for detailed content (hidden in condensed view)
        self._detailed_container = QWidget()
        self._detailed_layout = QVBoxLayout(self._detailed_container)
        self._detailed_container.setVisible(False)
        
        # Middle section: Details (Size, Concentration, etc.)
        details_layout = QGridLayout()
        details_layout.setColumnStretch(1, 1)  # Make second column stretch
        
        # Size
        size_label = QLabel("Size:")
        size_label.setObjectName("sectionLabel")
        self._size_value = QLabel(f"{self._fragrance.size_oz()} oz ({self._fragrance.size_ml()} ml)")
        self._size_value.setObjectName("detailsLabel")
        details_layout.addWidget(size_label, 0, 0)
        details_layout.addWidget(self._size_value, 0, 1)
        
        # Concentration
        concentration_label = QLabel("Concentration:")
        concentration_label.setObjectName("sectionLabel")
        self._concentration_value = QLabel(self._fragrance.concentration())
        self._concentration_value.setObjectName("detailsLabel")
        details_layout.addWidget(concentration_label, 1, 0)
        details_layout.addWidget(self._concentration_value, 1, 1)
        
        # Notes sections - create a scrollable container
        notes_section = QVBoxLayout()
        
        notes_label = QLabel("Fragrance Notes")
        notes_label.setObjectName("sectionLabel")
        notes_section.addWidget(notes_label)
        
        # Create a container for the notes content
        notes_container = QWidget()
        notes_container_layout = QVBoxLayout(notes_container)
        notes_container_layout.setContentsMargins(0, 0, 0, 0)
        notes_container_layout.setSpacing(2)  # Tighter spacing for notes
        
        # Top notes
        if self._fragrance.top_notes():
            top_notes_label = QLabel(f"<b>Top:</b> {self._fragrance.top_notes()}")
            top_notes_label.setObjectName("detailsLabel")
            top_notes_label.setWordWrap(True)
            notes_container_layout.addWidget(top_notes_label)
        
        # Middle notes
        if self._fragrance.middle_notes():
            middle_notes_label = QLabel(f"<b>Middle:</b> {self._fragrance.middle_notes()}")
            middle_notes_label.setObjectName("detailsLabel")
            middle_notes_label.setWordWrap(True)
            notes_container_layout.addWidget(middle_notes_label)
        
        # Base notes
        if self._fragrance.base_notes():
            base_notes_label = QLabel(f"<b>Base:</b> {self._fragrance.base_notes()}")
            base_notes_label.setObjectName("detailsLabel")
            base_notes_label.setWordWrap(True)
            notes_container_layout.addWidget(base_notes_label)
        
        # Create scroll area for notes if they're extensive
        scroll_area = QScrollArea()
        scroll_area.setWidget(notes_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Calculate a better height for the notes section
        # Each note line is approximately 20px high, plus spacing (5px) between lines
        # Add margins (10px top & bottom) and section header (20px)
        # For 3 lines (top, middle, base): 3 * 20px + 2 * 5px + 20px + 10px * 2 = 90px minimum
        # Set a reasonable maximum that allows scrolling for very extensive notes
        notes_count = sum(1 for x in [self._fragrance.top_notes(), 
                                     self._fragrance.middle_notes(), 
                                     self._fragrance.base_notes()] if x)
        min_height = max(90, notes_count * 25)  # 25px per note line including spacing
        max_height = 200  # Maximum height for extensive notes
        
        # Set a dynamic height, minimum 90px for 3 notes, maximum 200px
        scroll_area.setMinimumHeight(min_height)
        scroll_area.setMaximumHeight(max_height)
        
        notes_section.addWidget(scroll_area)
        
        # Seasonality section
        seasonality_section = QVBoxLayout()
        
        seasonality_label = QLabel("Seasonality")
        seasonality_label.setObjectName("sectionLabel")
        seasonality_section.addWidget(seasonality_label)
        
        # Seasonality panel
        self._seasonality_panel = SeasonalityPanel()
        self._seasonality_panel.set_ratings(
            self._fragrance.winter_rating(),
            self._fragrance.spring_rating(),
            self._fragrance.summer_rating(),
            self._fragrance.fall_rating()
        )
        seasonality_section.addWidget(self._seasonality_panel)
        
        # Performance section
        performance_section = QVBoxLayout()
        
        performance_label = QLabel("Performance")
        performance_label.setObjectName("sectionLabel")
        performance_section.addWidget(performance_label)
        
        # Performance bars
        self._longevity_bar = PerformanceBar("Longevity", self._fragrance.longevity())
        self._sillage_bar = PerformanceBar("Sillage", self._fragrance.sillage())
        
        performance_section.addWidget(self._longevity_bar)
        performance_section.addWidget(self._sillage_bar)
        
        # Clone information (if applicable)
        clone_layout = None
        if self._fragrance.is_clone():
            clone_layout = QVBoxLayout()
            
            clone_label = QLabel("Clone Information")
            clone_label.setObjectName("sectionLabel")
            clone_layout.addWidget(clone_label)
            
            original_label = QLabel(f"<b>Clone of:</b> {self._fragrance.original_fragrance()}")
            original_label.setObjectName("detailsLabel")
            original_label.setWordWrap(True)
            clone_layout.addWidget(original_label)
        
        # Action buttons (Copy, Edit, Delete)
        action_layout = QHBoxLayout()
        
        # Copy button
        copy_button = QPushButton("Copy Details")
        copy_button.setObjectName("copyButton")
        copy_button.clicked.connect(self._copy_to_clipboard)
        
        # Collapse button
        collapse_button = QPushButton("Collapse")
        collapse_button.setObjectName("collapseButton")
        collapse_button.clicked.connect(self._toggle_expanded)
        
        # Edit button
        edit_button = QPushButton("Edit")
        edit_button.setObjectName("editButton")
        edit_button.clicked.connect(lambda: self.editClicked.emit(self._fragrance.id()))
        
        # Delete button
        delete_button = QPushButton("Delete")
        delete_button.setObjectName("deleteButton")
        delete_button.clicked.connect(lambda: self.deleteClicked.emit(self._fragrance.id()))
        
        action_layout.addWidget(copy_button)
        action_layout.addWidget(collapse_button)
        action_layout.addWidget(edit_button)
        action_layout.addWidget(delete_button)
        
        # Add all sections to detailed layout
        self._detailed_layout.addLayout(details_layout)
        self._detailed_layout.addLayout(notes_section)
        self._detailed_layout.addLayout(seasonality_section)
        self._detailed_layout.addLayout(performance_section)
        
        if clone_layout:
            self._detailed_layout.addLayout(clone_layout)
        
        self._detailed_layout.addLayout(action_layout)
        
        # Add all to main layout
        self._main_layout.addLayout(self._summary_layout)
        self._main_layout.addWidget(self._detailed_container)
    
    def _toggle_expanded(self):
        """Toggle between condensed and expanded views"""
        self._expanded = not self._expanded
        self._detailed_container.setVisible(self._expanded)
        self._expand_button.setVisible(not self._expanded)
        
        # Update size
        self.updateGeometry()
    
    def expandItem(self):
        """Expand this fragrance item to show details"""
        if not self._expanded:
            self._expanded = True
            self._detailed_container.setVisible(True)
            self._expand_button.setVisible(False)
            self.updateGeometry()
    
    def collapseItem(self):
        """Collapse this fragrance item to hide details"""
        if self._expanded:
            self._expanded = False
            self._detailed_container.setVisible(False)
            self._expand_button.setVisible(True)
            self.updateGeometry()
    
    def _copy_to_clipboard(self):
        """Copy fragrance details to clipboard in plain text format"""
        fragrance_text = f"{self._fragrance.house()} {self._fragrance.name()}\n"
        fragrance_text += f"Size: {self._fragrance.size_oz()} oz ({self._fragrance.size_ml()} ml)\n"
        fragrance_text += f"Concentration: {self._fragrance.concentration()}\n\n"
        
        # Notes
        if self._fragrance.top_notes():
            fragrance_text += f"TOP NOTES: {self._fragrance.top_notes()}\n"
        if self._fragrance.middle_notes():
            fragrance_text += f"MIDDLE NOTES: {self._fragrance.middle_notes()}\n"
        if self._fragrance.base_notes():
            fragrance_text += f"BASE NOTES: {self._fragrance.base_notes()}\n"
        
        fragrance_text += f"\nSeasonality:\n"
        fragrance_text += f"Winter: {self._fragrance.winter_rating()}/5\n"
        fragrance_text += f"Spring: {self._fragrance.spring_rating()}/5\n"
        fragrance_text += f"Summer: {self._fragrance.summer_rating()}/5\n"
        fragrance_text += f"Fall: {self._fragrance.fall_rating()}/5\n\n"
        
        fragrance_text += f"Performance:\n"
        fragrance_text += f"Longevity: {self._fragrance.longevity()}/5\n"
        fragrance_text += f"Sillage: {self._fragrance.sillage()}/5\n"
        
        if self._fragrance.is_clone():
            fragrance_text += f"\nCLONE OF: {self._fragrance.original_fragrance()}\n"
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(fragrance_text)
    
    def _toggle_favorite(self):
        """Toggle the favorite status of this fragrance"""
        is_favorite = self._favorite_button.isChecked()
        self._fragrance.set_is_favorite(is_favorite)
        self.favoriteToggled.emit(self._fragrance.id(), is_favorite)
        
        # Update visuals directly here - don't call _update_favorite_button as it triggers layout warnings
        star_text = "★" if is_favorite else "☆"
        self._favorite_button.setText(star_text)
        
        # Update the color directly based on theme
        current_theme = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme]
        text_color = theme_data["palette"]["foreground"].name()
        primary_color = theme_data["palette"]["primary"].name()
        
        # Determine star color based on theme
        if current_theme == "nature":  # "Emerald Veil" theme
            star_color = "#78b478" if is_favorite else text_color
        else:
            star_color = primary_color if is_favorite else text_color
            
        self._favorite_button.setStyleSheet(f"""
            QToolButton#favoriteButton {{
                color: {star_color};
                background-color: transparent;
                border: none;
                font-size: 24px;
                font-weight: bold;
                padding: 4px;
            }}
            
            QToolButton#favoriteButton:hover {{
                color: {primary_color};
            }}
        """)
    
    def _update_favorite_button(self):
        """Update the favorite button appearance based on current state"""
        is_favorite = self._fragrance.is_favorite()
        self._favorite_button.setChecked(is_favorite)
        
        # Set the text directly here instead of in _update_styling
        star_text = "★" if is_favorite else "☆"
        self._favorite_button.setText(star_text)
        
        # Update the color directly based on theme
        current_theme = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme]
        text_color = theme_data["palette"]["foreground"].name()
        primary_color = theme_data["palette"]["primary"].name()
        
        # Determine star color based on theme
        if current_theme == "nature":  # "Emerald Veil" theme
            star_color = "#78b478" if is_favorite else text_color
        else:
            star_color = primary_color if is_favorite else text_color
            
        self._favorite_button.setStyleSheet(f"""
            QToolButton#favoriteButton {{
                color: {star_color};
                background-color: transparent;
                border: none;
                font-size: 24px;
                font-weight: bold;
                padding: 4px;
            }}
            
            QToolButton#favoriteButton:hover {{
                color: {primary_color};
            }}
        """)
    
    def _update_display(self):
        """Update display with current fragrance data"""
        # Update basic info
        house_name = self._fragrance.house()
        self._house_label.setText(house_name)
        self._name_label.setText(self._fragrance.name())
        self._summary_label.setText(f"{self._fragrance.size_oz()} oz | {self._fragrance.concentration()}")
        self._size_value.setText(f"{self._fragrance.size_oz()} oz ({self._fragrance.size_ml()} ml)")
        self._concentration_value.setText(self._fragrance.concentration())
        
        # Ensure house label is properly sized and visible
        self._house_label.adjustSize()
        
        # Update performance metrics
        self._longevity_bar.set_rating(self._fragrance.longevity())
        self._sillage_bar.set_rating(self._fragrance.sillage())
        
        # Update seasonality panel
        self._seasonality_panel.set_ratings(
            self._fragrance.winter_rating(),
            self._fragrance.spring_rating(),
            self._fragrance.summer_rating(),
            self._fragrance.fall_rating()
        )
        
        # Update favorite button
        self._update_favorite_button()
    
    @Slot()
    def _update_styling(self):
        """Update styling based on the current theme"""
        current_theme = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme]
        
        # Get colors from theme
        bg_color = theme_data["palette"]["background_alt"].name()
        bg2_color = theme_data["palette"]["background"].name()
        text_color = theme_data["palette"]["foreground"].name()
        primary_color = theme_data["palette"]["primary"].name()
        secondary_color = theme_data["palette"]["secondary"].name()
        
        # Standard styling
        name_font_size = "20px"
        house_font_size = "18px"
        details_font_size = "13px"
        section_font_size = "13px"
        border_style = f"border: 1px solid {primary_color};"
        card_padding = "8px"
        button_padding = "5px 10px"
        
        # Update favorite button (moved to _update_favorite_button method)
        self._update_favorite_button()
        
        # Apply theme-based styling for the card
        card_style = f"""
            #fragranceCard {{
                background-color: {bg_color};
                border-radius: 8px;
                padding: {card_padding};
                margin: 4px;
                {border_style}
            }}
            
            #nameLabel {{
                font-size: {name_font_size};
                font-weight: bold;
                color: {text_color};
                text-align: center;
                padding: 3px 9px;
                margin: 2px 12px;
            }}
            
            #houseLabel {{
                font-size: {house_font_size};
                font-weight: normal;
                color: {text_color};
                text-align: center;
                background-color: {bg2_color};
                border-radius: 4px;
                padding: 5px 10px;
                margin: 2px auto;
                min-height: 20px;
                {border_style}
            }}
            
            #detailsLabel {{
                font-size: {details_font_size};
                color: {text_color};
                text-align: center;
            }}
            
            #sectionLabel {{
                font-size: {section_font_size};
                font-weight: bold;
                color: {text_color};
                margin-top: 4px;
                border-bottom: 1px solid {primary_color};
                padding-bottom: 2px;
            }}
            
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            
            QScrollBar:vertical {{
                background-color: {bg2_color};
                width: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {primary_color};
                border-radius: 4px;
                min-height: 20px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QPushButton {{
                padding: {button_padding};
            }}
            
            QPushButton#expandButton, QPushButton#collapseButton {{
                background-color: {bg2_color};
                color: {text_color};
                border: 1px solid {primary_color};
                font-weight: bold;
            }}
            
            QPushButton#expandButton:hover, QPushButton#collapseButton:hover {{
                background-color: {primary_color};
                color: {bg2_color};
                border: 1px solid {text_color};
            }}
            
            QPushButton#copyButton {{
                background-color: {primary_color};
                color: white;
                border: 1px solid {primary_color};
                font-weight: bold;
            }}
            
            QPushButton#copyButton:hover {{
                background-color: {bg2_color};
                color: {text_color};
                border: 1px solid {primary_color};
            }}
        """
        
        self.setStyleSheet(card_style)
    
    def get_fragrance_id(self):
        """Get the ID of the fragrance this item represents"""
        return self._fragrance.id()
    
    def sizeHint(self):
        """Suggest a reasonable size for the widget"""
        if self._expanded:
            return QSize(400, 500)
        else:
            return QSize(400, 120)
    
    def resizeEvent(self, event):
        """Override of resize event to ensure star button is properly positioned"""
        super().resizeEvent(event)
        self._update_favorite_button_position()
    
    def showEvent(self, event):
        """Override of show event to ensure star button is properly positioned"""
        super().showEvent(event)
        self._update_favorite_button_position()
    
    def _update_favorite_button_position(self):
        """Update the position of the favorite button"""
        if hasattr(self, '_favorite_button'):
            margin = 32
            star_size = self._favorite_button.sizeHint()
            x = self.width() - star_size.width() - (margin / 2)
            y = margin
            self._favorite_button.move(x, y)
            self._favorite_button.raise_()  # Ensure button stays on top 