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
    QDialog, QLabel, QLineEdit, QDoubleSpinBox, QComboBox, QCheckBox,
    QFormLayout, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QDialogButtonBox, QSpinBox, QTextEdit, QSlider, QWidget, QCompleter,
    QApplication
)
from PySide6.QtCore import Qt, Signal, Slot, QEvent, QPoint, QRect, QTimer, QStringListModel
from PySide6.QtGui import QTextCursor, QKeyEvent, QFontMetrics

from src.models import Fragrance
from src.ui.widgets import RatingSlider
from src.db import db_manager


class PerformanceSlider(QWidget):
    """
    Custom slider widget for performance metrics (longevity, sillage)
    with values from 1-5 in increments of 1
    """
    valueChanged = Signal(int)
    
    def __init__(self, label="Rating", min_value=1, max_value=5, parent=None):
        super().__init__(parent)
        
        self._min_value = min_value
        self._max_value = max_value
        self._label_text = label
        self._value = 3  # Default value
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create label above the slider
        self._label = QLabel(f"{self._label_text}: {self._value}/5")
        self._label.setAlignment(Qt.AlignCenter)
        
        # Create slider
        slider_layout = QHBoxLayout()
        
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setMinimum(self._min_value)
        self._slider.setMaximum(self._max_value)
        self._slider.setValue(self._value)
        self._slider.setTickPosition(QSlider.TicksBelow)
        self._slider.setTickInterval(1)
        
        # Min and max labels
        min_label = QLabel(f"{self._min_value}")
        max_label = QLabel(f"{self._max_value}")
        
        slider_layout.addWidget(min_label)
        slider_layout.addWidget(self._slider, 1)
        slider_layout.addWidget(max_label)
        
        main_layout.addWidget(self._label)
        main_layout.addLayout(slider_layout)
        
        # Connect signal
        self._slider.valueChanged.connect(self._on_slider_changed)
    
    def _on_slider_changed(self, value):
        """Handle slider position changes"""
        if value != self._value:
            self._value = value
            self._label.setText(f"{self._label_text}: {self._value}/5")
            self.valueChanged.emit(self._value)
    
    def value(self):
        """Get the current value"""
        return self._value
    
    def setValue(self, value):
        """Set the current value"""
        value = max(self._min_value, min(self._max_value, value))
        if value != self._value:
            self._value = value
            self._slider.setValue(value)
            self._label.setText(f"{self._label_text}: {self._value}/5")


