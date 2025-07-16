import yaml
import logging
import os


class ConfigManager:
    """Manages loading and accessing configuration from YAML file"""
    
    def __init__(self, config_path='table_config.yaml'):
        self.config_path = config_path
        self._default_config = self._load_default_config()
        self._config = self._load_config()
    
    def load_config_file(self, new_config_path):
        """Load a new configuration file and update the current config"""
        self.config_path = new_config_path
        self._config = self._load_config()
        logging.info(f"Loaded new configuration file: {new_config_path}")
    
    def _load_default_config(self):
        """Load default configuration from default_config.yaml"""
        # Look for default_config.yaml in the project root
        default_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'default_config.yaml')
        try:
            with open(default_config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.warning(f"Default configuration file {default_config_path} not found. Using hardcoded defaults.")
            return {
                'default_decimal_places': 3,
                'table_style': 'hline',
                'underline_min_values': False,
                'column_underline': {'default': False},
                'column_formats': {},
                'display_names': {},
                'model_order': {},
                'latex_model_names': {},
                'ignored_models': [],
                'ignored_models_in_calculation': [],
                'model_patterns': {'suffixes': {}},
                'row_sorting': {'columns': [], 'sort_orders': {}},
                'value_replacements': {},
                'row_filtering': {'exclude_values': {}, 'exclude_from_calculations': {}},
                'pattern_formatting': {},
                'extra_columns': []
            }
    
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.warning(f"Configuration file {self.config_path} not found. Using defaults.")
            return {}
    
    def _get_config_value(self, key, default_key=None):
        """Get configuration value with fallback to defaults"""
        if default_key is None:
            default_key = key
        return self._config.get(key, self._default_config.get(default_key, {}))
    
    @property
    def column_mappings(self):
        """Get column name mappings"""
        return self._get_config_value('display_names')
    
    @property
    def latex_model_names(self):
        """Get LaTeX model name mappings"""
        return self._get_config_value('latex_model_names')
    
    @property
    def model_order(self):
        """Get model order configuration"""
        return self._get_config_value('model_order')
    
    @property
    def ignored_models(self):
        """Get list of models to ignore"""
        return set(self._get_config_value('ignored_models'))
    
    @property
    def ignored_in_calculation(self):
        """Get list of models to ignore in calculation"""
        return set(self._get_config_value('ignored_models_in_calculation'))
    
    @property
    def extra_columns(self):
        """Get extra columns configuration"""
        return self._get_config_value('extra_columns')
    
    @property
    def model_patterns(self):
        """Get model pattern rules"""
        return self._get_config_value('model_patterns', 'model_patterns')
    
    @property
    def column_formats(self):
        """Get column format specifications"""
        return self._get_config_value('column_formats')
    
    @property
    def underline_min_values(self):
        """Get whether to underline minimum values (legacy global setting)"""
        return self._get_config_value('underline_min_values')
    
    @property
    def column_underline(self):
        """Get per-column underline settings"""
        return self._get_config_value('column_underline')
    
    @property
    def table_style(self):
        """Get table style configuration"""
        return self._get_config_value('table_style')
    
    @property
    def default_decimal_places(self):
        """Get default decimal places"""
        return self._get_config_value('default_decimal_places')
    
    def get_model_order(self, model_name):
        """Get order value for model, with high default for unspecified models"""
        return self.model_order.get(str(model_name), 999999)
    
    def get_pretty_column_name(self, col_name):
        """Convert column names using mapping file or fallback to default prettify"""
        # First check if we have a direct mapping
        if col_name in self.column_mappings:
            return self.column_mappings[col_name]
            
        # Fallback to original prettify logic
        for prefix in ['data_', 'model_', 'result_']:
            if col_name.startswith(prefix):
                col_name = col_name[len(prefix):]
        
        words = col_name.split('_')
        return ' '.join(word.capitalize() for word in words)
    
    def get_column_format(self, col_name):
        """Get format specification for a column"""
        return self.column_formats.get(col_name, None)
    
    def get_column_underline(self, col_name):
        """Get underline setting for a specific column"""
        # Check per-column setting first, then fall back to global setting, then to default
        if col_name in self.column_underline:
            return self.column_underline[col_name]
        elif self.underline_min_values is not None:
            return self.underline_min_values
        else:
            return self.column_underline.get('default', False)
    
    # Generalized configuration properties
    @property
    def row_sorting(self):
        """Get generalized row sorting configuration"""
        return self._get_config_value('row_sorting')
    
    @property
    def value_replacements(self):
        """Get generalized value replacement configuration"""
        return self._get_config_value('value_replacements')
    
    @property
    def row_filtering(self):
        """Get generalized row filtering configuration"""
        return self._get_config_value('row_filtering')
    
    @property
    def pattern_formatting(self):
        """Get generalized pattern formatting configuration"""
        return self._get_config_value('pattern_formatting')
    
    def get_sort_order(self, col_name, value):
        """Get sort order for a value in a specific column"""
        # Check new generalized sorting first
        if self.row_sorting and 'sort_orders' in self.row_sorting:
            sort_orders = self.row_sorting['sort_orders']
            if col_name in sort_orders:
                return sort_orders[col_name].get(str(value), 999999)
        
        # Fallback to legacy model_order for backward compatibility
        if col_name == 'model':
            return self.get_model_order(value)
        
        return 999999
    
    def get_value_replacement(self, col_name, value):
        """Get value replacement for a specific column and value"""
        # Check new generalized replacements first
        if col_name in self.value_replacements:
            replacements = self.value_replacements[col_name]
            
            # Try multiple string representations for numeric values
            candidates = [str(value)]
            if isinstance(value, (int, float)):
                # Add integer representation for float values like 2022.0 -> "2022"
                if isinstance(value, float) and value.is_integer():
                    candidates.append(str(int(value)))
                # Add float representation for int values like 2022 -> "2022.0"
                elif isinstance(value, int):
                    candidates.append(str(float(value)))
            
            # Try each candidate until we find a match
            for candidate in candidates:
                if candidate in replacements:
                    return replacements[candidate]
            
            # No replacement found, return original value as string
            return str(value)
        
        # Fallback to legacy latex_model_names for backward compatibility
        if col_name == 'model':
            return self.latex_model_names.get(str(value), str(value))
        
        return str(value)
    
    def get_column_patterns(self, col_name):
        """Get pattern formatting rules for a specific column"""
        # Check new generalized patterns first
        if col_name in self.pattern_formatting:
            return self.pattern_formatting[col_name]
        
        # Fallback to legacy model_patterns for backward compatibility
        if col_name == 'model':
            return self.model_patterns
        
        return {'suffixes': {}}
    
    def should_exclude_value(self, col_name, value):
        """Check if a value should be excluded from display"""
        # Check new generalized filtering first
        if self.row_filtering and 'exclude_values' in self.row_filtering:
            exclude_values = self.row_filtering['exclude_values']
            if col_name in exclude_values:
                excluded = exclude_values[col_name]
                return any(self._matches_pattern(str(value), pattern) for pattern in excluded)
        
        # Fallback to legacy ignored_models for backward compatibility
        if col_name == 'model':
            return str(value) in self.ignored_models
        
        return False
    
    def should_exclude_from_calculations(self, col_name, value):
        """Check if a value should be excluded from calculations"""
        # Check new generalized filtering first
        if self.row_filtering and 'exclude_from_calculations' in self.row_filtering:
            exclude_from_calc = self.row_filtering['exclude_from_calculations']
            if col_name in exclude_from_calc:
                excluded = exclude_from_calc[col_name]
                return any(self._matches_pattern(str(value), pattern) for pattern in excluded)
        
        # Fallback to legacy ignored_models_in_calculation for backward compatibility
        if col_name == 'model':
            return str(value) in self.ignored_in_calculation
        
        return False
    
    def _matches_pattern(self, value, pattern):
        """Check if value matches a pattern (supports wildcards)"""
        import fnmatch
        return fnmatch.fnmatch(value, pattern)