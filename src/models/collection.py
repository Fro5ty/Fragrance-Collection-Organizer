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

from PySide6.QtCore import QObject, Signal, Slot, QSortFilterProxyModel, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

from src.db import db_manager
from .fragrance import Fragrance


class FragranceCollectionModel(QStandardItemModel):
    """
    Model to display fragrances in a view
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fragrances = []
        
        # Set up columns
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels([
            "Fragrance", "Size", "Concentration", 
            "Notes", "Seasonality", "Longevity", 
            "Sillage", "Clone Info"
        ])
    
    def refresh_fragrances(self, fragrances):
        """Update the model with new fragrance data"""
        self.beginResetModel()
        self._fragrances = fragrances
        self.clear()
        
        # Set up columns again after clear
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels([
            "Fragrance", "Size", "Concentration", 
            "Notes", "Seasonality", "Longevity", 
            "Sillage", "Clone Info"
        ])
        
        # Add fragrances to model
        for fragrance in fragrances:
            self._add_fragrance_row(fragrance)
        
        self.endResetModel()
    
    def _add_fragrance_row(self, fragrance):
        row = []
        
        # Column 0: Fragrance (House + Name)
        name_item = QStandardItem(f"{fragrance.house()} {fragrance.name()}")
        name_item.setData(fragrance.id(), Qt.UserRole)
        row.append(name_item)
        
        # Column 1: Size
        size_item = QStandardItem(f"{fragrance.size_oz()} oz ({fragrance.size_ml()} ml)")
        row.append(size_item)
        
        # Column 2: Concentration
        concentration_item = QStandardItem(fragrance.concentration())
        row.append(concentration_item)
        
        # Column 3: Notes
        notes = []
        if fragrance.top_notes():
            notes.append(f"Top: {fragrance.top_notes()}")
        if fragrance.middle_notes():
            notes.append(f"Mid: {fragrance.middle_notes()}")
        if fragrance.base_notes():
            notes.append(f"Base: {fragrance.base_notes()}")
        notes_item = QStandardItem("\n".join(notes))
        row.append(notes_item)
        
        # Column 4: Seasonality
        seasons = [
            f"Winter: {fragrance.winter_rating()}",
            f"Spring: {fragrance.spring_rating()}",
            f"Summer: {fragrance.summer_rating()}",
            f"Fall: {fragrance.fall_rating()}"
        ]
        seasonality_item = QStandardItem("\n".join(seasons))
        row.append(seasonality_item)
        
        # Column 5: Longevity
        longevity_item = QStandardItem(str(fragrance.longevity()))
        row.append(longevity_item)
        
        # Column 6: Sillage
        sillage_item = QStandardItem(str(fragrance.sillage()))
        row.append(sillage_item)
        
        # Column 7: Clone Info
        clone_text = ""
        if fragrance.is_clone():
            clone_text = f"Clone of: {fragrance.original_fragrance()}"
        clone_item = QStandardItem(clone_text)
        row.append(clone_item)
        
        self.appendRow(row)


class FragranceCollectionManager(QObject):
    """
    Manages the fragrance collection, providing operations to add, edit, remove, 
    search, and filter fragrances.
    """
    collection_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fragrances = []
        self._filtered_fragrances = []
        self._search_term = ""
        self._filters = {}
        self._sort_field = "house"
        self._sort_order = "ASC"
        
        # Connect to database updates
        db_manager.database_updated.connect(self.refresh_collection)
        
        # Initialize collection
        self.refresh_collection()
    
    @Slot()
    def refresh_collection(self):
        """Refresh the collection from the database"""
        db_fragrances = db_manager.get_all_fragrances(
            sort_by=self._sort_field, 
            sort_order=self._sort_order
        )
        
        self._fragrances = [Fragrance.from_db_row(row) for row in db_fragrances]
        self._apply_filters()
        
        self.collection_updated.emit()
    
    def get_fragrances(self):
        """Get the list of fragrances (filtered if filters are applied)"""
        return self._filtered_fragrances
    
    def get_all_fragrances(self):
        """Get all fragrances without filtering"""
        return self._fragrances
    
    def get_collection_stats(self):
        """Get statistics about the collection"""
        return db_manager.get_collection_stats()
    
    @Slot(dict)
    def add_fragrance(self, fragrance_data):
        """Add a new fragrance to the collection"""
        fragrance_id = db_manager.add_fragrance(fragrance_data)
        return fragrance_id
    
    @Slot(int, dict)
    def update_fragrance(self, fragrance_id, fragrance_data):
        """Update an existing fragrance"""
        success = db_manager.update_fragrance(fragrance_id, fragrance_data)
        return success
    
    @Slot(int)
    def delete_fragrance(self, fragrance_id):
        """Delete a fragrance from the collection"""
        success = db_manager.delete_fragrance(fragrance_id)
        return success
    
    @Slot(str)
    def set_search_term(self, term):
        """Set the search term for filtering"""
        if self._search_term != term:
            self._search_term = term
            self._apply_filters()
            self.collection_updated.emit()
    
    @Slot(dict)
    def set_filters(self, filters):
        """Set filters for the collection"""
        self._filters = filters or {}
        self._apply_filters()
        self.collection_updated.emit()
    
    @Slot(str, str)
    def set_sort(self, field, order="ASC"):
        """Set the sort field and order"""
        if self._sort_field != field or self._sort_order != order:
            self._sort_field = field
            self._sort_order = order
            self.refresh_collection()
    
    def _apply_filters(self):
        """Apply search term and filters to the collection"""
        if not self._search_term and not self._filters:
            self._filtered_fragrances = self._fragrances
            return
        
        # Get filtered results from database
        db_filtered = db_manager.search_fragrances(
            search_term=self._search_term,
            filters=self._filters
        )
        
        # Convert to Fragrance objects
        self._filtered_fragrances = [Fragrance.from_db_row(row) for row in db_filtered]


# Create a singleton instance
collection_manager = FragranceCollectionManager() 