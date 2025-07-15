
# Author: sentient-codebot
# Program Name: csv2latex Converter
# Date: Nov 22 2024
# Internal Version: v1.7
"""
This script provides a GUI application for converting CSV files to LaTeX tables using PyQt6.
It includes functionalities for loading CSV files, setting filters, sorting data, and customizing column mappings.

To use the application:
run `python main.py` in the terminal.
"""
import sys
import pandas as pd
from PyQt6.QtGui import QIntValidator, QDoubleValidator, QFont
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QHBoxLayout, QWidget, QFileDialog, QTableWidget, 
                           QTableWidgetItem, QLabel, QLineEdit, QDialog,
                           QCheckBox, QGridLayout, QScrollArea, QComboBox,
                           QListWidget, QListWidgetItem, QTextEdit)
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
            # Enable checkbox
            checkbox = QCheckBox()
            scroll_layout.addWidget(checkbox, current_row, 0)
            
            # Column name
            scroll_layout.addWidget(QLabel(col), current_row, 1)
            
            # Filter type combo box
            filter_type = QComboBox()
            filter_type.addItems(['Range', 'Equal to', 'Greater than', 'Less than'])
            scroll_layout.addWidget(filter_type, current_row, 2)
            
            # Value widget stack
            value_widget = QWidget()
            value_layout = QHBoxLayout(value_widget)
            
            # Create widgets for range inputs
            min_value = QLineEdit()
            max_value = QLineEdit()
            single_value = QLineEdit()
            
            # Set validators for numeric input
            if df[col].dtype == 'int64':
                min_val = df[col].min()
                max_val = df[col].max()
                validator = QIntValidator(min_val, max_val)
            else:
                min_val = float(df[col].min())
                max_val = float(df[col].max())
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
            
            scroll_layout.addWidget(value_widget, current_row, 3)
            
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
            
            current_row += 1
        
        # Process non-numeric columns (categorical/string)
        non_numeric_columns = df.select_dtypes(exclude=['int64', 'float64']).columns
        for col in non_numeric_columns:
            # Enable checkbox
            checkbox = QCheckBox()
            scroll_layout.addWidget(checkbox, current_row, 0)
            
            # Column name
            scroll_layout.addWidget(QLabel(col), current_row, 1)
            
            # Filter type (always 'Equal to' for categorical)
            filter_type_label = QLabel("Equal to")
            scroll_layout.addWidget(filter_type_label, current_row, 2)
            
            # Value combobox
            value_combo = QComboBox()
            unique_values = df[col].unique()
            value_combo.addItems([str(v) for v in unique_values])
            scroll_layout.addWidget(value_combo, current_row, 3)
            
            # Store widgets for this column
            self.filters[col] = {
                'type': 'categorical',
                'checkbox': checkbox,
                'value_combo': value_combo
            }
            
            current_row += 1
        
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

class CSVToLatexConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV to LaTeX Table Converter")
        self.setGeometry(100, 100, 1000, 800)
        
        self.column_mappings = {}
        self.active_filters = {}
        self.sort_keys = []
        self.df_columns = []  # Store original column order
        
        self._init_ui()
        
    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Top buttons
        button_layout = QHBoxLayout()
        load_button = QPushButton("Load CSV Files")
        filter_button = QPushButton("Set Filters")
        sort_button = QPushButton("Set Sort Order")
        convert_button = QPushButton("Convert to LaTeX")
        
        load_button.clicked.connect(self._load_csv_files)
        filter_button.clicked.connect(self._set_filters)
        sort_button.clicked.connect(self._set_sort_order)
        convert_button.clicked.connect(self._convert_to_latex)
        
        button_layout.addWidget(load_button)
        button_layout.addWidget(filter_button)
        button_layout.addWidget(sort_button)
        button_layout.addWidget(convert_button)
        layout.addLayout(button_layout)
        
        # Column selection and mapping
        column_layout = QHBoxLayout()
        
        # Column checkboxes and names
        self.column_widget = QTableWidget()
        self.column_widget.setColumnCount(3)
        self.column_widget.setHorizontalHeaderLabels(["Include", "Original Name", "Display Name"])
        column_layout.addWidget(self.column_widget)
        
        # Add the reorder buttons
        reorder_layout = QVBoxLayout()
        move_up_button = QPushButton("↑ Move Up")
        move_down_button = QPushButton("↓ Move Down")
        move_up_button.clicked.connect(self._move_column_up)
        move_down_button.clicked.connect(self._move_column_down)
        
        reorder_layout.addWidget(move_up_button)
        reorder_layout.addWidget(move_down_button)
        reorder_layout.addStretch()
        
        column_layout.addLayout(reorder_layout)
        layout.addLayout(column_layout)
        
        # Data preview
        layout.addWidget(QLabel("Data Preview:"))
        self.preview_table = QTableWidget()
        layout.addWidget(self.preview_table)
        
        # Decimal places configuration
        decimal_layout = QHBoxLayout()
        decimal_layout.addWidget(QLabel("Decimal Places:"))
        self.decimal_places_input = QLineEdit("4")
        decimal_layout.addWidget(self.decimal_places_input)
        layout.addLayout(decimal_layout)
        
        # LaTeX output
        layout.addWidget(QLabel("LaTeX Output:"))
        self.latex_output = QTextEdit()
        self.latex_output.setReadOnly(True)
        self.latex_output.setMinimumHeight(150)  # Make it taller
        self.latex_output.setFont(QFont("Courier"))  # Use monospace font
        layout.addWidget(self.latex_output)
        
        central_widget.setLayout(layout)
    
    def _move_column_up(self):
        current_row = self.column_widget.currentRow()
        if current_row > 0:
            # Save the states of both rows
            row_above = self._get_row_data(current_row - 1)
            current_row_data = self._get_row_data(current_row)
            
            # Swap the rows
            self._set_row_data(current_row - 1, current_row_data)
            self._set_row_data(current_row, row_above)
            
            # Update selection
            self.column_widget.setCurrentCell(current_row - 1, self.column_widget.currentColumn())
            self._update_preview()
    
    def _move_column_down(self):
        current_row = self.column_widget.currentRow()
        if current_row < self.column_widget.rowCount() - 1:
            # Save the states of both rows
            row_below = self._get_row_data(current_row + 1)
            current_row_data = self._get_row_data(current_row)
            
            # Swap the rows
            self._set_row_data(current_row + 1, current_row_data)
            self._set_row_data(current_row, row_below)
            
            # Update selection
            self.column_widget.setCurrentCell(current_row + 1, self.column_widget.currentColumn())
            self._update_preview()
    
    def _get_row_data(self, row):
        """Get all data from a row"""
        return {
            'checkbox': self.column_widget.cellWidget(row, 0).isChecked(),
            'original_name': self.column_widget.item(row, 1).text(),
            'display_name': self.column_widget.cellWidget(row, 2).text()
        }
    
    def _set_row_data(self, row, data):
        """Set all data for a row"""
        # Set checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(data['checkbox'])
        checkbox.stateChanged.connect(self._update_preview)
        self.column_widget.setCellWidget(row, 0, checkbox)
        
        # Set original name
        orig_name_item = QTableWidgetItem(data['original_name'])
        orig_name_item.setFlags(orig_name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.column_widget.setItem(row, 1, orig_name_item)
        
        # Set display name
        display_name = QLineEdit(data['display_name'])
        display_name.textChanged.connect(self._update_preview)
        self.column_widget.setCellWidget(row, 2, display_name)
    
    def _prettify_column_name(self, col_name):
        """Convert column names like 'model_name' to 'Model Name'"""
        # Remove prefixes like 'data_', 'model_', 'result_'
        for prefix in ['data_', 'model_', 'result_']:
            if col_name.startswith(prefix):
                col_name = col_name[len(prefix):]
        
        # Split by underscore and capitalize
        words = col_name.split('_')
        return ' '.join(word.capitalize() for word in words)
    
    def _load_csv_files(self):
        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "Select CSV Files",
            "",
            "CSV Files (*.csv)"
        )
        
        if not file_names:
            return
        
        # Load all dataframes and concatenate
        dfs = [pd.read_csv(f) for f in file_names]
        self.combined_df = pd.concat(dfs, axis=0, ignore_index=True)
        self.df_columns = self.combined_df.columns.tolist()  # Store original column order
        
        # Update column selection table
        self.column_widget.setRowCount(len(self.df_columns))
        for i, col in enumerate(self.df_columns):
            # Include checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self._update_preview)
            self.column_widget.setCellWidget(i, 0, checkbox)
            
            # Original name
            orig_name_item = QTableWidgetItem(col)
            orig_name_item.setFlags(orig_name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.column_widget.setItem(i, 1, orig_name_item)
            
            # Display name
            display_name = QLineEdit(self._prettify_column_name(col))
            display_name.textChanged.connect(self._update_preview)
            self.column_widget.setCellWidget(i, 2, display_name)
        
        self.column_widget.resizeColumnsToContents()
        self._update_preview()
    
    def _get_selected_columns(self):
        """Get dictionary of selected columns and their display names"""
        selected = {}
        for i in range(self.column_widget.rowCount()):
            checkbox = self.column_widget.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                col = self.column_widget.item(i, 1).text()
                display_name = self.column_widget.cellWidget(i, 2).text()
                selected[col] = display_name
        return selected
    
    def _set_filters(self):
        if not hasattr(self, 'combined_df'):
            return
        
        dialog = FilterDialog(self.combined_df)
        if dialog.exec():
            self.active_filters = dialog.get_active_filters()
            self._update_preview()
    
    def _set_sort_order(self):
        if not hasattr(self, 'combined_df'):
            return
        
        dialog = SortDialog(list(self.combined_df.columns))
        if dialog.exec():
            self.sort_keys = dialog.get_sort_keys()
            self._update_preview()
    
    def _apply_filters(self, df):
        """Apply active filters to dataframe with support for numeric ranges"""
        if not self.active_filters:
            return df
        
        mask = pd.Series(True, index=df.index)
        
        for col, filter_info in self.active_filters.items():
            filter_type = filter_info['type']
            
            if filter_type == 'range':
                min_val = filter_info['min']
                max_val = filter_info['max']
                
                if min_val is not None:
                    mask &= (df[col] >= min_val)
                if max_val is not None:
                    mask &= (df[col] <= max_val)
                    
            elif filter_type == 'equal_to':
                if isinstance(filter_info['value'], (int, float)):
                    mask &= (df[col] == filter_info['value'])
                else:
                    mask &= (df[col].astype(str) == str(filter_info['value']))
                    
            elif filter_type == 'greater_than':
                mask &= (df[col] > filter_info['value'])
                
            elif filter_type == 'less_than':
                mask &= (df[col] < filter_info['value'])
        
        return df[mask]
    
    def _apply_sort(self, df):
        """Apply sort keys to dataframe"""
        if not self.sort_keys:
            return df
        
        by = [col for col, _ in self.sort_keys]
        ascending = [asc for _, asc in self.sort_keys]
        return df.sort_values(by=by, ascending=ascending)
    
    def _update_preview(self):
        if not hasattr(self, 'combined_df'):
            return
        
        # Get filtered and sorted data
        df = self._apply_filters(self.combined_df)
        df = self._apply_sort(df)
        
        # Get selected columns and their display names
        selected_columns = self._get_selected_columns()
        cols = list(selected_columns.keys())
        display_names = list(selected_columns.values())
        
        # Update preview table structure
        self.preview_table.setRowCount(len(df))
        self.preview_table.setColumnCount(len(cols))
        self.preview_table.setHorizontalHeaderLabels(display_names)
        
        # Fill data
        try:
            decimal_places = int(self.decimal_places_input.text())
        except ValueError:
            decimal_places = 4
            
        for i, (_, row) in enumerate(df[cols].iterrows()):
            for j, value in enumerate(row):
                if isinstance(value, float):
                    formatted_value = f"{value:.{decimal_places}f}"
                else:
                    formatted_value = str(value)
                item = QTableWidgetItem(formatted_value)
                self.preview_table.setItem(i, j, item)
        
        self.preview_table.resizeColumnsToContents()
    
    def _convert_to_latex(self):
        if not hasattr(self, 'combined_df'):
            return
        
        try:
            decimal_places = int(self.decimal_places_input.text())
        except ValueError:
            decimal_places = 4
        
        # Get filtered and sorted data
        df = self._apply_filters(self.combined_df)
        df = self._apply_sort(df)
        
        # Get selected columns
        selected_columns = self._get_selected_columns()
        display_names = list(selected_columns.values())
        cols = list(selected_columns.keys())
        
        if not cols:  # No columns selected
            self.latex_output.setPlainText("Please select at least one column")
            return
        
        # Start building LaTeX table
        latex = "\\begin{table}[t]\n\\centering\n"
        latex += "\\caption{Your Caption Here}\n"
        
        # Create column specification
        col_spec = "c" * len(cols)
        latex += f"\\begin{{tabular}}{{{col_spec}}}\n\\hline\n"
        
        # Add headers
        headers = " & ".join([f"\\textbf{{{header}}}" for header in display_names])
        latex += f"{headers} \\\\\n\\hline\n"
        
        # Add data rows
        for _, row in df[cols].iterrows():
            row_values = []
            for value in row:
                if isinstance(value, float):
                    formatted_value = f"{value:.{decimal_places}f}"
                else:
                    formatted_value = str(value)
                row_values.append(formatted_value)
            latex += " & ".join(row_values) + " \\\\\n"
        
        # Close table
        latex += "\\hline\n\\end{tabular}\n\\end{table}"
        
        self.latex_output.setPlainText(latex)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVToLatexConverter()
    window.show()
    sys.exit(app.exec())