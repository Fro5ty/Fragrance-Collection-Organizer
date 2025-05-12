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
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QPushButton, QFrame, QSpacerItem, QSizePolicy,
    QMessageBox, QLayout
)
from PySide6.QtCore import Qt, Signal, Property, Slot, QRect, QSize, QPoint

from src.models import collection_manager, Fragrance
from src.ui.dialogs import FragranceDialog
from src.utils import theme_manager
from .fragrance_item import FragranceItem


# Custom flow layout for responsive item display
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self._items = []
    
    def __del__(self):
        while self.count():
            self.takeAt(0)
    
    def addItem(self, item):
        self._items.append(item)
    
    def count(self):
        return len(self._items)
    
    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientations(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        
        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size
    
    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        # Calculate the available width
        available_width = rect.width()
        min_item_width = 400  # Minimum width needed for a fragrance card
        
        # Calculate how many items can fit in a row
        items_per_row = max(1, int((available_width + spacing) / (min_item_width + spacing)))
        
        # Calculate the actual width for each item to fill the space nicely
        if items_per_row > 1:
            target_width = int((available_width - (items_per_row - 1) * spacing) / items_per_row)
        else:
            target_width = min(min_item_width, available_width)
        
        # Ensure minimum width
        target_width = max(target_width, min_item_width)
        
        # Layout items
        item_count = 0
        for item in self._items:
            widget = item.widget()
            if widget:
                item_count += 1
                
                # Check if this item would extend beyond available width
                next_x = x + target_width + spacing
                if next_x - spacing > rect.right() and line_height > 0:
                    # Move to the next row
                    x = rect.x()
                    y = y + line_height + spacing
                    next_x = x + target_width + spacing
                    line_height = 0
                
                # Set the item's geometry
                if not test_only:
                    item_rect = QRect(QPoint(x, y), QSize(target_width, item.sizeHint().height()))
                    item.setGeometry(item_rect)
                
                # Update position and line height
                x = next_x
                line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()


class CollectionView(QWidget):
    """
    Widget that displays the collection of fragrances
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._setup_ui()
        
        # Connect to collection updates
        collection_manager.collection_updated.connect(self._update_collection)
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._update_styling)
        
        # Initial load
        self._update_collection()
        
        # Initial styling
        self._update_styling()
    
    def _setup_ui(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Header section
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)  # Add some bottom margin
        
        # Collection stats label on the left
        self._stats_label = QLabel("Fragrance Collection")
        self._stats_label.setObjectName("collectionHeader")
        header_layout.addWidget(self._stats_label, 4)  # Give more weight to label
        header_layout.addStretch(10)
        
        # Add fragrance button on the right
        self._add_button = QPushButton("Add Fragrance")
        self._add_button.setObjectName("copyButton")
        self._add_button.clicked.connect(self._add_fragrance)
        header_layout.addWidget(self._add_button)
        header_layout.addStretch(1)
        
        main_layout.addLayout(header_layout)
        
        # Collection container (scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Container widget for flow layout
        self._collection_container = QWidget()
        
        # Use a flow layout for responsive item display
        self._collection_layout = FlowLayout(self._collection_container, 10, 10)
        
        scroll_area.setWidget(self._collection_container)
        main_layout.addWidget(scroll_area)
        
        # Create empty state label but don't add it yet
        self._empty_label = QLabel("No fragrances found. Add a fragrance to get started!")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setObjectName("emptyLabel")
    
    @Slot()
    def _update_styling(self):
        """Update styling based on the current theme"""
        current_theme = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme]
        
        # Get colors from theme
        text_color = theme_data["palette"]["foreground"].name()
        primary_color = theme_data["palette"]["primary"].name()
        bg_color = theme_data["palette"]["background"].name()
        bg2_color = theme_data["palette"]["background_alt"].name()
        
        # Update styles
        self._stats_label.setStyleSheet(f"""
            #collectionHeader {{
                font-size: 18px;
                font-weight: bold;
                color: {text_color};
            }}
        """)
        
        self._empty_label.setStyleSheet(f"""
            #emptyLabel {{
                font-size: 14px;
                color: {text_color};
                padding: 40px;
            }}
        """)
        
        # Style the Add Fragrance button
        self._add_button.setStyleSheet(f"""
            QPushButton#copyButton {{
                background-color: {primary_color};
                color: white;
                border: 1px solid {primary_color};
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 3px;
            }}
            
            QPushButton#copyButton:hover {{
                background-color: {bg2_color};
                color: {text_color};
                border: 1px solid {primary_color};
            }}
        """)
    
    @Slot()
    def _update_collection(self):
        """Update the displayed collection"""
        # Clear existing items
        while self._collection_layout.count():
            item = self._collection_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get fragrances from the collection manager
        fragrances = collection_manager.get_fragrances()
        
        # Update stats
        stats = collection_manager.get_collection_stats()
        self._stats_label.setText(f"Fragrance Collection ({stats.get('total_fragrances', 0)} fragrances)")
        
        # Display no fragrances message if collection is empty
        if not fragrances:
            self._collection_layout.addWidget(self._empty_label)
            return
        
        # Add fragrances to view
        for fragrance in fragrances:
            fragrance_item = FragranceItem(fragrance)
            
            # Connect signals
            fragrance_item.editClicked.connect(self._edit_fragrance)
            fragrance_item.deleteClicked.connect(self._delete_fragrance)
            fragrance_item.favoriteToggled.connect(self._toggle_favorite)
            
            self._collection_layout.addWidget(fragrance_item)
    
    @Slot()
    def _add_fragrance(self):
        """Show dialog to add a new fragrance"""
        dialog = FragranceDialog(parent=self)
        
        if dialog.exec() == FragranceDialog.Accepted:
            fragrance_data = dialog.get_fragrance_data()
            collection_manager.add_fragrance(fragrance_data)
    
    @Slot(int)
    def _edit_fragrance(self, fragrance_id):
        """Show dialog to edit a fragrance"""
        # Find the fragrance with the given ID
        fragrances = collection_manager.get_all_fragrances()
        fragrance = next((f for f in fragrances if f.id() == fragrance_id), None)
        
        if not fragrance:
            QMessageBox.warning(self, "Error", "Fragrance not found.")
            return
        
        dialog = FragranceDialog(fragrance, parent=self)
        
        if dialog.exec() == FragranceDialog.Accepted:
            fragrance_data = dialog.get_fragrance_data()
            collection_manager.update_fragrance(fragrance_id, fragrance_data)
    
    @Slot(int)
    def _delete_fragrance(self, fragrance_id):
        """Delete a fragrance after confirmation"""
        # Find the fragrance with the given ID
        fragrances = collection_manager.get_all_fragrances()
        fragrance = next((f for f in fragrances if f.id() == fragrance_id), None)
        
        if not fragrance:
            QMessageBox.warning(self, "Error", "Fragrance not found.")
            return
        
        # Confirm deletion
        fragrance_name = fragrance.full_name()
        confirmation = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{fragrance_name}' from your collection?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirmation == QMessageBox.Yes:
            collection_manager.delete_fragrance(fragrance_id)
    
    @Slot()
    def expandAll(self):
        """Expand all fragrance items in the collection"""
        for i in range(self._collection_layout.count()):
            item = self._collection_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, FragranceItem):
                    widget.expandItem()
    
    @Slot()
    def collapseAll(self):
        """Collapse all fragrance items in the collection"""
        for i in range(self._collection_layout.count()):
            item = self._collection_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, FragranceItem):
                    widget.collapseItem()
    
    @Slot(int, bool)
    def _toggle_favorite(self, fragrance_id, is_favorite):
        """Update favorite status in the database"""
        # Find the fragrance with the given ID
        fragrances = collection_manager.get_all_fragrances()
        fragrance = next((f for f in fragrances if f.id() == fragrance_id), None)
        
        if not fragrance:
            QMessageBox.warning(self, "Error", "Fragrance not found.")
            return
        
        # Update the fragrance
        fragrance_data = fragrance.to_dict()
        fragrance_data['is_favorite'] = is_favorite
        collection_manager.update_fragrance(fragrance_id, fragrance_data) 