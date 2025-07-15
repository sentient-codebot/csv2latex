# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PyQt6-based GUI application for converting CSV files to LaTeX tables. It provides filtering, sorting, and column customization capabilities for generating publication-ready LaTeX tables.

## Development Commands

**Run the application:**
```bash
python main.py
```

**Install dependencies:**
deprecated.
```bash
pip install -r requirements.txt
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

## Code Architecture

### Main Components

1. **Entry Points:**
   - `main.py` - Direct execution entry point
   - `src/csv2latex/app.py` - Contains `cli()` function for package entry point

2. **Core Application:**
   - `src/csv2latex/converters.py` - Main GUI application (`CSVToLatexConverter` class)
   - `src/csv2latex/_converters.py` - Simplified version without YAML config support

3. **Key Classes:**
   - `CSVToLatexConverter` - Main window with full feature set including YAML configuration
   - `FilterDialog` - Modal dialog for setting row filters (numeric ranges, categorical values)
   - `SortDialog` - Modal dialog for configuring multi-column sorting with drag-and-drop reordering

### Configuration System

The application supports advanced configuration through `table_config.yaml`:

- `display_names` - Column name mappings for display
- `latex_model_names` - Model name mappings for LaTeX output
- `model_order` - Custom ordering for model rows
- `ignored_models` - Models to exclude from display
- `ignored_models_in_calculation` - Models to exclude from min value calculations
- `extra_columns` - Additional columns to insert at specific positions
- `model_patterns` - Pattern-based formatting rules (e.g., suffixes)

### Data Processing Flow

1. **CSV Loading** - Multiple files can be loaded and concatenated
2. **Model Filtering** - Ignored models are filtered out early
3. **Model Sorting** - Custom model ordering is applied
4. **User Filtering** - Interactive filters for numeric ranges and categorical values
5. **User Sorting** - Multi-column sorting with custom order
6. **Column Selection** - Interactive column inclusion/exclusion and renaming
7. **LaTeX Generation** - Table generation with min value highlighting and custom formatting

### GUI Layout

- Top buttons: Load CSV, Set Filters, Set Sort Order, Convert to LaTeX
- Column configuration table with Include/Original Name/Display Name columns
- Move Up/Down buttons for column reordering
- Data preview table
- Decimal places input
- LaTeX output text area (monospace font)

## Key Features

- **Multi-file CSV loading** with automatic concatenation
- **Advanced filtering** supporting numeric ranges and categorical equality
- **Multi-column sorting** with drag-and-drop reordering
- **Column customization** with include/exclude and display name mapping
- **LaTeX formatting** with minimum value highlighting and custom model name mapping
- **Configuration-driven** behavior through YAML files
- **Pattern matching** for model-specific formatting rules