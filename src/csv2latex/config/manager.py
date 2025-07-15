import yaml
import logging


class ConfigManager:
    """Manages loading and accessing configuration from YAML file"""
    
    def __init__(self, config_path='table_config.yaml'):
        self.config_path = config_path
        self._config = self._load_config()
    
    def load_config_file(self, new_config_path):
        """Load a new configuration file and update the current config"""
        self.config_path = new_config_path
        self._config = self._load_config()
        logging.info(f"Loaded new configuration file: {new_config_path}")
    
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.warning(f"Configuration file {self.config_path} not found. Using defaults.")
            return {}
    
    @property
    def column_mappings(self):
        """Get column name mappings"""
        return self._config.get('display_names', {})
    
    @property
    def latex_model_names(self):
        """Get LaTeX model name mappings"""
        return self._config.get('latex_model_names', {})
    
    @property
    def model_order(self):
        """Get model order configuration"""
        return self._config.get('model_order', {})
    
    @property
    def ignored_models(self):
        """Get list of models to ignore"""
        return set(self._config.get('ignored_models', []))
    
    @property
    def ignored_in_calculation(self):
        """Get list of models to ignore in calculation"""
        return set(self._config.get('ignored_models_in_calculation', []))
    
    @property
    def extra_columns(self):
        """Get extra columns configuration"""
        return self._config.get('extra_columns', [])
    
    @property
    def model_patterns(self):
        """Get model pattern rules"""
        return self._config.get('model_patterns', {'suffixes': {}})
    
    @property
    def column_formats(self):
        """Get column format specifications"""
        return self._config.get('column_formats', {})
    
    @property
    def underline_min_values(self):
        """Get whether to underline minimum values (legacy global setting)"""
        return self._config.get('underline_min_values', True)
    
    @property
    def column_underline(self):
        """Get per-column underline settings"""
        return self._config.get('column_underline', {})
    
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
        # Check per-column setting first, then fall back to global setting
        if col_name in self.column_underline:
            return self.column_underline[col_name]
        else:
            return self.underline_min_values