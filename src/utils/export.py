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

import csv
import os


def export_collection_to_csv(fragrances, filepath, selected_fields=None):
    """
    Export a collection of fragrances to a CSV file
    
    Args:
        fragrances: List of Fragrance objects
        filepath: Path to save the CSV file
        selected_fields: Dictionary of field names to boolean values indicating which fields to export
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not fragrances:
        return False
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Determine which fields to include
            field_names = []
            
            # Add default fields
            if selected_fields.get('house', True):
                field_names.append('House')
            if selected_fields.get('name', True):
                field_names.append('Name')
                
            # Add selected fields
            if selected_fields.get('size_oz', False):
                field_names.append('Size (oz)')
            if selected_fields.get('size_ml', False):
                field_names.append('Size (ml)')
            if selected_fields.get('concentration', False):
                field_names.append('Concentration')
            if selected_fields.get('top_notes', False):
                field_names.append('Top Notes')
            if selected_fields.get('middle_notes', False):
                field_names.append('Middle Notes')
            if selected_fields.get('base_notes', False):
                field_names.append('Base Notes')
            if selected_fields.get('winter_rating', False):
                field_names.append('Winter Rating')
            if selected_fields.get('spring_rating', False):
                field_names.append('Spring Rating')
            if selected_fields.get('summer_rating', False):
                field_names.append('Summer Rating')
            if selected_fields.get('fall_rating', False):
                field_names.append('Fall Rating')
            if selected_fields.get('longevity', False):
                field_names.append('Longevity')
            if selected_fields.get('sillage', False):
                field_names.append('Sillage')
            if selected_fields.get('is_clone', False):
                field_names.append('Is Clone')
            if selected_fields.get('original_fragrance', False):
                field_names.append('Original Fragrance')
            if selected_fields.get('is_favorite', False):
                field_names.append('Is Favorite')
            
            # Create CSV writer
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            
            # Write each fragrance
            for fragrance in fragrances:
                row = {}
                
                # Add default fields
                if 'House' in field_names:
                    row['House'] = fragrance.house()
                if 'Name' in field_names:
                    row['Name'] = fragrance.name()
                
                # Add selected fields
                if 'Size (oz)' in field_names:
                    row['Size (oz)'] = fragrance.size_oz()
                if 'Size (ml)' in field_names:
                    row['Size (ml)'] = fragrance.size_ml()
                if 'Concentration' in field_names:
                    row['Concentration'] = fragrance.concentration()
                if 'Top Notes' in field_names:
                    row['Top Notes'] = fragrance.top_notes()
                if 'Middle Notes' in field_names:
                    row['Middle Notes'] = fragrance.middle_notes()
                if 'Base Notes' in field_names:
                    row['Base Notes'] = fragrance.base_notes()
                if 'Winter Rating' in field_names:
                    row['Winter Rating'] = fragrance.winter_rating()
                if 'Spring Rating' in field_names:
                    row['Spring Rating'] = fragrance.spring_rating()
                if 'Summer Rating' in field_names:
                    row['Summer Rating'] = fragrance.summer_rating()
                if 'Fall Rating' in field_names:
                    row['Fall Rating'] = fragrance.fall_rating()
                if 'Longevity' in field_names:
                    row['Longevity'] = fragrance.longevity()
                if 'Sillage' in field_names:
                    row['Sillage'] = fragrance.sillage()
                if 'Is Clone' in field_names:
                    row['Is Clone'] = 'Yes' if fragrance.is_clone() else 'No'
                if 'Original Fragrance' in field_names:
                    row['Original Fragrance'] = fragrance.original_fragrance()
                if 'Is Favorite' in field_names:
                    row['Is Favorite'] = 'Yes' if fragrance.is_favorite() else 'No'
                
                writer.writerow(row)
        
        return True
    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return False 