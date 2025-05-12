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

import os
import sqlite3
from PySide6.QtCore import QObject, Signal


class DatabaseManager(QObject):

    database_updated = Signal()
    
    def __init__(self, db_path="fragrances.db"):
        super().__init__()
        self.db_path = db_path
        self.initialize_database()
    
    def get_connection(self):
        """Create and return a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_database(self):
        """Initialize the database with required tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create fragrances table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fragrances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            house TEXT NOT NULL,
            name TEXT NOT NULL,
            size_oz REAL NOT NULL,
            size_ml REAL NOT NULL,
            concentration TEXT NOT NULL,
            top_notes TEXT,
            middle_notes TEXT,
            base_notes TEXT,
            winter_rating REAL DEFAULT 3.0,
            spring_rating REAL DEFAULT 3.0,
            summer_rating REAL DEFAULT 3.0,
            fall_rating REAL DEFAULT 3.0,
            longevity INTEGER DEFAULT 3,
            sillage INTEGER DEFAULT 3,
            is_clone BOOLEAN DEFAULT 0,
            original_fragrance TEXT,
            is_favorite INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute("PRAGMA table_info(fragrances)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_favorite' not in columns:
            cursor.execute('ALTER TABLE fragrances ADD COLUMN is_favorite INTEGER DEFAULT 0')
        
        conn.commit()
        conn.close()
    
    def add_fragrance(self, fragrance_data):
        """
        Add a new fragrance to the database
        
        Args:
            fragrance_data (dict): Dictionary containing fragrance information
        
        Returns:
            int: ID of the newly added fragrance
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert bottle size from oz to ml
        size_oz = fragrance_data.get('size_oz', 0)
        size_ml = round(size_oz * 29.5735, 1)  # Convert and round to nearest 0.1 ml
        
        query = '''
        INSERT INTO fragrances (
            house, name, size_oz, size_ml, concentration, 
            top_notes, middle_notes, base_notes,
            winter_rating, spring_rating, summer_rating, fall_rating,
            longevity, sillage, is_clone, original_fragrance, is_favorite
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        cursor.execute(query, (
            fragrance_data.get('house', ''),
            fragrance_data.get('name', ''),
            size_oz,
            size_ml,
            fragrance_data.get('concentration', ''),
            fragrance_data.get('top_notes', ''),
            fragrance_data.get('middle_notes', ''),
            fragrance_data.get('base_notes', ''),
            fragrance_data.get('winter_rating', 3.0),
            fragrance_data.get('spring_rating', 3.0),
            fragrance_data.get('summer_rating', 3.0),
            fragrance_data.get('fall_rating', 3.0),
            fragrance_data.get('longevity', 3),
            fragrance_data.get('sillage', 3),
            1 if fragrance_data.get('is_clone', False) else 0,
            fragrance_data.get('original_fragrance', ''),
            1 if fragrance_data.get('is_favorite', False) else 0
        ))
        
        fragrance_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.database_updated.emit()
        return fragrance_id
    
    def update_fragrance(self, fragrance_id, fragrance_data):
        """
        Update an existing fragrance in the database
        
        Args:
            fragrance_id (int): ID of the fragrance to update
            fragrance_data (dict): Dictionary containing updated fragrance information
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert bottle size from oz to ml
        size_oz = fragrance_data.get('size_oz', 0)
        size_ml = round(size_oz * 29.5735, 1)  # Convert and round to nearest 0.1 ml
        
        query = '''
        UPDATE fragrances SET
            house = ?,
            name = ?,
            size_oz = ?,
            size_ml = ?,
            concentration = ?,
            top_notes = ?,
            middle_notes = ?,
            base_notes = ?,
            winter_rating = ?,
            spring_rating = ?,
            summer_rating = ?,
            fall_rating = ?,
            longevity = ?,
            sillage = ?,
            is_clone = ?,
            original_fragrance = ?,
            is_favorite = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        '''
        
        cursor.execute(query, (
            fragrance_data.get('house', ''),
            fragrance_data.get('name', ''),
            size_oz,
            size_ml,
            fragrance_data.get('concentration', ''),
            fragrance_data.get('top_notes', ''),
            fragrance_data.get('middle_notes', ''),
            fragrance_data.get('base_notes', ''),
            fragrance_data.get('winter_rating', 3.0),
            fragrance_data.get('spring_rating', 3.0),
            fragrance_data.get('summer_rating', 3.0),
            fragrance_data.get('fall_rating', 3.0),
            fragrance_data.get('longevity', 3),
            fragrance_data.get('sillage', 3),
            1 if fragrance_data.get('is_clone', False) else 0,
            fragrance_data.get('original_fragrance', ''),
            1 if fragrance_data.get('is_favorite', False) else 0,
            fragrance_id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        self.database_updated.emit()
        return success
    
    def delete_fragrance(self, fragrance_id):
        """
        Delete a fragrance from the database
        
        Args:
            fragrance_id (int): ID of the fragrance to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM fragrances WHERE id = ?"
        cursor.execute(query, (fragrance_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        self.database_updated.emit()
        return success
    
    def get_all_fragrances(self, sort_by="house", sort_order="ASC"):
        """
        Retrieve all fragrances from the database
        
        Args:
            sort_by (str): Field to sort by
            sort_order (str): 'ASC' for ascending or 'DESC' for descending
        
        Returns:
            list: List of dictionaries containing fragrance data
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        valid_sort_fields = [
            "id", "house", "name", "concentration", 
            "winter_rating", "spring_rating", "summer_rating", "fall_rating",
            "longevity", "sillage"
        ]
        
        if sort_by not in valid_sort_fields:
            sort_by = "house"
            
        if sort_order not in ["ASC", "DESC"]:
            sort_order = "ASC"
        
        query = f"""
        SELECT * FROM fragrances 
        ORDER BY {sort_by} {sort_order}, house ASC, name ASC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        fragrances = []
        for row in rows:
            fragrances.append(dict(row))
        
        conn.close()
        return fragrances
    
    def search_fragrances(self, search_term="", filters=None):
        """
        Search fragrances with optional filtering
        
        Args:
            search_term (str): Term to search for in house and name
            filters (dict): Optional dictionary containing filter criteria
                - notes (list): List of notes to filter by
                - season (str): Season to filter by (Winter, Spring, Summer, Fall)
                - house (str): House to filter by
        
        Returns:
            list: List of dictionaries containing filtered fragrance data
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM fragrances WHERE 1=1"
        params = []
        
        # Apply search term to house and name
        if search_term:
            query += " AND (house LIKE ? OR name LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        # Apply filters if provided
        if filters:
            # Filter by notes
            if filters.get('notes'):
                note_conditions = []
                for note in filters['notes']:
                    note_conditions.append("(top_notes LIKE ? OR middle_notes LIKE ? OR base_notes LIKE ?)")
                    params.extend([f"%{note}%", f"%{note}%", f"%{note}%"])
                
                if note_conditions:
                    query += f" AND ({' OR '.join(note_conditions)})"
            
            # Filter by season
            if filters.get('season'):
                season = filters['season'].lower()
                if season in ['winter', 'spring', 'summer', 'fall']:
                    query += f" AND {season}_rating >= 3.5"  # Consider suitable if rating > 3.5
            
            # Filter by house
            if filters.get('house'):
                query += " AND house = ?"
                params.append(filters['house'])
            
            # Filter by favorite
            if filters.get('favorite') and filters['favorite']:
                query += " AND is_favorite = 1"
        
        # Apply default sorting
        query += " ORDER BY house ASC, name ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        fragrances = []
        for row in rows:
            fragrances.append(dict(row))
        
        conn.close()
        return fragrances
    
    def get_collection_stats(self):
        """
        Get statistics about the fragrance collection
        
        Returns:
            dict: Dictionary containing collection statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM fragrances")
        total = cursor.fetchone()['total']
        
        # Get houses count
        cursor.execute("SELECT COUNT(DISTINCT house) as house_count FROM fragrances")
        house_count = cursor.fetchone()['house_count']
        
        # Get average ratings
        cursor.execute("""
            SELECT 
                AVG(winter_rating) as avg_winter,
                AVG(spring_rating) as avg_spring,
                AVG(summer_rating) as avg_summer,
                AVG(fall_rating) as avg_fall,
                AVG(longevity) as avg_longevity,
                AVG(sillage) as avg_sillage
            FROM fragrances
        """)
        
        averages = dict(cursor.fetchone())
        
        conn.close()
        
        return {
            "total_fragrances": total,
            "house_count": house_count,
            "averages": averages
        }
    
    def get_top_houses(self, limit=3):
        """
        Get the most common houses in the collection
        
        Args:
            limit: Maximum number of houses to return
            
        Returns:
            List of tuples (house_name, count)
        """
        try:
            cursor = self.get_connection().cursor()
            query = """
                SELECT house, COUNT(*) as count
                FROM fragrances
                GROUP BY house
                ORDER BY count DESC
                LIMIT ?
            """
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            return [(row['house'], row['count']) for row in results]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def get_top_notes(self, limit=10):
        """
        Get the most common notes in the collection
        
        Args:
            limit: Maximum number of notes to return
            
        Returns:
            List of tuples (note, count)
        """
        try:
            cursor = self.get_connection().cursor()
            
            # Process and count all notes by splitting the comma-separated lists
            query = """
                SELECT f.id, f.top_notes, f.middle_notes, f.base_notes
                FROM fragrances f
            """
            cursor.execute(query)
            all_fragrances = cursor.fetchall()
            
            # Process notes (split by comma, trim whitespace)
            note_counts = {}
            for frag in all_fragrances:
                note_fields = [
                    frag['top_notes'] or "", 
                    frag['middle_notes'] or "", 
                    frag['base_notes'] or ""
                ]
                
                for field in note_fields:
                    if field.strip():
                        notes = [n.strip() for n in field.split(',')]
                        for note in notes:
                            if note:  # Skip empty notes
                                note_counts[note] = note_counts.get(note, 0) + 1
            
            # Sort by count and get the top notes
            sorted_notes = sorted(note_counts.items(), key=lambda x: x[1], reverse=True)
            return sorted_notes[:limit]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def get_seasonal_averages(self):
        """
        Get average ratings for each season across the collection
        
        Returns:
            Dictionary with season averages
        """
        try:
            cursor = self.get_connection().cursor()
            query = """
                SELECT 
                    AVG(winter_rating) as winter_avg,
                    AVG(spring_rating) as spring_avg,
                    AVG(summer_rating) as summer_avg,
                    AVG(fall_rating) as fall_avg
                FROM fragrances
            """
            cursor.execute(query)
            return dict(cursor.fetchone())
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {}
    
    def get_seasonal_preferences(self):
        """
        Get the number of fragrances that score highest in each season
        If a fragrance scores highest in multiple seasons, it's counted in each
        
        Returns:
            Dictionary with season counts and ties
        """
        try:
            cursor = self.get_connection().cursor()
            
            # Get all fragrances with their seasonal ratings
            query = """
                SELECT id, winter_rating, spring_rating, summer_rating, fall_rating
                FROM fragrances
            """
            cursor.execute(query)
            fragrances = cursor.fetchall()
            
            # Count fragrances by their highest rated season
            winter_count = 0
            spring_count = 0
            summer_count = 0
            fall_count = 0
            
            for frag in fragrances:
                # Get all ratings
                winter = frag['winter_rating']
                spring = frag['spring_rating']
                summer = frag['summer_rating']
                fall = frag['fall_rating']
                
                # Find the maximum rating
                max_rating = max(winter, spring, summer, fall)
                
                # Count each season that matches the max rating
                if winter == max_rating:
                    winter_count += 1
                if spring == max_rating:
                    spring_count += 1
                if summer == max_rating:
                    summer_count += 1
                if fall == max_rating:
                    fall_count += 1
            
            return {
                'winter_count': winter_count,
                'spring_count': spring_count,
                'summer_count': summer_count,
                'fall_count': fall_count
            }
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {}
            
    def get_top_notes_from_favorites(self, limit=10):
        """
        Get the most common notes in favorited fragrances
        
        Args:
            limit: Maximum number of notes to return
            
        Returns:
            List of tuples (note, count)
        """
        try:
            cursor = self.get_connection().cursor()
            
            # Process and count notes from favorited fragrances only
            query = """
                SELECT f.id, f.top_notes, f.middle_notes, f.base_notes
                FROM fragrances f
                WHERE f.is_favorite = 1
            """
            cursor.execute(query)
            favorite_fragrances = cursor.fetchall()
            
            # Process notes (split by comma, trim whitespace)
            note_counts = {}
            for frag in favorite_fragrances:
                note_fields = [
                    frag['top_notes'] or "", 
                    frag['middle_notes'] or "", 
                    frag['base_notes'] or ""
                ]
                
                for field in note_fields:
                    if field.strip():
                        notes = [n.strip() for n in field.split(',')]
                        for note in notes:
                            if note:  # Skip empty notes
                                note_counts[note] = note_counts.get(note, 0) + 1
            
            # Sort by count and get the top notes
            sorted_notes = sorted(note_counts.items(), key=lambda x: x[1], reverse=True)
            return sorted_notes[:limit] 
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return [] 