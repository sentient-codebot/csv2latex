# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PyQt6-based GUI application for converting CSV files to LaTeX tables. It provides filtering, sorting, and column customization capabilities for generating publication-ready LaTeX tables.

## Development Commands

**Run the application:**
```bash
python main.py
```

**Using uv (recommended):**
```bash
uv sync
uv run python main.py
```

**Package entry point:**
```bash
csv2latex  # after installation
```

**Install for development:**
```bash
uv sync  # installs dependencies from pyproject.toml
```

## Code Architecture

### Modular Structure

The application follows a modular architecture with clear separation of concerns:

1. **Entry Points:**
   - `main.py` - Direct execution entry point
   - `src/csv2latex/app.py` - Contains `cli()` function for package entry point

2. **Core Application:**
   - `src/csv2latex/main_window.py` - Main GUI window (`CSVToLatexConverter` class)
   - `src/csv2latex/__converters.py` - Legacy monolithic implementation

3. **Component Modules:**
   - `src/csv2latex/config/manager.py` - Configuration management (`ConfigManager` class)
   - `src/csv2latex/dialogs/` - UI dialog components (`FilterDialog`, `SortDialog`)
   - `src/csv2latex/latex/formatter.py` - LaTeX generation (`LatexFormatter` class)
   - `src/csv2latex/utils/data_processing.py` - Data operations (`DataProcessor` class)

4. **Key Classes:**
   - `CSVToLatexConverter` - Main window orchestrating all components
   - `ConfigManager` - Loads and manages YAML configuration
   - `DataProcessor` - Handles filtering, sorting, and data manipulation
   - `LatexFormatter` - Generates LaTeX table output with formatting rules

### Configuration System

The application supports advanced configuration through `table_config.yaml`:

- `display_names` - Column name mappings for display
- `latex_model_names` - Model name mappings for LaTeX output
- `model_order` - Custom ordering for model rows
- `ignored_models` - Models to exclude from display
- `ignored_models_in_calculation` - Models to exclude from min value calculations
- `extra_columns` - Additional columns to insert at specific positions
- `model_patterns` - Pattern-based formatting rules (e.g., suffixes)
- `column_formats` - **NEW FEATURE**: Column-specific display formatting using Python format strings

The `ConfigManager` class provides centralized access to all configuration options with fallback defaults when the YAML file is missing.

#### Column Formatting

The `column_formats` section allows specifying custom display formats for each column:

```yaml
column_formats:
  accuracy: ".3f"           # 3 decimal places: 0.856432 -> 0.856
  loss: ".2e"               # Scientific notation: 0.00034 -> 3.40e-04
  learning_rate: ".1e"      # Scientific notation: 0.001 -> 1.0e-03
  percentage_improved: ".1%"  # Percentage: 0.156 -> 15.6%
  epoch_time: ".0f"         # No decimals: 45.67 -> 46
```

- Supports all Python format specifiers (decimal, scientific, percentage, etc.)
- Applied to both preview table and LaTeX output
- Falls back to default decimal places if format fails or not specified
- Accessed via `ConfigManager.get_column_format(column_name)`

### Data Processing Flow

1. **CSV Loading** - Multiple files can be loaded and concatenated
2. **Model Filtering** - Ignored models are filtered out early via `DataProcessor.filter_ignored_models()`
3. **Model Sorting** - Custom model ordering is applied via `DataProcessor.sort_by_model_order()`
4. **User Filtering** - Interactive filters for numeric ranges and categorical values via `DataProcessor.apply_filters()`
5. **User Sorting** - Multi-column sorting with custom order via `DataProcessor.apply_sort()`
6. **Column Selection** - Interactive column inclusion/exclusion and renaming in main window
7. **Value Formatting** - Custom column formats applied via `ConfigManager.get_column_format()` in both preview and LaTeX generation
8. **LaTeX Generation** - Table generation with min value highlighting and custom formatting via `LatexFormatter.generate_latex_table()`

### Component Interaction

- **Main Window** (`CSVToLatexConverter`) orchestrates all components and manages UI state
- **ConfigManager** is shared across components for consistent configuration access
- **DataProcessor** provides pure static methods for data manipulation without state
- **LatexFormatter** receives processed data and generates formatted LaTeX output
- **Dialog components** (`FilterDialog`, `SortDialog`) handle specific user interactions

### GUI Layout

- Top buttons: Load CSV, Set Filters, Set Sort Order, Convert to LaTeX
- Column configuration table with Include/Original Name/Display Name columns
- Move Up/Down buttons for column reordering
- Data preview table (updates automatically with filters/sorting)
- Decimal places input
- LaTeX output text area (monospace font)

## Key Features

- **Multi-file CSV loading** with automatic concatenation
- **Advanced filtering** supporting numeric ranges and categorical equality
- **Multi-column sorting** with drag-and-drop reordering
- **Column customization** with include/exclude and display name mapping
- **Custom column formatting** with Python format strings (decimal, scientific, percentage, etc.)
- **LaTeX formatting** with minimum value highlighting and custom model name mapping
- **Configuration-driven** behavior through YAML files
- **Pattern matching** for model-specific formatting rules
- **Modular architecture** with clear separation of concerns