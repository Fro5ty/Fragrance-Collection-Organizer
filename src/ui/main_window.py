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

import os, sys
from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QStatusBar, QLabel, QMessageBox, QMenu, QApplication, QToolButton
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, Slot, QSize

from src.models import collection_manager
from src.ui.components import FilterPanel, CollectionView
from src.ui.dialogs import OverviewDialog
from src.utils import theme_manager

class MainWindow(QMainWindow):
    """
    Main application window
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Fragrance Organizer")
        self.setMinimumSize(1370, 900)  # Adjusted minimum size for better card display
        
        # Track filter panel state
        self._filter_panel_visible = True
        self._saved_filter_width = 0
        
        self._setup_ui()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_connections()
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Splitter for filter panel and collection view
        self._splitter = QSplitter(Qt.Horizontal)
        self._splitter.setHandleWidth(1)
        
        # Filter panel (left side)
        self._filter_panel = FilterPanel()
        self._filter_container = QWidget()
        filter_layout = QVBoxLayout(self._filter_container)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        filter_layout.addWidget(self._filter_panel)
        
        # Toggle button for filter panel
        self._toggle_filter_btn = QToolButton()
        self._toggle_filter_btn.setText("◀")  # Left arrow to hide panel
        self._toggle_filter_btn.setToolTip("Hide Filter Panel")
        self._toggle_filter_btn.setFixedSize(10, 80)
        self._toggle_filter_btn.clicked.connect(self._toggle_filter_panel)
        self._toggle_filter_btn.setObjectName("toggleFilterButton")
        
        # Collection view (right side)
        self._collection_view = CollectionView()
        collection_container = QWidget()
        collection_layout = QVBoxLayout(collection_container)
        collection_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add toggle button to left side of collection view
        toggle_layout = QHBoxLayout()
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.addWidget(self._toggle_filter_btn)
        toggle_layout.addWidget(self._collection_view)
        collection_layout.addLayout(toggle_layout)
        
        # Add widgets to splitter
        self._splitter.addWidget(self._filter_container)
        self._splitter.addWidget(collection_container)
        
        # Calculate sizes
        total_width = 1000
        filter_width = int(total_width * 0.23)  # 23% for filter panel
        collection_width = total_width - filter_width
        
        # Set initial sizes
        self._splitter.setSizes([filter_width, collection_width])
        self._saved_filter_width = filter_width  # Save initial width for restoration
        
        main_layout.addWidget(self._splitter)
        
        # Connect to theme changes to update the splitter
        theme_manager.theme_changed.connect(self._update_splitter_style)
        
        # Initial update of splitter style
        self._update_splitter_style()
    
    def _setup_toolbar(self):
        """Set up the application toolbar"""
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # Add actions
        refresh_action = QAction("Refresh Collection", self)
        refresh_action.setStatusTip("Refresh the collection display")
        refresh_action.triggered.connect(self._refresh_collection)
        
        add_action = QAction("Add Fragrance", self)
        add_action.setStatusTip("Add a new fragrance to your collection")
        add_action.triggered.connect(self._collection_view._add_fragrance)
        
        overview_action = QAction("Collection Overview", self)
        overview_action.setStatusTip("Show collection statistics and overview")
        overview_action.triggered.connect(self._show_overview)
        
        # Filter panel toggle in toolbar
        toggle_filter_action = QAction("Toggle Filter Panel", self)
        toggle_filter_action.setStatusTip("Show/Hide the filter panel")
        toggle_filter_action.triggered.connect(self._toggle_filter_panel)
        
        # Theme menu
        theme_menu = QMenu("Theme", self)
        theme_menu.setStatusTip("Change application theme")
        
        # Add theme options
        for theme_id, theme_name in theme_manager.get_theme_names():
            theme_action = QAction(theme_name, self)
            theme_action.setStatusTip(f"Switch to {theme_name} theme")
            theme_action.setData(theme_id)
            theme_action.triggered.connect(self._change_theme)
            theme_menu.addAction(theme_action)
        
        # Add actions to toolbar
        self.toolbar.addAction(refresh_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(add_action)
        self.toolbar.addAction(overview_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(toggle_filter_action)
        self.toolbar.addSeparator()
        
        # Add theme menu to toolbar
        theme_button = QToolButton()
        theme_button.setText("Themes")
        theme_button.setMenu(theme_menu)
        theme_button.setPopupMode(QToolButton.InstantPopup)  # Makes entire button clickable
        theme_button.setStatusTip("Change application theme")
        theme_button.setStyleSheet("""
            QToolButton {
                padding-right: 10px;
            }
            QToolButton::menu-indicator {
                subcontrol-position: right center;
                subcontrol-origin: padding;
                padding-left: 4px;
            }
        """)
        self.toolbar.addWidget(theme_button)
    
    def _setup_statusbar(self):
        """Set up the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_message = QLabel("Ready")
        self.status_bar.addWidget(self.status_message, 1)
        
        # Collection stats
        self.collection_stats = QLabel()
        self._update_status_stats()
        self.status_bar.addPermanentWidget(self.collection_stats)
        
        # Current theme
        self.theme_label = QLabel()
        self._update_theme_label()
        self.status_bar.addPermanentWidget(self.theme_label)
        
        # Connect to collection updates
        collection_manager.collection_updated.connect(self._update_status_stats)
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._update_theme_label)
    
    def _setup_connections(self):
        """Set up signal-slot connections"""
        # Connect filter panel signals to collection manager
        self._filter_panel.searchApplied.connect(collection_manager.set_search_term)
        self._filter_panel.filtersApplied.connect(collection_manager.set_filters)
        
        # Connect expand/collapse signals
        self._filter_panel.expandAllClicked.connect(self._collection_view.expandAll)
        self._filter_panel.collapseAllClicked.connect(self._collection_view.collapseAll)
    
    @Slot()
    def _toggle_filter_panel(self):
        """Toggle the visibility of the filter panel"""
        if self._filter_panel_visible:
            # Hide the filter panel
            self._saved_filter_width = self._splitter.sizes()[0]  # Save current width
            self._splitter.setSizes([0, self._splitter.sizes()[1] + self._saved_filter_width])
            self._toggle_filter_btn.setText("▶")  # Right arrow to show panel
            self._toggle_filter_btn.setToolTip("Show Filter Panel")
            self.status_message.setText("Filter panel hidden")
        else:
            # Show the filter panel
            self._splitter.setSizes([self._saved_filter_width, self._splitter.sizes()[1] - self._saved_filter_width])
            self._toggle_filter_btn.setText("◀")  # Left arrow to hide panel
            self._toggle_filter_btn.setToolTip("Hide Filter Panel")
            self.status_message.setText("Filter panel shown")
        
        self._filter_panel_visible = not self._filter_panel_visible
        
        # Update the toggle button style based on the current theme
        self._update_toggle_button_style()
    
    @Slot()
    def _update_toggle_button_style(self):
        """Update the toggle button style based on the current theme"""
        current_theme_id = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme_id]
        
        primary_color = theme_data["palette"]["primary"].name()
        text_color = theme_data["palette"]["foreground"].name()
        bg_color = theme_data["palette"]["background_alt"].name()
        
        # Set button style
        self._toggle_filter_btn.setStyleSheet(f"""
            QToolButton#toggleFilterButton {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {primary_color};
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
                border-left: none;
                font-weight: bold;
                font-size: 12px;
            }}
            
            QToolButton#toggleFilterButton:hover {{
                background-color: {primary_color};
                color: white;
            }}
        """)
    
    @Slot()
    def _refresh_collection(self):
        """Refresh the collection data"""
        collection_manager.refresh_collection()
        self.status_message.setText("Collection refreshed")
    
    @Slot()
    def _update_status_stats(self):
        """Update the collection stats in the status bar"""
        stats = collection_manager.get_collection_stats()
        total = stats.get('total_fragrances', 0)
        house_count = stats.get('house_count', 0)
        
        self.collection_stats.setText(f" Total fragrances: {total} | Houses: {house_count} ")
    
    @Slot()
    def _update_theme_label(self):
        """Update the theme label in the status bar"""
        current_theme_id = theme_manager.get_current_theme()
        theme_names = dict(theme_manager.get_theme_names())
        theme_name = theme_names.get(current_theme_id, "Unknown")
        
        self.theme_label.setText(f" Theme: {theme_name} ")
    
    @Slot()
    def _change_theme(self):
        """Change the application theme"""
        action = self.sender()
        theme_id = action.data()
        
        # Apply the new theme
        app = QApplication.instance()
        theme_manager.apply_theme(app, theme_id)
        
        # Update status message
        theme_names = dict(theme_manager.get_theme_names())
        theme_name = theme_names.get(theme_id, "Unknown")
        self.status_message.setText(f"Theme changed to {theme_name}")
        
        # Update toggle button style after theme change
        self._update_toggle_button_style()
    
    @Slot()
    def _update_splitter_style(self):
        """Update the splitter handle style based on the current theme"""
        current_theme_id = theme_manager.get_current_theme()
        theme_data = theme_manager._themes[current_theme_id]
        bg_color = theme_data["palette"]["background_alt"].name()
        
        # Set splitter style
        style = f"""
            QSplitter::handle {{
                background-color: {bg_color};
            }}
        """
        
        # Find all splitters and update their style
        for splitter in self.findChildren(QSplitter):
            splitter.setStyleSheet(style)
        
        # Also update the toggle button style
        self._update_toggle_button_style()
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.accept() 

    @Slot()
    def _show_overview(self):
        """Show the collection overview dialog"""
        dialog = OverviewDialog()
        dialog.exec() 