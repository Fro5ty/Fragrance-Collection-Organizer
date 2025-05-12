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
    QWidget, QLineEdit, QComboBox, QLabel, QPushButton, QVBoxLayout, 
    QHBoxLayout, QGroupBox, QCheckBox, QFormLayout, QCompleter,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal, Slot, QStringListModel, QEvent
from PySide6.QtGui import QKeyEvent

from src.db import db_manager
from src.models import collection_manager
from src.ui.dialogs import ExportDialog
from src.utils import export_collection_to_csv


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


class FilterPanel(QWidget):
    """
    Panel for searching and filtering fragrances
    """
    filtersApplied = Signal(dict)
    searchApplied = Signal(str)
    expandAllClicked = Signal()
    collapseAllClicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._setup_ui()
        self._populate_filter_options()
        
        # Connect to collection updates to refresh filter options
        collection_manager.collection_updated.connect(self._populate_filter_options)
    
    def _setup_ui(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search Group
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout(search_group)
        
        # Search box
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search by house or name...")
        # Connect Enter key press to trigger search
        self._search_input.returnPressed.connect(self._apply_search)
        search_layout.addWidget(self._search_input)
        
        # Search button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self._apply_search)
        search_layout.addWidget(search_button)
        
        # Filters Group
        filters_group = QGroupBox("Filters")
        filters_layout = QFormLayout(filters_group)
        
        # House filter
        self._house_filter = QComboBox()
        self._house_filter.addItem("All Houses", None)
        filters_layout.addRow("House:", self._house_filter)
        
        # Season filter
        self._season_filter = QComboBox()
        self._season_filter.addItems(["All Seasons", "Winter", "Spring", "Summer", "Fall"])
        filters_layout.addRow("Season:", self._season_filter)
        
        # Notes filter - use custom LineEdit with autocomplete
        self._notes_filter = NotesCompleterLineEdit()
        self._notes_filter.setPlaceholderText("Filter by notes (comma separated)")
        filters_layout.addRow("Notes:", self._notes_filter)
        
        # Favorites filter
        self._favorites_filter = QCheckBox("Favorites Only")
        filters_layout.addRow("", self._favorites_filter)
        
        # Apply filters button
        filter_button = QPushButton("Apply Filters")
        filter_button.clicked.connect(self._apply_filters)
        
        # Clear filters button
        clear_button = QPushButton("Clear Filters")
        clear_button.clicked.connect(self._clear_filters)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(filter_button)
        buttons_layout.addWidget(clear_button)
        filters_layout.addRow(buttons_layout)
        
        # Sort options
        sort_group = QGroupBox("Sort Options")
        sort_layout = QFormLayout(sort_group)
        
        self._sort_field = QComboBox()
        self._sort_field.addItems([
            "House & Name", 
            "Favorites First",
            "Longevity (Highest First)", 
            "Longevity (Lowest First)",
            "Sillage (Highest First)", 
            "Sillage (Lowest First)",
            "Winter Rating", 
            "Spring Rating", 
            "Summer Rating", 
            "Fall Rating"
        ])
        
        sort_layout.addRow("Sort by:", self._sort_field)
        
        # Sort apply button
        sort_button = QPushButton("Apply Sorting")
        sort_button.clicked.connect(self._apply_sort)
        sort_layout.addRow(sort_button)
        
        # Expand/Collapse group
        expand_group = QGroupBox("Expand/Collapse")
        expand_layout = QHBoxLayout(expand_group)
        
        # Expand all button
        expand_all_button = QPushButton("Expand All")
        expand_all_button.clicked.connect(self._on_expand_all)
        expand_layout.addWidget(expand_all_button)
        
        # Collapse all button
        collapse_all_button = QPushButton("Collapse All")
        collapse_all_button.clicked.connect(self._on_collapse_all)
        expand_layout.addWidget(collapse_all_button)
        
        # Export group
        export_group = QGroupBox("Export Collection")
        export_layout = QVBoxLayout(export_group)
        
        # Export description
        export_label = QLabel(
            "Export your fragrance collection to a CSV file\n"
            "that can be opened in Excel or other spreadsheet programs."
        )
        export_label.setAlignment(Qt.AlignCenter)
        export_layout.addWidget(export_label)
        
        # Export button
        export_button = QPushButton("Export to CSV...")
        export_button.clicked.connect(self._export_collection)
        export_layout.addWidget(export_button)
        
        # Add all groups to main layout
        main_layout.addWidget(search_group)
        main_layout.addWidget(filters_group)
        main_layout.addWidget(sort_group)
        main_layout.addWidget(expand_group)
        main_layout.addWidget(export_group)
        main_layout.addStretch()
    
    def _populate_filter_options(self):
        """Populate filter dropdown options based on collection data"""
        # Get all fragrances
        fragrances = collection_manager.get_all_fragrances()
        
        # Get unique houses
        houses = set()
        all_notes = set()
        
        for fragrance in fragrances:
            if fragrance.house():
                houses.add(fragrance.house())
            
            # Collect all notes for autocomplete
            if fragrance.top_notes():
                for note in [n.strip() for n in fragrance.top_notes().split(',')]:
                    if note:
                        all_notes.add(note)
            
            if fragrance.middle_notes():
                for note in [n.strip() for n in fragrance.middle_notes().split(',')]:
                    if note:
                        all_notes.add(note)
            
            if fragrance.base_notes():
                for note in [n.strip() for n in fragrance.base_notes().split(',')]:
                    if note:
                        all_notes.add(note)
        
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
        
        # Update house filter
        current_house = self._house_filter.currentText()
        self._house_filter.clear()
        self._house_filter.addItem("All Houses", None)
        
        for house in sorted(houses):
            self._house_filter.addItem(house, house)
        
        # Try to restore the previous selection if it exists
        if current_house != "All Houses":
            index = self._house_filter.findText(current_house)
            if index >= 0:
                self._house_filter.setCurrentIndex(index)
        
        # Update notes completer with sorted notes
        self._notes_filter.setAllItems(sorted(all_notes))
    
    @Slot()
    def _apply_search(self):
        """Apply the search term"""
        search_term = self._search_input.text().strip()
        self.searchApplied.emit(search_term)
    
    @Slot()
    def _apply_filters(self):
        """Apply the selected filters"""
        filters = {}
        
        # House filter
        if self._house_filter.currentText() != "All Houses":
            filters['house'] = self._house_filter.currentText()
        
        # Season filter
        season = self._season_filter.currentText()
        if season != "All Seasons":
            filters['season'] = season
        
        # Notes filter
        notes_text = self._notes_filter.text().strip()
        if notes_text:
            notes = [note.strip() for note in notes_text.split(',')]
            if notes:
                filters['notes'] = notes
        
        # Favorites filter
        if self._favorites_filter.isChecked():
            filters['favorite'] = True
        
        self.filtersApplied.emit(filters)
    
    @Slot()
    def _clear_filters(self):
        """Clear all filters"""
        self._house_filter.setCurrentIndex(0)
        self._season_filter.setCurrentIndex(0)
        self._notes_filter.clear()
        self._search_input.clear()
        self._favorites_filter.setChecked(False)
        
        # Apply empty filters to reset
        self.searchApplied.emit("")
        self.filtersApplied.emit({})
    
    @Slot()
    def _apply_sort(self):
        """Apply the selected sort options"""
        sort_option = self._sort_field.currentText()
        
        if sort_option == "House & Name":
            collection_manager.set_sort("house", "ASC")
        elif sort_option == "Favorites First":
            collection_manager.set_sort("is_favorite", "DESC")
        elif sort_option == "Longevity (Highest First)":
            collection_manager.set_sort("longevity", "DESC")
        elif sort_option == "Longevity (Lowest First)":
            collection_manager.set_sort("longevity", "ASC")
        elif sort_option == "Sillage (Highest First)":
            collection_manager.set_sort("sillage", "DESC")
        elif sort_option == "Sillage (Lowest First)":
            collection_manager.set_sort("sillage", "ASC")
        elif sort_option == "Winter Rating":
            collection_manager.set_sort("winter_rating", "DESC")
        elif sort_option == "Spring Rating":
            collection_manager.set_sort("spring_rating", "DESC")
        elif sort_option == "Summer Rating":
            collection_manager.set_sort("summer_rating", "DESC")
        elif sort_option == "Fall Rating":
            collection_manager.set_sort("fall_rating", "DESC")
    
    @Slot()
    def _on_expand_all(self):
        """Emit signal when Expand All button is clicked"""
        self.expandAllClicked.emit()
    
    @Slot()
    def _on_collapse_all(self):
        """Emit signal when Collapse All button is clicked"""
        self.collapseAllClicked.emit()
    
    @Slot()
    def _export_collection(self):
        """Export the fragrance collection to a CSV file"""
        # Get all fragrances
        fragrances = collection_manager.get_all_fragrances()
        
        if not fragrances:
            QMessageBox.warning(
                self,
                "Export Error",
                "There are no fragrances in your collection to export."
            )
            return
        
        # Show export options dialog
        export_dialog = ExportDialog(self)
        if export_dialog.exec() != ExportDialog.Accepted:
            return
        
        # Get selected fields
        selected_fields = export_dialog.get_selected_fields()
        
        # Get save file path
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Collection",
            "Fragrance_Collection.csv",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if not filepath:
            return
        
        # Ensure .csv extension
        if not filepath.lower().endswith('.csv'):
            filepath += '.csv'
        
        # Export to CSV
        success = export_collection_to_csv(fragrances, filepath, selected_fields)
        
        if success:
            QMessageBox.information(
                self,
                "Export Successful",
                f"Your fragrance collection has been exported to:\n{filepath}"
            )
        else:
            QMessageBox.critical(
                self,
                "Export Error",
                "An error occurred while exporting your collection. Please try again."
            ) 