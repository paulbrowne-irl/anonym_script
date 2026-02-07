Simple scripts to anonmyise personal and company info from a folder of word and pdf docs. Forked from [ioanag248/anonym_script](https://github.com/ioanag248/anonym_script)

## Project Overview

This project provides tools to anonymize sensitive information from documents (word, pdf, docx) and generate wordcount distributions from the resulting markdown files.

### Features

-   **Anonymization**: `anonymize.py` processes PDF and DOCX files to redact sensitive information such as names, emails, and specific keywords. It outputs the redacted text as Markdown files.
-   **Word Count Analysis**: `wordcount.py` scans a directory of Markdown files to count word frequencies and outputs the results to an Excel file.

## Prerequisites

-   **Python 3.x**: This project requires Python 3. Ensure you have it installed by running `python --version` or `python3 --version`. If not, a guide to install Python can be found here: https://www.tomshardware.com/how-to/install-python-on-windows-10-and-11
-   **pip**: The Python package installer. It is usually included with Python. Verify with `pip --version`.

## Installation

1.  **Clone or Download the Repository**:
    If you haven't already, clone this repository or download the source code.

2.  **Set up a Virtual Environment (Recommended)**:
    It is best practice to use a virtual environment to manage dependencies.

    ```bash
    # Create a virtual environment named 'venv'
    python -m venv venv

    # Activate the virtual environment
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    Install the required Python packages using `pip` and the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```
    *Note: You may need to upgrade `pip` first: `python -m pip install --upgrade pip`*

## Usage

### 1. Anonymize Documents

Use `anonymize.py` to redact sensitive information from your documents.

**Command:**

```bash
python anonymize.py <input_directory> <output_directory> <stopwords_file>
```

**Arguments:**

-   `<input_directory>`: Path to the folder containing the PDF or DOCX files you want to anonymize.
-   `<output_directory>`: Path where the redacted Markdown files will be saved. The script will create this directory if it doesn't exist.
-   `<stopwords_file>`: Path to a text file containing stopwords to be removed/redacted (e.g., `stopwords.txt`).

**Example:**

```bash
python anonymize.py ./docs ./redacted_docs stopwords.txt
```

### 2. Count Words

Use `wordcount.py` to generate a word frequency report from Markdown files.

**Command:**

```bash
python wordcount.py <input_folder> <output_file>
```

**Arguments:**

-   `<input_folder>`: Path to the folder containing the Markdown (.md) files.
-   `<output_file>`: Name (and path) of the Excel file to be created (e.g., `word_counts.xlsx`).

**Example:**

```bash
python wordcount.py ./redacted_docs word_counts.xlsx
```