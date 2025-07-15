import pandas as pd
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QCheckBox, QGridLayout, QScrollArea, QComboBox, QPushButton, QWidget)


class FilterDialog(QDialog):
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Row Filters")
        self.setModal(True)
        self.df = df
        
        # Main layout
        layout = QVBoxLayout()
        
        # Create scrollable area for filters
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        
        # Headers
        scroll_layout.addWidget(QLabel("Enable"), 0, 0)
        scroll_layout.addWidget(QLabel("Column"), 0, 1)
        scroll_layout.addWidget(QLabel("Filter Type"), 0, 2)
        scroll_layout.addWidget(QLabel("Value/Range"), 0, 3)
        
        # Store filter widgets
        self.filters = {}
        current_row = 1
        
        # Process numeric columns
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_columns:
            current_row = self._add_numeric_filter(scroll_layout, col, current_row)
        
        # Process non-numeric columns (categorical/string)
        non_numeric_columns = df.select_dtypes(exclude=['int64', 'float64']).columns
        for col in non_numeric_columns:
            current_row = self._add_categorical_filter(scroll_layout, col, current_row)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Add Clear All and OK buttons
        button_layout = QHBoxLayout()
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self._clear_all_filters)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        
        button_layout.addWidget(clear_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _add_numeric_filter(self, layout, col, row):
        """Add numeric filter widgets for a column"""
        # Enable checkbox
        checkbox = QCheckBox()
        layout.addWidget(checkbox, row, 0)
        
        # Column name
        layout.addWidget(QLabel(col), row, 1)
        
        # Filter type combo box
        filter_type = QComboBox()
        filter_type.addItems(['Range', 'Equal to', 'Greater than', 'Less than'])
        layout.addWidget(filter_type, row, 2)
        
        # Value widget stack
        value_widget = QWidget()
        value_layout = QHBoxLayout(value_widget)
        
        # Create widgets for range inputs
        min_value = QLineEdit()
        max_value = QLineEdit()
        single_value = QLineEdit()
        
        # Set validators for numeric input
        if self.df[col].dtype == 'int64':
            min_val = self.df[col].min()
            max_val = self.df[col].max()
            validator = QIntValidator(min_val, max_val)
        else:
            min_val = float(self.df[col].min())
            max_val = float(self.df[col].max())
            validator = QDoubleValidator(min_val, max_val, 6, None)
        
        min_value.setValidator(validator)
        max_value.setValidator(validator)
        single_value.setValidator(validator)
        
        # Add placeholders
        min_value.setPlaceholderText("Min")
        max_value.setPlaceholderText("Max")
        single_value.setPlaceholderText("Value")
        
        # Initial setup with range widgets
        value_layout.addWidget(min_value)
        value_layout.addWidget(QLabel("to"))
        value_layout.addWidget(max_value)
        single_value.hide()
        
        layout.addWidget(value_widget, row, 3)
        
        # Store widgets for this column
        self.filters[col] = {
            'type': 'numeric',
            'checkbox': checkbox,
            'filter_type': filter_type,
            'min_value': min_value,
            'max_value': max_value,
            'single_value': single_value,
            'value_widget': value_widget,
            'value_layout': value_layout
        }
        
        # Connect filter type change to update value widgets
        filter_type.currentTextChanged.connect(
            lambda text, col=col: self._update_value_widgets(col, text))
        
        return row + 1
    
    def _add_categorical_filter(self, layout, col, row):
        """Add categorical filter widgets for a column"""
        # Enable checkbox
        checkbox = QCheckBox()
        layout.addWidget(checkbox, row, 0)
        
        # Column name
        layout.addWidget(QLabel(col), row, 1)
        
        # Filter type (always 'Equal to' for categorical)
        filter_type_label = QLabel("Equal to")
        layout.addWidget(filter_type_label, row, 2)
        
        # Value combobox
        value_combo = QComboBox()
        unique_values = self.df[col].unique()
        value_combo.addItems([str(v) for v in unique_values])
        layout.addWidget(value_combo, row, 3)
        
        # Store widgets for this column
        self.filters[col] = {
            'type': 'categorical',
            'checkbox': checkbox,
            'value_combo': value_combo
        }
        
        return row + 1
    
    def _update_value_widgets(self, col, filter_type):
        """Update the value widgets based on the selected filter type"""
        widgets = self.filters[col]
        if widgets['type'] != 'numeric':
            return
            
        # Clear the layout
        for i in reversed(range(widgets['value_layout'].count())): 
            widgets['value_layout'].itemAt(i).widget().hide()
        
        # Show appropriate widgets based on filter type
        if filter_type == 'Range':
            widgets['min_value'].show()
            widgets['value_layout'].itemAt(1).widget().show()  # "to" label
            widgets['max_value'].show()
            widgets['single_value'].hide()
        else:
            widgets['min_value'].hide()
            widgets['value_layout'].itemAt(1).widget().hide()  # "to" label
            widgets['max_value'].hide()
            widgets['single_value'].show()
    
    def _clear_all_filters(self):
        """Clear all filter selections"""
        for widgets in self.filters.values():
            widgets['checkbox'].setChecked(False)
            if widgets['type'] == 'numeric':
                widgets['min_value'].clear()
                widgets['max_value'].clear()
                widgets['single_value'].clear()
                widgets['filter_type'].setCurrentIndex(0)
    
    def get_active_filters(self):
        """Return dictionary of active filters with their types and values"""
        active_filters = {}
        for col, widgets in self.filters.items():
            if not widgets['checkbox'].isChecked():
                continue
                
            if widgets['type'] == 'numeric':
                filter_type = widgets['filter_type'].currentText()
                if filter_type == 'Range':
                    min_val = widgets['min_value'].text()
                    max_val = widgets['max_value'].text()
                    if min_val or max_val:  # At least one value provided
                        active_filters[col] = {
                            'type': 'range',
                            'min': float(min_val) if min_val else None,
                            'max': float(max_val) if max_val else None
                        }
                else:
                    value = widgets['single_value'].text()
                    if value:  # Value provided
                        active_filters[col] = {
                            'type': filter_type.lower().replace(' ', '_'),
                            'value': float(value)
                        }
            else:  # categorical
                active_filters[col] = {
                    'type': 'equal_to',
                    'value': widgets['value_combo'].currentText()
                }
        
        return active_filters