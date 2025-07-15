from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QListWidget, QListWidgetItem, QComboBox, QWidget)
from PyQt6.QtCore import Qt


class SortDialog(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sort Settings")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Available columns
        layout.addWidget(QLabel("Available Columns:"))
        self.column_list = QListWidget()
        self.column_list.addItems(columns)
        layout.addWidget(self.column_list)
        
        # Selected sort keys
        layout.addWidget(QLabel("Sort Order (Drag to reorder):"))
        self.sort_list = QListWidget()
        self.sort_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        # Set a fixed height for items to ensure proper layout
        self.sort_list.setFixedHeight(200)
        layout.addWidget(self.sort_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add →")
        remove_button = QPushButton("← Remove")
        add_button.clicked.connect(self._add_sort_key)
        remove_button.clicked.connect(self._remove_sort_key)
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        layout.addLayout(button_layout)
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)
    
    def _add_sort_key(self):
        current_item = self.column_list.currentItem()
        if current_item:
            # Create a widget to hold both the column name and combo box
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(5, 2, 5, 2)
            
            # Add column name label
            label = QLabel(current_item.text())
            container_layout.addWidget(label)
            
            # Add combo box for ascending/descending
            combo = QComboBox()
            combo.addItems(["Ascending", "Descending"])
            container_layout.addWidget(combo)
            
            # Add spacer to push combo box to the right
            container_layout.addStretch()
            
            # Create list item and set its size hint to accommodate the container
            item = QListWidgetItem()
            item.setSizeHint(container.sizeHint())
            
            # Add to sort list
            self.sort_list.addItem(item)
            self.sort_list.setItemWidget(item, container)
            
            # Store the column name with the item
            item.setData(Qt.ItemDataRole.UserRole, current_item.text())
    
    def _remove_sort_key(self):
        current_row = self.sort_list.currentRow()
        if current_row >= 0:
            self.sort_list.takeItem(current_row)
    
    def get_sort_keys(self):
        """Return list of (column, ascending) tuples"""
        sort_keys = []
        for i in range(self.sort_list.count()):
            item = self.sort_list.item(i)
            container = self.sort_list.itemWidget(item)
            combo = container.findChild(QComboBox)
            column = item.data(Qt.ItemDataRole.UserRole)
            ascending = combo.currentText() == "Ascending"
            sort_keys.append((column, ascending))
        return sort_keys