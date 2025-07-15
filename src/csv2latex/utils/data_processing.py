import pandas as pd
import fnmatch


class DataProcessor:
    """Handles data filtering and sorting operations"""
    
    @staticmethod
    def apply_filters(df, active_filters):
        """Apply active filters to dataframe with support for numeric ranges"""
        if not active_filters:
            return df
        
        mask = pd.Series(True, index=df.index)
        
        for col, filter_info in active_filters.items():
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
    
    @staticmethod
    def apply_sort(df, sort_keys):
        """Apply sort keys to dataframe"""
        if not sort_keys:
            return df
        
        by = [col for col, _ in sort_keys]
        ascending = [asc for _, asc in sort_keys]
        return df.sort_values(by=by, ascending=ascending)
    
    @staticmethod
    def matches_ignored_pattern(model_name, ignored_patterns):
        """Check if model name matches any ignored pattern"""
        return any(fnmatch.fnmatch(str(model_name), pattern) 
                  for pattern in ignored_patterns)
    
    @staticmethod
    def filter_ignored_models(df, ignored_models):
        """Filter out ignored models from dataframe"""
        if 'model' not in df.columns:
            return df
        return df[~df['model'].isin(ignored_models)]
    
    @staticmethod
    def sort_by_model_order(df, get_model_order_func):
        """Sort dataframe by model order using provided function"""
        if 'model' not in df.columns:
            return df
        
        df_copy = df.copy()
        df_copy['_model_order'] = df_copy['model'].apply(get_model_order_func)
        return df_copy.sort_values('_model_order').drop('_model_order', axis=1)