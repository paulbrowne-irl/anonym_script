import os
import re
import fitz  
import docx
import stanza

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

# Extract text from PDF
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    full_text = []
    for page in doc:
        full_text.append(page.get_text("text"))
    doc.close()
    return "\n".join(full_text)

# Extract text from DOCX
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_sensitive_values(text):
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

# Redact values in text
def redact_text(text, values_to_redact):
    for value in values_to_redact:
        pattern = re.compile(rf"\b{re.escape(value)}\b")
        text = pattern.sub("[REDACTED]", text)
    return text

def process_documents(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.startswith("~$"):
            continue  # Skip temporary Word files

        file_path = os.path.join(input_dir, filename)
        if filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif filename.lower().endswith(".docx"):
            text = extract_text_from_docx(file_path)
        else:
            continue

        values_to_redact = extract_sensitive_values(text)
        redacted_text = redact_text(text, values_to_redact)

        output_filename = os.path.splitext(filename)[0] + ".md"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(redacted_text)



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python updated_anonymize_script.py <input_directory> <output_directory>")
        sys.exit(1)
    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    process_documents(input_directory, output_directory)

