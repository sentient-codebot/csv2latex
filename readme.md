# CSV to LaTeX Table Converter

This script provides a GUI application for converting CSV files to LaTeX tables using PyQt6. It includes functionalities for loading CSV files, setting filters, sorting data, and customizing column mappings.

**Acknowledgement**: This project is produced by the collaboration of chatGPT-4o and Claude 3.5 Sonnet. The script and documents are subject to mistakes and do not represent the stand of the author. The author is not responsible for any misuse of the script and documents.

## Features

- Load multiple CSV files and combine them into a single dataframe
- Set filters on columns to include only specific data
- Sort data based on selected columns and order
- Customize column names for the LaTeX output
- Convert the filtered and sorted data to a LaTeX table format

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/sentient-codebot/csv2latex
    cd csv2latex
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:
    ```sh
    python csv2latex.py
    ```

2. Use the GUI to load CSV files, set filters, sort data, and convert to LaTeX.

## Example

1. Load CSV files by clicking the "Load CSV Files" button.
2. Set filters by clicking the "Set Filters" button and configuring the desired filters.
3. Set the sort order by clicking the "Set Sort Order" button and selecting the columns and order.
4. Convert to LaTeX by clicking the "Convert to LaTeX" button.

## License

This project is licensed under the MIT License.