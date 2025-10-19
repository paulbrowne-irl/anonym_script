import os
import sys
import re
import fitz  
import docx
import stanza
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

#setup tracker for file names
counter =1 

#handle stopwords globally
stopwords =[]

# Initialize Stanza English pipeline
stanza.download('en')
nlp = stanza.Pipeline('en', processors='tokenize,ner')

# Define keywords and email pattern
keywords = [
    "Company Name:",
    "Project Number:",
    "Company Contact Name:",
    "Contact Email Address:",
    "Consultant Name:",
    "Consultant Company Name:",
    "Consultant Email Address:",
    "Consultant Signature (3) :",
    "Consultant Signature"
]
email_pattern = re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}")



def extract_text_from_pdf(file_path):
    """
    Extracts all text from a given PDF file.

    Args:
        file_path: The path to the PDF file.

    Returns:
        A string containing all the text from the PDF.
    """
    logging.info(f"Extracting text from PDF: {file_path}")
    doc = fitz.open(file_path)
    full_text = []
    for page in doc:
        full_text.append(page.get_text("text"))
    doc.close()
    return "\n".join(full_text)

def extract_text_from_docx(file_path):
    """
    Extracts all text from a given DOCX file.

    Args:
        file_path: The path to the DOCX file.

    Returns:
        A string containing all the text from the DOCX file.
    """
    logging.info(f"Extracting text from DOCX: {file_path}")
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def redact_sensitive_values(text):
    """
    Identifies sensitive values in a text based on keywords, email patterns, and named entity recognition.

    Args:
        text: The input string to search for sensitive values.

    Returns:
        A set of strings containing the identified sensitive values.
    """
    logging.info("Extracting sensitive values from text")
    values_to_redact = set()

    # Extract values after keywords
    for keyword in keywords:
        pattern = re.escape(keyword) + r"\s*(.*)"
        matches = re.findall(pattern, text)
        for match in matches:
            value = match.strip().split("\n")[0]
            if value:
                values_to_redact.add(value)

    # Extract email addresses
    emails = email_pattern.findall(text)
    values_to_redact.update(emails)

    # Extract names using Stanza NER
    doc_nlp = nlp(text)
    for ent in doc_nlp.ents:
        if ent.type == "PERSON":
            values_to_redact.add(ent.text.strip())

    return values_to_redact

def redact_text(text, values_to_redact):
    """
    Redacts a set of values from a given text.

    Args:
        text: The input string to redact values from.
        values_to_redact: A set of strings to be replaced with "[REDACTED]".

    Returns:
        The text with the specified values redacted.
    """
    logging.info(f"Redacting {len(values_to_redact)} values from text")
    for value in values_to_redact:
        pattern = re.compile(rf"\b{re.escape(value)}\b")
        text = pattern.sub("[REDACTED]", text)


    # check and remove stopwords from this text
    text=redact_stopwords_from_markdown(text)
    
    return text

def redact_stopwords_from_markdown(markdown_text):
    """
    removes previously read list of stopwords from 'stopwords.txt' and removes them from the given markdown text.

    Args:
        markdown_text: A string containing the text from a markdown file.

    Returns:
        The markdown text with stopwords removed.
    """
    logging.info("Redacting stopwords from markdown text.")

    global stopwords

    total_replacements = 0

    # Ensure stopwords is iterable (set or list); skip empty items
    for sw in (stopwords or []):
        if not sw:
            continue
        # Use whole-word, case-insensitive matching; escape the stopword for regex safety
        try:
            pattern = re.compile(rf"\b{re.escape(sw)}\b", flags=re.IGNORECASE)
        except re.error:
            pattern = re.compile(re.escape(sw), flags=re.IGNORECASE)
        markdown_text, n = pattern.subn("[redacted]", markdown_text)
        total_replacements += n

    logging.info(f"Replaced {total_replacements} stopword occurrences.")
    return markdown_text

def process_documents(input_dir, output_dir,stopwords_file_name):
    """
    Processes all PDF and DOCX documents in an input directory, redacts sensitive information,
    and writes the redacted text to markdown files in an output directory.

    Args:
        input_dir: The path to the directory containing the documents to process.
        output_dir: The path to the directory where the redacted markdown files will be saved.
        stopwords_file_name: The path to the stopwords file.
    """
    global counter
    global stopwords

    # Load a list of specfic stop words to remove from the text
    try:
        with open(stopwords_file_name, "r", encoding="utf-8") as f:
            stopwords = set(f.read().splitlines())
            logging.info(f"Loaded {len(stopwords)} stopwords from {stopwords_file_name}.")
            
    except FileNotFoundError:
        logging.error(f"{stopwords_file_name} not found. No stopwords will be removed.")
       


    logging.info(f"Processing documents in directory: {input_dir}")
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.startswith("~$"):
            continue  # Skip temporary Word files

        file_path = os.path.join(input_dir, filename)

        try:

            if filename.lower().endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            elif filename.lower().endswith(".docx"):
                text = extract_text_from_docx(file_path)
            else:
                logging.warning(f"Skipping unsupported file: {filename}")
                continue
        except Exception as e:
            logging.error(f"Failed to open file  file {output_path}: {e}")
        
        
        values_to_redact = redact_sensitive_values(text)
        redacted_text = redact_text(text, values_to_redact)

        #output_filename = os.path.splitext(filename)[0] + ".md"
        output_filename = f"redacted_document_{counter}.md"
        counter += 1

        output_path = os.path.join(output_dir, output_filename)
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(redacted_text)
            logging.info(f"Redacted file written: {output_path}")
        except Exception as e:
            logging.error(f"Failed to write redacted file {output_path}: {e}")

if __name__ == "__main__":
    ''' 
    Example usage: python anonymize.py <input_directory> <output_directory>
    '''
    if len(sys.argv) != 4:
        logging.error("Usage: python anonymize.py <input_directory> <output_directory> <stopwords_file>")
        logging.info("Params given:"+str(sys.argv))
        sys.exit(1)
    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    stopwords_file = sys.argv[3]

    try:
        process_documents(input_directory, output_directory, stopwords_file)
    except Exception as e:
        logging.exception(f"An error occurred during processing: {e}")
        sys.exit(1)
