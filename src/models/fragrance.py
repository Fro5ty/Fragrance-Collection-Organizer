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

from PySide6.QtCore import QObject, Property, Signal, Slot, QDateTime


class Fragrance(QObject):
    """
    Represents a single fragrance in the collection.
    This is a Qt-aware wrapper around the raw data from the database.
    """
    dataChanged = Signal()
    
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self._data = data or {}
        
        # Set default values if not provided
        if 'id' not in self._data:
            self._data['id'] = None
        if 'house' not in self._data:
            self._data['house'] = ""
        if 'name' not in self._data:
            self._data['name'] = ""
        if 'size_oz' not in self._data:
            self._data['size_oz'] = 0.0
        if 'size_ml' not in self._data:
            self._data['size_ml'] = 0.0
        if 'concentration' not in self._data:
            self._data['concentration'] = ""
        if 'top_notes' not in self._data:
            self._data['top_notes'] = ""
        if 'middle_notes' not in self._data:
            self._data['middle_notes'] = ""
        if 'base_notes' not in self._data:
            self._data['base_notes'] = ""
        if 'winter_rating' not in self._data:
            self._data['winter_rating'] = 3.0
        if 'spring_rating' not in self._data:
            self._data['spring_rating'] = 3.0
        if 'summer_rating' not in self._data:
            self._data['summer_rating'] = 3.0
        if 'fall_rating' not in self._data:
            self._data['fall_rating'] = 3.0
        if 'longevity' not in self._data:
            self._data['longevity'] = 3
        if 'sillage' not in self._data:
            self._data['sillage'] = 3
        if 'is_clone' not in self._data:
            self._data['is_clone'] = False
        if 'original_fragrance' not in self._data:
            self._data['original_fragrance'] = ""
        if 'is_favorite' not in self._data:
            self._data['is_favorite'] = False
    
    # Helper to convert database data to model data
    @staticmethod
    def from_db_row(row):
        """Convert a database row to a Fragrance instance"""
        data = dict(row)
        
        # Convert boolean fields from SQLite (0/1) to Python bool
        data['is_clone'] = bool(data.get('is_clone', 0))
        data['is_favorite'] = bool(data.get('is_favorite', 0))
        
        return Fragrance(data)
    
    # Properties and accessors for all fields
    def id(self):
        return self._data.get('id')
    
    def house(self):
        return self._data.get('house', '')
    
    @Slot(str)
    def set_house(self, house):
        if self._data.get('house') != house:
            self._data['house'] = house
            self.dataChanged.emit()
    
    def name(self):
        return self._data.get('name', '')
    
    @Slot(str)
    def set_name(self, name):
        if self._data.get('name') != name:
            self._data['name'] = name
            self.dataChanged.emit()
    
    def full_name(self):
        """Get the full name (house + name)"""
        house = self.house()
        name = self.name()
        if house and name:
            return f"{house} {name}"
        return house or name or "Unnamed Fragrance"
    
    def size_oz(self):
        return self._data.get('size_oz', 0.0)
    
    @Slot(float)
    def set_size_oz(self, size_oz):
        if self._data.get('size_oz') != size_oz:
            self._data['size_oz'] = size_oz
            # Auto-calculate ml equivalent (1 oz ≈ 29.5735 ml)
            self._data['size_ml'] = round(size_oz * 29.5735, 1)
            self.dataChanged.emit()
    
    def size_ml(self):
        return self._data.get('size_ml', 0.0)
    
    def concentration(self):
        return self._data.get('concentration', '')
    
    @Slot(str)
    def set_concentration(self, concentration):
        if self._data.get('concentration') != concentration:
            self._data['concentration'] = concentration
            self.dataChanged.emit()
    
    def top_notes(self):
        return self._data.get('top_notes', '')
    
    @Slot(str)
    def set_top_notes(self, notes):
        if self._data.get('top_notes') != notes:
            self._data['top_notes'] = notes
            self.dataChanged.emit()
    
    def middle_notes(self):
        return self._data.get('middle_notes', '')
    
    @Slot(str)
    def set_middle_notes(self, notes):
        if self._data.get('middle_notes') != notes:
            self._data['middle_notes'] = notes
            self.dataChanged.emit()
    
    def base_notes(self):
        return self._data.get('base_notes', '')
    
    @Slot(str)
    def set_base_notes(self, notes):
        if self._data.get('base_notes') != notes:
            self._data['base_notes'] = notes
            self.dataChanged.emit()
    
    def winter_rating(self):
        return self._data.get('winter_rating', 3.0)
    
    @Slot(float)
    def set_winter_rating(self, rating):
        # Ensure rating is within bounds and has valid precision
        rating = round(max(1.0, min(5.0, rating)) * 4) / 4  # Round to nearest 0.25
        if self._data.get('winter_rating') != rating:
            self._data['winter_rating'] = rating
            self.dataChanged.emit()
    
    def spring_rating(self):
        return self._data.get('spring_rating', 3.0)
    
    @Slot(float)
    def set_spring_rating(self, rating):
        rating = round(max(1.0, min(5.0, rating)) * 4) / 4  # Round to nearest 0.25
        if self._data.get('spring_rating') != rating:
            self._data['spring_rating'] = rating
            self.dataChanged.emit()
    
    def summer_rating(self):
        return self._data.get('summer_rating', 3.0)
    
    @Slot(float)
    def set_summer_rating(self, rating):
        rating = round(max(1.0, min(5.0, rating)) * 4) / 4  # Round to nearest 0.25
        if self._data.get('summer_rating') != rating:
            self._data['summer_rating'] = rating
            self.dataChanged.emit()
    
    def fall_rating(self):
        return self._data.get('fall_rating', 3.0)
    
    @Slot(float)
    def set_fall_rating(self, rating):
        rating = round(max(1.0, min(5.0, rating)) * 4) / 4  # Round to nearest 0.25
        if self._data.get('fall_rating') != rating:
            self._data['fall_rating'] = rating
            self.dataChanged.emit()
    
    def longevity(self):
        return self._data.get('longevity', 3)
    
    @Slot(int)
    def set_longevity(self, longevity):
        longevity = max(1, min(5, longevity))  # Ensure within range 1-5
        if self._data.get('longevity') != longevity:
            self._data['longevity'] = longevity
            self.dataChanged.emit()
    
    def sillage(self):
        return self._data.get('sillage', 3)
    
    @Slot(int)
    def set_sillage(self, sillage):
        sillage = max(1, min(5, sillage))  # Ensure within range 1-5
        if self._data.get('sillage') != sillage:
            self._data['sillage'] = sillage
            self.dataChanged.emit()
    
    def is_clone(self):
        return self._data.get('is_clone', False)
    
    @Slot(bool)
    def set_is_clone(self, is_clone):
        if self._data.get('is_clone') != is_clone:
            self._data['is_clone'] = is_clone
            self.dataChanged.emit()
    
    def original_fragrance(self):
        return self._data.get('original_fragrance', '')
    
    @Slot(str)
    def set_original_fragrance(self, original):
        if self._data.get('original_fragrance') != original:
            self._data['original_fragrance'] = original
            self.dataChanged.emit()
    
    def is_favorite(self):
        return self._data.get('is_favorite', False)
    
    @Slot(bool)
    def set_is_favorite(self, is_favorite):
        if self._data.get('is_favorite') != is_favorite:
            self._data['is_favorite'] = is_favorite
            self.dataChanged.emit()
    
    def to_dict(self):
        """Convert the fragrance data to a dictionary for database operations"""
        return {
            'house': self.house(),
            'name': self.name(),
            'size_oz': self.size_oz(),
            'size_ml': self.size_ml(),
            'concentration': self.concentration(),
            'top_notes': self.top_notes(),
            'middle_notes': self.middle_notes(),
            'base_notes': self.base_notes(),
            'winter_rating': self.winter_rating(),
            'spring_rating': self.spring_rating(),
            'summer_rating': self.summer_rating(),
            'fall_rating': self.fall_rating(),
            'longevity': self.longevity(),
            'sillage': self.sillage(),
            'is_clone': self.is_clone(),
            'original_fragrance': self.original_fragrance(),
            'is_favorite': self.is_favorite()
        } 