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

from PySide6.QtWidgets import QWidget, QSlider, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, Signal, Property, Slot

from src.utils import theme_manager


class RatingSlider(QWidget):
    """
    Custom slider widget for seasonal ratings with 0.25 step increments
    """
    valueChanged = Signal(float)
    
    def __init__(self, label="Rating", min_value=1.0, max_value=5.0, step=0.25, parent=None):
        super().__init__(parent)
        
        self._min_value = min_value
        self._max_value = max_value
        self._step = step
        self._label_text = label
        self._value = 3.0  # Default value
        
        # Calculate the number of steps
        self._steps = int((max_value - min_value) / step) + 1
        
        self._setup_ui()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._update_styling)
        
        # Apply initial styling
        self._update_styling()
    
    def _setup_ui(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create label above the slider
        self._label = QLabel(f"{self._label_text}: {self._value:.2f}")
        self._label.setAlignment(Qt.AlignCenter)
        
        # Create slider
        slider_layout = QHBoxLayout()
        
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(self._steps - 1)
        self._slider.setValue(self._value_to_slider(self._value))
        self._slider.setTickPosition(QSlider.TicksBelow)
        self._slider.setTickInterval(4)  # Tick every 1.0 (4 steps of 0.25)
        
        # Min and max labels
        self._min_label = QLabel(f"{self._min_value:.1f}")
        self._max_label = QLabel(f"{self._max_value:.1f}")
        
        slider_layout.addWidget(self._min_label)
        slider_layout.addWidget(self._slider, 1)
        slider_layout.addWidget(self._max_label)
        
        main_layout.addWidget(self._label)
        main_layout.addLayout(slider_layout)
        
        # Connect signal
        self._slider.valueChanged.connect(self._on_slider_changed)
    
    @Slot()
    def _update_styling(self):
        """Update styling based on the current theme"""
        current_theme = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme]
        
        # Get colors from theme
        bg_color = theme_data["palette"]["background"].name()
        bg_alt_color = theme_data["palette"]["background_alt"].name()
        fg_color = theme_data["palette"]["foreground"].name()
        primary_color = theme_data["palette"]["primary"].name()
        
        # Default styling
        groove_height = "8px"
        handle_width = "16px"
        handle_margin = "-4px 0"
        border = f"border: 1px solid {primary_color};"
        label_style = ""
        
        # Apply styling to slider
        self._slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: {groove_height};
                background-color: {bg_alt_color};
                border-radius: 4px;
                {border}
            }}
            
            QSlider::handle:horizontal {{
                background-color: {primary_color};
                border: none;
                width: {handle_width};
                margin: {handle_margin};
                border-radius: {int(float(handle_width.replace('px', '')) / 2)}px;
                {label_style}
            }}
            
            QSlider::sub-page:horizontal {{
                background-color: {primary_color};
                border-radius: 4px;
            }}
        """)
    
    def _value_to_slider(self, value):
        """Convert a rating value to slider position"""
        # Constrain value to range
        value = max(self._min_value, min(self._max_value, value))
        
        # Convert to slider position
        position = int((value - self._min_value) / self._step)
        return position
    
    def _slider_to_value(self, position):
        """Convert slider position to rating value"""
        value = position * self._step + self._min_value
        return value
    
    def _on_slider_changed(self, position):
        """Handle slider position changes"""
        value = self._slider_to_value(position)
        
        if value != self._value:
            self._value = value
            self._label.setText(f"{self._label_text}: {self._value:.2f}")
            self.valueChanged.emit(self._value)
    
    def value(self):
        """Get the current value"""
        return self._value
    
    def setValue(self, value):
        """Set the current value"""
        if value != self._value:
            # Ensure value is within range and snapped to step increments
            value = round((value - self._min_value) / self._step) * self._step + self._min_value
            value = max(self._min_value, min(self._max_value, value))
            
            self._value = value
            self._slider.setValue(self._value_to_slider(value))
            self._label.setText(f"{self._label_text}: {self._value:.2f}") 