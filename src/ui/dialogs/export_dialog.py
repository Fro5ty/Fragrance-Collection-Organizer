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
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QCheckBox, QDialogButtonBox, QLabel, QFileDialog,
    QPushButton, QGridLayout
)
from PySide6.QtCore import Qt, Slot, Signal


class ExportDialog(QDialog):
    """
    Dialog for selecting which fields to include in CSV export
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Export Options")
        self.setMinimumWidth(400)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        
        info_label = QLabel(
            "Select which fields to include in the exported CSV file:"
        )
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Fields group
        fields_group = QGroupBox("Fields")
        fields_layout = QVBoxLayout(fields_group)
        
        # Checkboxes for each field
        self._field_checkboxes = {}
        
        # Basic info fields
        self._field_checkboxes["house"] = QCheckBox("House")
        self._field_checkboxes["house"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["house"])
        
        self._field_checkboxes["name"] = QCheckBox("Name")
        self._field_checkboxes["name"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["name"])
        
        self._field_checkboxes["size_oz"] = QCheckBox("Size (oz)")
        self._field_checkboxes["size_oz"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["size_oz"])
        
        self._field_checkboxes["size_ml"] = QCheckBox("Size (ml)")
        self._field_checkboxes["size_ml"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["size_ml"])
        
        self._field_checkboxes["concentration"] = QCheckBox("Concentration")
        self._field_checkboxes["concentration"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["concentration"])
        
        # Notes fields
        self._field_checkboxes["top_notes"] = QCheckBox("Top Notes")
        self._field_checkboxes["top_notes"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["top_notes"])
        
        self._field_checkboxes["middle_notes"] = QCheckBox("Middle Notes")
        self._field_checkboxes["middle_notes"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["middle_notes"])
        
        self._field_checkboxes["base_notes"] = QCheckBox("Base Notes")
        self._field_checkboxes["base_notes"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["base_notes"])
        
        # Seasonal ratings
        self._field_checkboxes["winter_rating"] = QCheckBox("Winter Rating")
        self._field_checkboxes["winter_rating"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["winter_rating"])
        
        self._field_checkboxes["spring_rating"] = QCheckBox("Spring Rating")
        self._field_checkboxes["spring_rating"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["spring_rating"])
        
        self._field_checkboxes["summer_rating"] = QCheckBox("Summer Rating")
        self._field_checkboxes["summer_rating"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["summer_rating"])
        
        self._field_checkboxes["fall_rating"] = QCheckBox("Fall Rating")
        self._field_checkboxes["fall_rating"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["fall_rating"])
        
        # Performance metrics
        self._field_checkboxes["longevity"] = QCheckBox("Longevity")
        self._field_checkboxes["longevity"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["longevity"])
        
        self._field_checkboxes["sillage"] = QCheckBox("Sillage")
        self._field_checkboxes["sillage"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["sillage"])
        
        # Clone information
        self._field_checkboxes["is_clone"] = QCheckBox("Is Clone")
        self._field_checkboxes["is_clone"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["is_clone"])
        
        self._field_checkboxes["original_fragrance"] = QCheckBox("Original Fragrance")
        self._field_checkboxes["original_fragrance"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["original_fragrance"])
        
        # Favorite field
        self._field_checkboxes["is_favorite"] = QCheckBox("Is Favorite")
        self._field_checkboxes["is_favorite"].setChecked(True)
        fields_layout.addWidget(self._field_checkboxes["is_favorite"])
        
        main_layout.addWidget(fields_group)
        
        # Buttons
        select_buttons_layout = QHBoxLayout()
        
        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self._select_all)
        select_buttons_layout.addWidget(select_all_button)
        
        select_none_button = QPushButton("Select None")
        select_none_button.clicked.connect(self._select_none)
        select_buttons_layout.addWidget(select_none_button)
        
        main_layout.addLayout(select_buttons_layout)
        
        # Action buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def _select_all(self):
        """Select all export fields"""
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setChecked(True)
    
    def _select_none(self):
        """Deselect all export fields"""
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setChecked(False)
    
    def get_selected_fields(self):
        """Get a dictionary of selected export fields"""
        return {
            'house': self._field_checkboxes["house"].isChecked(),
            'name': self._field_checkboxes["name"].isChecked(),
            'size_oz': self._field_checkboxes["size_oz"].isChecked(),
            'size_ml': self._field_checkboxes["size_ml"].isChecked(),
            'concentration': self._field_checkboxes["concentration"].isChecked(),
            'top_notes': self._field_checkboxes["top_notes"].isChecked(),
            'middle_notes': self._field_checkboxes["middle_notes"].isChecked(),
            'base_notes': self._field_checkboxes["base_notes"].isChecked(),
            'winter_rating': self._field_checkboxes["winter_rating"].isChecked(),
            'spring_rating': self._field_checkboxes["spring_rating"].isChecked(),
            'summer_rating': self._field_checkboxes["summer_rating"].isChecked(),
            'fall_rating': self._field_checkboxes["fall_rating"].isChecked(),
            'longevity': self._field_checkboxes["longevity"].isChecked(),
            'sillage': self._field_checkboxes["sillage"].isChecked(),
            'is_clone': self._field_checkboxes["is_clone"].isChecked(),
            'original_fragrance': self._field_checkboxes["original_fragrance"].isChecked(),
            'is_favorite': self._field_checkboxes["is_favorite"].isChecked()
        } 