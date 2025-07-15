from ..utils.data_processing import DataProcessor


class LatexFormatter:
    """Handles LaTeX table generation"""
    
    def __init__(self, config_manager):
        self.config = config_manager
    
    def generate_latex_table(self, df, selected_columns, decimal_places=4):
        """Generate LaTeX table from dataframe and selected columns"""
        display_names = list(selected_columns.values())
        cols = list(selected_columns.keys())
        
        if not cols:
            return "Please select at least one column"
        
        # Find minimum values for each numeric column (except first column)
        min_values = self._calculate_min_values(df, cols)
        
        # Start building LaTeX table
        latex = self._build_table_header(len(cols))
        latex += self._build_table_headers(display_names)
        latex += self._build_table_rows(df, cols, min_values, decimal_places)
        latex += self._build_table_footer()
        
        return latex
    
    def _calculate_min_values(self, df, cols):
        """Calculate minimum values for numeric columns, excluding ignored models"""
        min_values = {}
        
        # Filter dataframe for minimum calculation
        df_for_mins = df.copy()
        if 'model' in df.columns:
            # Filter out ignored models and pattern matches
            df_for_mins = df_for_mins[
                ~df_for_mins['model'].isin(self.config.ignored_models) & 
                ~df_for_mins['model'].apply(
                    lambda x: DataProcessor.matches_ignored_pattern(x, self.config.ignored_in_calculation)
                )
            ]
        
        for col in cols[1:]:  # Skip first column
            if df_for_mins[col].dtype in ['float64', 'int64']:
                min_values[col] = df_for_mins[col].min()
        
        return min_values
    
    def _build_table_header(self, num_cols):
        """Build LaTeX table header with column specification"""
        # Create column specification with extra columns
        col_spec = "c" * (num_cols + len(self.config.extra_columns))
        
        latex = "\\begin{table}[t]\n\\centering\n"
        latex += "\\caption{Your Caption Here}\n"
        latex += f"\\begin{{tabular}}{{{col_spec}}}\n\\hline\n"
        
        return latex
    
    def _build_table_headers(self, display_names):
        """Build table headers with extra columns inserted"""
        headers = display_names.copy()
        
        # Insert extra column headers at specified positions
        for extra_col in self.config.extra_columns:
            position = extra_col['position']
            if position < len(headers):
                headers.insert(position, extra_col['display_name'])
        
        headers_str = " & ".join([f"\\textbf{{{header}}}" for header in headers])
        return f"{headers_str} \\\\\n\\hline\n"
    
    def _build_table_rows(self, df, cols, min_values, decimal_places):
        """Build table data rows with extra columns and formatting"""
        latex_rows = ""
        
        for _, row in df[cols].iterrows():
            row_values = []
            current_pos = 0
            current_model = str(row[cols[0]])  # Get current model name
            
            for i, value in enumerate(row):
                col = cols[i]
                
                # Add any extra columns that should appear before this position
                while any(ec['position'] == current_pos for ec in self.config.extra_columns):
                    extra_col = next(ec for ec in self.config.extra_columns if ec['position'] == current_pos)
                    row_values.append(extra_col['value'])
                    current_pos += 1
                
                # Add the actual column value
                formatted_value = self._format_cell_value(value, col, current_model, min_values, decimal_places, i == 0)
                row_values.append(formatted_value)
                current_pos += 1
            
            # Add any remaining extra columns
            for extra_col in self.config.extra_columns:
                if extra_col['position'] >= current_pos:
                    row_values.append(extra_col['value'])
            
            latex_rows += " & ".join(row_values) + " \\\\\n"
        
        return latex_rows
    
    def _format_cell_value(self, value, col, current_model, min_values, decimal_places, is_first_column):
        """Format individual cell value with appropriate LaTeX formatting"""
        if is_first_column:  # First column (model names)
            return self.config.latex_model_names.get(str(value), str(value))
        elif isinstance(value, (int, float)):
            # Check if there's a custom format for this column
            column_format = self.config.get_column_format(col)
            if column_format:
                try:
                    formatted_value = f"{value:{column_format}}"
                except (ValueError, TypeError):
                    # Fallback to default formatting if custom format fails
                    formatted_value = f"{value:.{decimal_places}f}"
            else:
                formatted_value = f"{value:.{decimal_places}f}"
            
            # Check if current model name matches any patterns
            prefix = ""
            for suffix, pattern_prefix in self.config.model_patterns['suffixes'].items():
                if current_model.endswith(suffix):
                    prefix = pattern_prefix
                    break
            
            # Underline minimum values
            if col in min_values and abs(value - min_values[col]) < 1e-10:
                formatted_value = f"\\underline{{{formatted_value}}}"
            
            return f"${prefix}{formatted_value}$"
        else:
            return str(value)
    
    def _build_table_footer(self):
        """Build LaTeX table footer"""
        return "\\hline\n\\end{tabular}\n\\end{table}"