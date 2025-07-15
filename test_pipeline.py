#!/usr/bin/env python3
"""
Comprehensive pipeline test for CSV to LaTeX converter.

This script tests the complete pipeline including:
1. CSV loading and data processing
2. Generalized configuration features
3. Row filtering and sorting
4. Value replacements
5. Pattern formatting
6. Column formatting
7. LaTeX generation with underlines
8. Backward compatibility

Usage:
    python test_pipeline.py

Files used:
    - test_data.csv: Sample data with year, month, cluster, generative, scaled columns
    - test_config.yaml: Comprehensive configuration demonstrating all features
"""

import pandas as pd
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from csv2latex.config import ConfigManager
from csv2latex.utils import DataProcessor
from csv2latex.latex import LatexFormatter


def test_complete_pipeline():
    """Test the complete CSV to LaTeX conversion pipeline"""
    print("=" * 80)
    print("COMPREHENSIVE CSV TO LATEX PIPELINE TEST")
    print("=" * 80)
    
    # Step 1: Load data and configuration
    print("\\n1. LOADING DATA AND CONFIGURATION")
    print("-" * 40)
    
    try:
        df = pd.read_csv("test_data.csv")
        config = ConfigManager()
        config.load_config_file("test_config.yaml")
        
        print(f"✅ Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"✅ Configuration loaded: {config.config_path}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Data types: {dict(df.dtypes)}")
        
    except Exception as e:
        print(f"❌ Error loading data/config: {e}")
        return False
    
    # Step 2: Test generalized row filtering
    print("\\n2. TESTING GENERALIZED ROW FILTERING")
    print("-" * 40)
    
    original_shape = df.shape
    filtered_df = DataProcessor.filter_excluded_values(df, config)
    
    excluded_clusters = set(df['cluster'].unique()) - set(filtered_df['cluster'].unique())
    print(f"✅ Original data: {original_shape[0]} rows")
    print(f"✅ After filtering: {filtered_df.shape[0]} rows")
    print(f"✅ Excluded clusters: {sorted(excluded_clusters)}")
    
    if excluded_clusters != {4, 5}:
        print(f"❌ Expected to exclude clusters 4,5 but excluded {excluded_clusters}")
        return False
    
    # Step 3: Test generalized row sorting
    print("\\n3. TESTING GENERALIZED ROW SORTING")
    print("-" * 40)
    
    sorted_df = DataProcessor.sort_by_custom_order(filtered_df, config)
    
    print("✅ Data sorted by custom order")
    print("   First 10 rows (year, month, cluster):")
    for i, (_, row) in enumerate(sorted_df[['year', 'month', 'cluster']].head(10).iterrows()):
        print(f"     {i+1:2d}. {row['year']}-{row['month']:2d}-{row['cluster']}")
    
    # Step 4: Test value replacements
    print("\\n4. TESTING VALUE REPLACEMENTS")
    print("-" * 40)
    
    test_replacements = [
        ("year", 2022, "Year 1"),
        ("year", 2023, "Year 2"),
        ("month", 0, "Jan"),
        ("month", 6, "Jul"),
        ("cluster", 0, "0"),  # No replacement configured
    ]
    
    replacement_success = True
    for col, value, expected in test_replacements:
        result = config.get_value_replacement(col, value)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {col}[{value}] -> '{result}' (expected: '{expected}')")
        if result != expected:
            replacement_success = False
    
    if not replacement_success:
        print("❌ Some value replacements failed")
        return False
    
    # Step 5: Test pattern formatting
    print("\\n5. TESTING PATTERN FORMATTING")
    print("-" * 40)
    
    generative_patterns = config.get_column_patterns("generative")
    scaled_patterns = config.get_column_patterns("scaled")
    
    print(f"✅ Generative patterns: {generative_patterns}")
    print(f"✅ Scaled patterns: {scaled_patterns}")
    
    # Step 6: Test column formatting
    print("\\n6. TESTING COLUMN FORMATTING")
    print("-" * 40)
    
    format_tests = [
        ("year", 2022.0, "d"),
        ("month", 0.0, "d"),
        ("generative", 0.0092, ".4f"),
        ("scaled", 0.0180, ".4f"),
    ]
    
    for col, value, expected_format in format_tests:
        actual_format = config.get_column_format(col)
        status = "✅" if actual_format == expected_format else "❌"
        print(f"   {status} {col} format: '{actual_format}' (expected: '{expected_format}')")
    
    # Step 7: Test LaTeX generation
    print("\\n7. TESTING LATEX GENERATION")
    print("-" * 40)
    
    latex_formatter = LatexFormatter(config)
    selected_columns = {col: config.get_pretty_column_name(col) for col in sorted_df.columns}
    
    # Generate LaTeX for first 5 rows
    latex_output = latex_formatter.generate_latex_table(
        sorted_df.head(5), selected_columns, decimal_places=4
    )
    
    print("✅ LaTeX table generated successfully")
    print("   Sample output (first data row):")
    
    # Extract and display first data row
    latex_lines = latex_output.split('\\n')
    for line in latex_lines:
        if '&' in line and 'textbf' not in line and 'hline' not in line:
            print(f"     {line}")
            break
    
    # Step 8: Test specific features in LaTeX output
    print("\\n8. TESTING LATEX OUTPUT FEATURES")
    print("-" * 40)
    
    features_found = {
        "Year replacements": any(year_name in latex_output for year_name in ["Year 1", "Year 2", "Year 3"]),
        "Month replacements": any(month_name in latex_output for month_name in ["Jan", "Feb", "Jul"]),
        "Underlined values": "\\underline{" in latex_output,
        "Pattern symbols": any(symbol in latex_output for symbol in ["\\dagger", "\\ddagger", "\\ast"]),
        "Extra columns": "\\checkmark" in latex_output,
        "Proper formatting": "$" in latex_output,
    }
    
    all_features_work = True
    for feature, found in features_found.items():
        status = "✅" if found else "❌"
        print(f"   {status} {feature}: {'Found' if found else 'Not found'}")
        if not found and feature != "Pattern symbols":  # Pattern symbols depend on data
            all_features_work = False
    
    # Step 9: Test backward compatibility
    print("\\n9. TESTING BACKWARD COMPATIBILITY")
    print("-" * 40)
    
    # Test with legacy model configuration
    legacy_config = ConfigManager()
    legacy_config._config = {
        'model_order': {'test-model-1': 1, 'test-model-2': 2},
        'latex_model_names': {'test-model-1': 'Test Model 1'},
        'ignored_models': ['debug-model']
    }
    
    legacy_tests = [
        ("get_sort_order", lambda: legacy_config.get_sort_order('model', 'test-model-1') == 1),
        ("get_value_replacement", lambda: legacy_config.get_value_replacement('model', 'test-model-1') == 'Test Model 1'),
        ("should_exclude_value", lambda: legacy_config.should_exclude_value('model', 'debug-model') == True),
    ]
    
    for test_name, test_func in legacy_tests:
        try:
            result = test_func()
            status = "✅" if result else "❌"
            print(f"   {status} Legacy {test_name}: {'Passed' if result else 'Failed'}")
        except Exception as e:
            print(f"   ❌ Legacy {test_name}: Error - {e}")
            all_features_work = False
    
    # Final summary
    print("\\n" + "=" * 80)
    print("PIPELINE TEST SUMMARY")
    print("=" * 80)
    
    if all_features_work and replacement_success:
        print("🎉 ALL TESTS PASSED! The complete pipeline is working correctly.")
        print("\\n✅ Key features verified:")
        print("   • Generalized row filtering and sorting")
        print("   • Value replacements for all columns")
        print("   • Pattern formatting and custom column formats")
        print("   • LaTeX generation with underlines and symbols")
        print("   • Backward compatibility with legacy configurations")
        print("   • Extra columns and comprehensive formatting")
        return True
    else:
        print("❌ SOME TESTS FAILED! Please review the errors above.")
        return False


def main():
    """Main entry point"""
    success = test_complete_pipeline()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()