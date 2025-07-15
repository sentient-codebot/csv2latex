import logging
import pandas as pd
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, 
                           QHBoxLayout, QWidget, QFileDialog, QTableWidget, 
                           QTableWidgetItem, QLabel, QLineEdit, QCheckBox, QTextEdit)
from PyQt6.QtCore import Qt

from .dialogs import SortDialog, FilterDialog
from .config import ConfigManager
from .utils import DataProcessor
from .latex import LatexFormatter

logging.basicConfig(level=logging.INFO)


class CSVToLatexConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV to LaTeX Table Converter")
        self.setGeometry(100, 100, 1000, 800)
        
        # Initialize components
        self.config = ConfigManager()
        self.data_processor = DataProcessor()
        self.latex_formatter = LatexFormatter(self.config)
        
        # State variables
        self.active_filters = {}
        self.sort_keys = []
        self.df_columns = []  # Store original column order
        
        self._init_ui()
        
    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Configuration section
        layout.addLayout(self._create_config_layout())
        
        # Top buttons
        layout.addLayout(self._create_button_layout())
        
        # Column selection and mapping
        layout.addLayout(self._create_column_layout())
        
        # Data preview
        layout.addWidget(QLabel("Data Preview:"))
        self.preview_table = QTableWidget()
        layout.addWidget(self.preview_table)
        
        # Decimal places and formatting options
        layout.addLayout(self._create_format_options_layout())
        
        # LaTeX output
        layout.addWidget(QLabel("LaTeX Output:"))
        self.latex_output = QTextEdit()
        self.latex_output.setReadOnly(True)
        self.latex_output.setMinimumHeight(150)
        self.latex_output.setFont(QFont("Courier"))
        layout.addWidget(self.latex_output)
        
        central_widget.setLayout(layout)
    
    def _create_config_layout(self):
        """Create the configuration file selection layout"""
        config_layout = QHBoxLayout()
        
        config_layout.addWidget(QLabel("Configuration:"))
        
        # Current config file label
        self.config_file_label = QLabel(f"Current: {self.config.config_path}")
        config_layout.addWidget(self.config_file_label)
        
        # Load config button
        load_config_button = QPushButton("Load Config File")
        load_config_button.clicked.connect(self._load_config_file)
        config_layout.addWidget(load_config_button)
        
        config_layout.addStretch()
        return config_layout
    
    def _create_button_layout(self):
        """Create the top button layout"""
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
        
        return button_layout
    
    def _create_column_layout(self):
        """Create the column selection and reordering layout"""
        column_layout = QHBoxLayout()
        
        # Column checkboxes and names
        self.column_widget = QTableWidget()
        self.column_widget.setColumnCount(4)
        self.column_widget.setHorizontalHeaderLabels(["Include", "Original Name", "Display Name", "Underline Min"])
        column_layout.addWidget(self.column_widget)
        
        # Reorder buttons
        reorder_layout = QVBoxLayout()
        move_up_button = QPushButton("↑ Move Up")
        move_down_button = QPushButton("↓ Move Down")
        move_up_button.clicked.connect(self._move_column_up)
        move_down_button.clicked.connect(self._move_column_down)
        
        reorder_layout.addWidget(move_up_button)
        reorder_layout.addWidget(move_down_button)
        reorder_layout.addStretch()
        
        column_layout.addLayout(reorder_layout)
        return column_layout
    
    def _create_format_options_layout(self):
        """Create the formatting options layout"""
        format_layout = QHBoxLayout()
        
        # Decimal places
        format_layout.addWidget(QLabel("Decimal Places:"))
        self.decimal_places_input = QLineEdit("4")
        format_layout.addWidget(self.decimal_places_input)
        
        format_layout.addWidget(QLabel("  (Underline settings are per-column)"))  # Info text
        
        format_layout.addStretch()
        return format_layout
    
    def _move_column_up(self):
        current_row = self.column_widget.currentRow()
        if current_row > 0:
            self._swap_rows(current_row, current_row - 1)
            self.column_widget.setCurrentCell(current_row - 1, self.column_widget.currentColumn())
            self._update_preview()
    
    def _move_column_down(self):
        current_row = self.column_widget.currentRow()
        if current_row < self.column_widget.rowCount() - 1:
            self._swap_rows(current_row, current_row + 1)
            self.column_widget.setCurrentCell(current_row + 1, self.column_widget.currentColumn())
            self._update_preview()
    
    def _swap_rows(self, row1, row2):
        """Swap two rows in the column widget"""
        row1_data = self._get_row_data(row1)
        row2_data = self._get_row_data(row2)
        
        self._set_row_data(row1, row2_data)
        self._set_row_data(row2, row1_data)
    
    def _get_row_data(self, row):
        """Get all data from a row"""
        return {
            'checkbox': self.column_widget.cellWidget(row, 0).isChecked(),
            'original_name': self.column_widget.item(row, 1).text(),
            'display_name': self.column_widget.cellWidget(row, 2).text(),
            'underline': self.column_widget.cellWidget(row, 3).isChecked()
        }
    
    def _set_row_data(self, row, data):
        """Set all data for a row"""
        # Set include checkbox
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
        
        # Set underline checkbox
        underline_checkbox = QCheckBox()
        underline_checkbox.setChecked(data['underline'])
        underline_checkbox.stateChanged.connect(self._on_column_underline_changed)
        self.column_widget.setCellWidget(row, 3, underline_checkbox)
    
    def _on_column_underline_changed(self):
        """Handle per-column underline checkbox changes"""
        # Regenerate LaTeX if we have data
        if hasattr(self, 'combined_df'):
            self._convert_to_latex()
    
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
        
        # Apply initial data processing
        self.combined_df = self.data_processor.filter_ignored_models(
            self.combined_df, self.config.ignored_models)
        self.combined_df = self.data_processor.sort_by_model_order(
            self.combined_df, self.config.get_model_order)
        
        logging.info(f"Filtered out ignored models: {self.config.ignored_models}")
        
        self.df_columns = self.combined_df.columns.tolist()
        self._setup_column_widget()
        self._update_preview()
    
    def _setup_column_widget(self):
        """Setup the column selection widget with loaded data"""
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
            display_name = QLineEdit(self.config.get_pretty_column_name(col))
            display_name.textChanged.connect(self._update_preview)
            self.column_widget.setCellWidget(i, 2, display_name)
            
            # Underline minimum values checkbox
            underline_checkbox = QCheckBox()
            underline_checkbox.setChecked(self.config.get_column_underline(col))
            underline_checkbox.stateChanged.connect(self._on_column_underline_changed)
            self.column_widget.setCellWidget(i, 3, underline_checkbox)
        
        self.column_widget.resizeColumnsToContents()
    
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
    
    def _update_preview(self):
        if not hasattr(self, 'combined_df'):
            return
        
        # Get filtered and sorted data
        df = self.data_processor.apply_filters(self.combined_df, self.active_filters)
        df = self.data_processor.apply_sort(df, self.sort_keys)
        
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
                col = cols[j]
                if isinstance(value, (int, float)):
                    # Check if there's a custom format for this column
                    column_format = self.config.get_column_format(col)
                    if column_format:
                        try:
                            # Handle integer formats by converting float to int
                            if column_format in ['d', 'b', 'o', 'x', 'X'] or column_format.endswith('d'):
                                formatted_value = f"{int(value):{column_format}}"
                            else:
                                formatted_value = f"{value:{column_format}}"
                        except (ValueError, TypeError) as e:
                            # Fallback to default formatting if custom format fails
                            formatted_value = f"{value:.{decimal_places}f}"
                    else:
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
        df = self.data_processor.apply_filters(self.combined_df, self.active_filters)
        df = self.data_processor.apply_sort(df, self.sort_keys)
        
        # Get selected columns
        selected_columns = self._get_selected_columns()
        
        # Generate LaTeX with per-column underline settings
        column_underline_settings = self._get_column_underline_settings()
        latex = self.latex_formatter.generate_latex_table(df, selected_columns, decimal_places, column_underline_settings)
        self.latex_output.setPlainText(latex)
    
    def _get_column_underline_settings(self):
        """Get dictionary of column underline settings from GUI"""
        underline_settings = {}
        for i in range(self.column_widget.rowCount()):
            col = self.column_widget.item(i, 1).text()
            underline_checkbox = self.column_widget.cellWidget(i, 3)
            if underline_checkbox:
                underline_settings[col] = underline_checkbox.isChecked()
        return underline_settings
    
    def _load_config_file(self):
        """Load a new configuration file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Configuration File",
            "",
            "YAML Files (*.yaml *.yml);;All Files (*)"
        )
        
        if file_path:
            # Load the new configuration
            self.config.load_config_file(file_path)
            
            # Update the formatter with the new config
            self.latex_formatter = LatexFormatter(self.config)
            
            # Update the UI label
            self.config_file_label.setText(f"Current: {self.config.config_path}")
            
            # If we have loaded data, update the column names and preview
            if hasattr(self, 'combined_df'):
                self._update_column_display_names()
                self._update_preview()
    
    def _update_column_display_names(self):
        """Update the display names and underline settings in the column widget based on new config"""
        for i in range(self.column_widget.rowCount()):
            original_name = self.column_widget.item(i, 1).text()
            
            # Update display name
            display_name_widget = self.column_widget.cellWidget(i, 2)
            if display_name_widget:
                display_name_widget.setText(self.config.get_pretty_column_name(original_name))
            
            # Update underline checkbox
            underline_widget = self.column_widget.cellWidget(i, 3)
            if underline_widget:
                underline_widget.setChecked(self.config.get_column_underline(original_name))