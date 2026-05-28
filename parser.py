import pdfplumber
import pandas as pd
import re

def extract_transactions(pdf_path):
    all_text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"
    
    return all_text

def parse_transactions(raw_text):
    transactions = []
    lines = raw_text.split("\n")
    
    for line in lines:
        if re.search(r'\d+[\.,]\d+', line) and len(line.strip()) > 5:
            transactions.append(line.strip())
    
    return transactions

def get_transaction_dataframe(pdf_path):
    raw_text = extract_transactions(pdf_path)
    transactions = parse_transactions(raw_text)
    df = pd.DataFrame(transactions, columns=["raw_transaction"])
    return df, raw_text

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        df, raw = get_transaction_dataframe(sys.argv[1])
        print(f"Found {len(df)} transactions")
        print(df.head(10))
    else:
        print("Usage: python parser.py <path_to_pdf>")