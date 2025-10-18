import os
import re
import pandas as pd
from collections import Counter
import argparse

def count_md_file_words(folder_path, output_excel_file='word_counts.xlsx'):
    """
    Iterates over .md files in a folder, counts word frequencies, and outputs 
    the results to an Excel file.

    Args:
        folder_path (str): The path to the folder containing the .md files.
        output_excel_file (str): The name of the Excel file to create.
    """
    
    # 1. Initialize a Counter to store all word frequencies across all files
    all_words_counter = Counter()
    total_files_processed = 0

    print(f"Starting word count for .md files in: {folder_path}")
    print("-" * 30)

    # 2. Iterate over all files in the specified folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            
            try:
                print(f"Processing file: {filename}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                # 3. Tokenize and Normalize the text:
                # - Convert to lowercase
                # - Use re.findall to find all sequences of one or more word characters (\w+)
                words = re.findall(r'\b\w+\b', text.lower())
                
                # 4. Update the master counter with words from the current file
                all_words_counter.update(words)
                total_files_processed += 1

            except Exception as e:
                print(f"Error reading or processing file {filename}: {e}")

    print("-" * 30)
    
    if total_files_processed == 0:
        print("No .md files found or processed. Exiting.")
        return

    # 5. Prepare data for Excel output
    # Convert the Counter object to a list of (word, count) tuples
    word_data = all_words_counter.most_common()

    # Create a Pandas DataFrame
    df = pd.DataFrame(word_data, columns=['Word', 'Count'])

    # Sort the DataFrame alphabetically by word before saving (optional, but clean)
    df = df.sort_values(by='Word', ascending=True)

    # 6. Output to Excel file
    try:
        df.to_excel(output_excel_file, index=False)
        print(f"✅ Successfully wrote word counts to: {output_excel_file}")
        print(f"Total unique words: {len(df)}")
        print(f"Files processed: {total_files_processed}")
    except Exception as e:
        print(f"❌ Error writing to Excel file {output_excel_file}: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Count word frequencies in .md files.')
    parser.add_argument('input_folder', type=str, help='The path to the folder containing the .md files.')
    parser.add_argument('output_file', type=str, help='The name of the Excel file to create.')
    args = parser.parse_args()

    count_md_file_words(args.input_folder, args.output_file)