class NotesCompleterLineEdit(QLineEdit):
    """
    Custom QLineEdit with comma-separated text autocompletion
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._completer = QCompleter([])
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.activated.connect(self._insertCompletion)
        self._completer.setWidget(self)
        self._all_items = []
        self._current_completion = ""
        
        # Connect text changed signal for real-time completion
        self.textChanged.connect(self._handleTextChanged)
        
        # Connect to completer signals for highlighted items
        self._completer.highlighted.connect(self._onCompletionHighlighted)
        
    def keyPressEvent(self, event):
        """Override key press event to handle special keys"""
        # Handle right arrow to accept current highlighted completion
        if self._completer.popup().isVisible():
            if event.key() == Qt.Key_Right:
                if self._current_completion:
                    self._insertCompletion(self._current_completion)
                    return
        
        super().keyPressEvent(event)
        
        # Don't update completer for navigation keys or other special keys
        if event.key() not in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, 
                              Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Right, Qt.Key_Left):
            self._handleTextChanged(self.text())
    
    def _onCompletionHighlighted(self, text):
        """Track the currently highlighted completion"""
        self._current_completion = text
    
    def setAllItems(self, items):
        """Set the complete list of available items"""
        self._all_items = items
        
    def _handleTextChanged(self, text):
        """Handle text changes to update the completer"""
        if not text:
            # Hide completer if there's no text
            self._completer.popup().hide()
            return
            
        # Find the last comma and get text after it
        last_comma_pos = text.rfind(",") + 1
        if last_comma_pos > 0:
            current_term = text[last_comma_pos:].strip()
        else:
            current_term = text
            
        if current_term:
            # Only update and show completer if there's something to complete
            has_matches = self._updateCompleter(current_term)
            if has_matches:
                self._completer.complete()
    
    def _updateCompleter(self, current_term):
        """Update the completer model with filtered items"""
        filtered_items = [item for item in self._all_items if current_term.lower() in item.lower()]
        
        if filtered_items:
            self._completer.setModel(QStringListModel(filtered_items))
            
            # Set the first item as current if there's an exact prefix match
            for item in filtered_items:
                if item.lower().startswith(current_term.lower()):
                    index = self._completer.completionModel().index(filtered_items.index(item), 0)
                    self._completer.popup().setCurrentIndex(index)
                    break
            return True
        else:
            # Hide the completer if there are no matches
            self._completer.popup().hide()
            return False
    
    def _insertCompletion(self, completion):
        """Insert the selected completion at the current position"""
        current_text = self.text()
        cursor_pos = self.cursorPosition()
        last_comma_pos = current_text.rfind(",", 0, cursor_pos) + 1
        
        # Create the new text with the completion inserted
        if last_comma_pos > 0:
            # Adding to existing comma-separated list
            prefix = current_text[:last_comma_pos]
            suffix = current_text[cursor_pos:]
            
            # Add space after comma if needed
            if not prefix.endswith(" "):
                prefix += " "
                
            # Build the new text with the completion properly inserted
            new_text = prefix + completion + suffix
            
            # Set the cursor position to be after the completion
            new_cursor_pos = len(prefix) + len(completion)
        else:
            # First item in the list
            suffix = current_text[cursor_pos:]
            
            # Build the new text
            new_text = completion + suffix
            
            # Set the cursor position to be after the completion
            new_cursor_pos = len(completion)
        
        # Set the new text
        self.setText(new_text)
        
        # Set the cursor position
        self.setCursorPosition(new_cursor_pos)
        
        # Hide the completer after selection
        self._completer.popup().hide()


class FragranceDialog(QDialog):
    """
    Dialog for adding or editing a fragrance
    """
    def __init__(self, fragrance=None, parent=None):
        super().__init__(parent)
        
        self._fragrance = fragrance
        self._is_edit_mode = fragrance is not None
        self._notes_list = []  # Store the list of notes for completion
        
        self._setup_ui()
        self._setup_autocompletion()
        
        if self._is_edit_mode:
            self.setWindowTitle("Edit Fragrance")
            self._load_fragrance_data()
        else:
            self.setWindowTitle("Add New Fragrance")
    
    def _setup_ui(self):
        """Set up the user interface"""
        self.setMinimumWidth(500)
        
        main_layout = QVBoxLayout(self)
        
        # Basic Info Group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self._house_input = QLineEdit()
        self._name_input = QLineEdit()
        self._size_input = QDoubleSpinBox()
        self._size_input.setRange(0.1, 50.0)
        self._size_input.setSingleStep(0.1)
        self._size_input.setDecimals(1)
        self._size_input.setSuffix(" oz")
        self._size_input.setValue(3.4)  # Common size
        self._size_input.setFixedWidth(110)  # Set fixed width to prevent overlap with buttons
        self._size_input.setStyleSheet("QDoubleSpinBox { padding-right: 20px; }")
        
        self._ml_label = QLabel("100.0 ml")
        self._size_input.valueChanged.connect(self._update_ml_equivalent)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(self._size_input)
        size_layout.addWidget(self._ml_label)
        size_layout.addStretch(1)  # Add stretch to push controls to the left
        
        self._concentration_input = QComboBox()
        self._concentration_input.addItems([
            "Eau de Cologne (EdC)",
            "Eau de Toilette (EdT)",
            "Eau de Parfum (EdP)",
            "Parfum / Extrait",
            "Elixir",
            "Pure Perfume",
            "Other"
        ])
        self._concentration_input.setCurrentIndex(1)  # EdT default
        
        basic_layout.addRow("Perfume House:", self._house_input)
        basic_layout.addRow("Perfume Name:", self._name_input)
        basic_layout.addRow("Bottle Size:", size_layout)
        basic_layout.addRow("Concentration:", self._concentration_input)
        
        # Notes Group
        notes_group = QGroupBox("Fragrance Notes")
        notes_layout = QFormLayout(notes_group)
        
        # Using custom NotesCompleterLineEdit for all notes fields
        self._top_notes_input = NotesCompleterLineEdit()
        self._top_notes_input.setPlaceholderText("Comma-separated list of top notes")
        
        self._middle_notes_input = NotesCompleterLineEdit()
        self._middle_notes_input.setPlaceholderText("Comma-separated list of middle notes")
        
        self._base_notes_input = NotesCompleterLineEdit()
        self._base_notes_input.setPlaceholderText("Comma-separated list of base notes")
        
        # Create notes autocompletion help label
        notes_help = QLabel("Tip: Type to see suggestions. Press Enter or Right-Arrow to select.")
        notes_help.setStyleSheet("color: gray; font-style: italic;")
        
        notes_layout.addRow("Top Notes:", self._top_notes_input)
        notes_layout.addRow("Middle Notes:", self._middle_notes_input)
        notes_layout.addRow("Base Notes:", self._base_notes_input)
        notes_layout.addRow("", notes_help)
        
        # Seasonality Group
        seasonality_group = QGroupBox("Seasonal Suitability")
        seasonality_layout = QVBoxLayout(seasonality_group)
        
        self._winter_slider = RatingSlider("Winter", 1.0, 5.0, 0.25)
        self._spring_slider = RatingSlider("Spring", 1.0, 5.0, 0.25)
        self._summer_slider = RatingSlider("Summer", 1.0, 5.0, 0.25)
        self._fall_slider = RatingSlider("Fall", 1.0, 5.0, 0.25)
        
        seasonality_layout.addWidget(self._winter_slider)
        seasonality_layout.addWidget(self._spring_slider)
        seasonality_layout.addWidget(self._summer_slider)
        seasonality_layout.addWidget(self._fall_slider)
        
        # Performance Group
        performance_group = QGroupBox("Performance")
        performance_layout = QVBoxLayout(performance_group)
        
        self._longevity_slider = PerformanceSlider("Longevity", 1, 5)
        self._sillage_slider = PerformanceSlider("Sillage", 1, 5)
        
        performance_layout.addWidget(self._longevity_slider)
        performance_layout.addWidget(self._sillage_slider)
        
        # Clone Information
        clone_group = QGroupBox("Clone Information")
        clone_layout = QFormLayout(clone_group)
        
        self._is_clone_checkbox = QCheckBox("This is a clone/imitation fragrance")
        self._original_fragrance_input = QLineEdit()
        self._original_fragrance_input.setPlaceholderText("Which fragrance is this a clone of?")
        self._original_fragrance_input.setEnabled(False)
        
        self._is_clone_checkbox.toggled.connect(self._toggle_clone_field)
        
        clone_layout.addRow(self._is_clone_checkbox)
        clone_layout.addRow("Original Fragrance:", self._original_fragrance_input)
        
        # Buttons
        self._button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        
        # Add all groups to main layout
        main_layout.addWidget(basic_group)
        main_layout.addWidget(notes_group)
        main_layout.addWidget(seasonality_group)
        main_layout.addWidget(performance_group)
        main_layout.addWidget(clone_group)
        main_layout.addWidget(self._button_box)
        
        # Initial update
        self._update_ml_equivalent(self._size_input.value())
    
    def _update_ml_equivalent(self, oz_value):
        """Update the milliliter equivalent label when oz value changes"""
        ml_value = round(oz_value * 29.5735, 1)
        self._ml_label.setText(f"{ml_value} ml")
    
    def _toggle_clone_field(self, is_checked):
        """Enable/disable the original fragrance field based on clone checkbox"""
        self._original_fragrance_input.setEnabled(is_checked)
        if not is_checked:
            self._original_fragrance_input.clear()
    
    def _load_fragrance_data(self):
        """Load data from existing fragrance into form fields"""
        if not self._fragrance:
            return
        
        # Basic Info
        self._house_input.setText(self._fragrance.house())
        self._name_input.setText(self._fragrance.name())
        self._size_input.setValue(self._fragrance.size_oz())
        
        # Set concentration
        concentration = self._fragrance.concentration()
        index = self._concentration_input.findText(concentration, Qt.MatchStartsWith)
        if index >= 0:
            self._concentration_input.setCurrentIndex(index)
        
        # Notes
        self._top_notes_input.setText(self._fragrance.top_notes())
        self._middle_notes_input.setText(self._fragrance.middle_notes())
        self._base_notes_input.setText(self._fragrance.base_notes())
        
        # Seasonality
        self._winter_slider.setValue(self._fragrance.winter_rating())
        self._spring_slider.setValue(self._fragrance.spring_rating())
        self._summer_slider.setValue(self._fragrance.summer_rating())
        self._fall_slider.setValue(self._fragrance.fall_rating())
        
        # Performance
        self._longevity_slider.setValue(self._fragrance.longevity())
        self._sillage_slider.setValue(self._fragrance.sillage())
        
        # Clone Info
        self._is_clone_checkbox.setChecked(self._fragrance.is_clone())
        self._original_fragrance_input.setText(self._fragrance.original_fragrance())
    
    def get_fragrance_data(self):
        """Get fragrance data from the form as a dictionary"""
        data = {
            'house': self._house_input.text(),
            'name': self._name_input.text(),
            'size_oz': self._size_input.value(),
            'concentration': self._concentration_input.currentText(),
            'top_notes': self._top_notes_input.text(),
            'middle_notes': self._middle_notes_input.text(),
            'base_notes': self._base_notes_input.text(),
            'winter_rating': self._winter_slider.value(),
            'spring_rating': self._spring_slider.value(),
            'summer_rating': self._summer_slider.value(),
            'fall_rating': self._fall_slider.value(),
            'longevity': self._longevity_slider.value(),
            'sillage': self._sillage_slider.value(),
            'is_clone': self._is_clone_checkbox.isChecked(),
            'original_fragrance': self._original_fragrance_input.text() if self._is_clone_checkbox.isChecked() else ''
        }
        
        return data
    
    def _setup_autocompletion(self):
        """Set up autocompletion for houses and notes"""
        # Get all fragrances
        fragrances = db_manager.get_all_fragrances()
        
        # Get unique houses
        houses = set()
        all_notes = set()
        
        for fragrance in fragrances:
            # Collect houses
            if fragrance['house']:
                houses.add(fragrance['house'])
            
            # Collect all notes for autocomplete
            if fragrance['top_notes']:
                for note in [n.strip() for n in fragrance['top_notes'].split(',')]:
                    if note:
                        all_notes.add(note)
            
            if fragrance['middle_notes']:
                for note in [n.strip() for n in fragrance['middle_notes'].split(',')]:
                    if note:
                        all_notes.add(note)
            
            if fragrance['base_notes']:
                for note in [n.strip() for n in fragrance['base_notes'].split(',')]:
                    if note:
                        all_notes.add(note)
        
        sample_houses = [
            "Chanel", "Dior", "Yves Saint Laurent", "Gucci", "Giorgio Armani", "Versace",
            "Prada", "Dolce & Gabbana", "Givenchy", "Hermès", "Burberry",
            "Calvin Klein", "Hugo Boss", "Tommy Hilfiger", "Lacoste", "Jean Paul Gaultier",
            "Creed", "Maison Francis Kurkdjian", "Amouage", "Parfums de Marly",
            "Xerjoff", "Initio", "Memo Paris", "Byredo", "Diptyque", "Le Labo",
            "Frederic Malle", "Maison Margiela", "Penhaligon's", "Ormonde Jayne",
            "Lattafa Perfumes", "Rasasi", "Ard Al Zaafaran", "Afnan", "Al Haramain", 
            "Swiss Arabian", "Ajmal", "Khadlaj", "Nabeel", "Armaf", "Louis Vuitton",
            "Zoologist", "Imaginary Authors", "Gallivant", "House of Matriarch",
            "4160 Tuesdays", "Slumberhouse", "Bortnikoff", "Rogue Perfumery", "DS & Durga",
            "Bath & Body Works", "Victoria's Secret", "Abercrombie & Fitch", "Coach", "Michael Kors"
        ]

        # Always include the sample houses
        houses.update(sample_houses)

        # Always add these sample notes to ensure rich autocomplete suggestions
        sample_notes = [
            "Bergamot", "Lemon", "Orange", "Grapefruit", "Lime", "Neroli",
            "Lavender", "Rose", "Jasmine", "Violet", "Ylang-Ylang", "Iris",
            "Sandalwood", "Cedarwood", "Vetiver", "Patchouli", "Musk", "Amber",
            "Vanilla", "Tobacco", "Leather", "Oud", "Cinnamon", "Cardamom",
            "Apple", "Wild Lavender", "Orange Blossom", "Lily-of-the-Valley", "Tonka Bean",
            "Black Currant", "Pink Pepper", "Cedar", "Incense", "Ginger",
            "Oakmoss", "Ambergris", "Saffron", "Pineapple", "Birch", "Moroccan Jasmine",
            "Mandarin Orange", "Petitgrain", "Seaweed", "Cotton Flower", "Virginia Cedar",
            "Woodsy Notes", "Clary Sage", "Water Notes", "Rosemary", "Green Notes",
            "Papaya", "Nutmeg", "Orris Root", "Freesia", "Green Accord", "Green Tea",
            "Guaiac Wood", "Labdanum", "Plum", "Geranium", "Truffle", "Oak", "Sichuan Pepper",
            "Star Anise", "Ambroxan", "Elemi", "Olibanum", "Blood Orange", "Juniper Berries",
            "Pimento", "Sicilian Lemon", "Fig Nectar", "Cypriol Oil or Nagarmotha",
            "Sea Water", "Juniper", "Coriander", "Basil", "Peach", "Melon", "Sea Salt",
            "Aquozone", "Green Mandarin", "Cypress", "Mastic or Lentisque", "Coconut",
            "Benzoin", "Honey", "Watermelon", "Green Apple", "Black Tea", "Frankincense",
            "Agarwood (Oud)", "Woody Notes", "Black Pepper", "Amberwood", "Violet Leaf",
            "Cashmeran", "Haitian Vetiver", "Clearwood", "Indian Ginger",
            "Green Tangerine", "Aromatic Notes", "Spicy Notes", "Patchouli Leaf", "Water Jasmine",
            "White Musk", "Moss", "Driftwood", "Tequila", "Sea Notes",
            "Agave", "Salt", "Guava", "Palm Leaf", "Red Apple", "Calabrian Bergamot",
            "Bourbon Geranium", "Tobacco Leaf", "Mineral Notes", "Papyrus",
            "Carambola (Star Fruit)", "Brazilian Rosewood", "Tarragon", "Pepper",
            "Rose de Mai", "Hyacinth", "White Pepper", "Tunisian Orange Blossom",
            "Ambrofix", "Aldeyhydes", "Sycamore", "Tahitian Vetiver", "Cashmere Wood",
            "Blackberry", "Tonka", "Bergamot Zest", "Lavandin", "Mandarin", "Mandarin Zest",
            "Orange Zest", "Grapefruit Zest", "Pear", "Peony", "Gardenia", "Magnolia",
            "Heliotrope", "Tiare Flower", "Carnation", "Cyclamen", "Honeysuckle",
            "Chamomile", "Green Leaves", "Tea", "Mate", "Beeswax", "Coumarin",
            "Myrrh", "Resins", "Balsam Fir", "Fir Resin", "Fir Balsam", "Pine",
            "Cade Oil", "Amyris", "Iso E Super", "Oakwood", "Hinoki Wood", "Mahogany",
            "Teak Wood", "Wormwood", "Absinthe", "Rum", "Whiskey", "Gin", "Cognac",
            "Champagne", "Coffee", "Cacao", "Chocolate", "Dark Chocolate", "Milk",
            "Cream", "Sugar", "Praline", "Caramel", "Almond", "Hazelnut", "Pistachio",
            "Chestnut", "Walnut", "Marzipan", "Butter", "Pastry", "Candy",
            "Mango", "Lychee", "Passionfruit", "Kiwi", "Pomegranate", "Fig", "Dates",
            "Raisin", "Currant Buds", "Red Berries", "Strawberry", "Raspberry",
            "Blueberry", "Cherry", "Ice", "Snow", "Metallic Notes", "Ink", "Gasoline",
            "Gunpowder", "Rubber", "Smoke", "Ash", "Burnt Wood", "Charcoal", "Leather Accord",
            "Suede", "Tobacco Blossom", "Hay", "Earthy Notes", "Mushroom", "Mossy Notes",
            "Rain", "Dew", "Solar Notes", "Aldehydic Notes", "Skin", "Clean Cotton", "Powdery Notes"
        ]
        
        # Always add the sample notes, regardless of whether the collection is empty
        all_notes.update(sample_notes)
        
        # Set up house autocompleter
        house_completer = QCompleter(sorted(houses))
        house_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._house_input.setCompleter(house_completer)
        
        # Set up notes autocompleters
        notes_list = sorted(all_notes)
        
        # Update notes lists for all note fields
        self._top_notes_input.setAllItems(notes_list)
        self._middle_notes_input.setAllItems(notes_list)
        self._base_notes_input.setAllItems(notes_list) 