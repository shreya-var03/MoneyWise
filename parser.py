import pdfplumber
import pandas as pd
import re

def extract_transactions(pdf_path):
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # try table extraction first (much better for HDFC)
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        if row:
                            all_text += " | ".join([str(cell) for cell in row if cell]) + "\n"
            else:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"
    return all_text

def parse_transactions(raw_text):
    transactions = []
    lines = raw_text.split("\n")
    
    seen = set()
    
    for line in lines:
        line = line.strip()
        
        # skip empty, header, or too short lines
        if len(line) < 10:
            continue
        if any(skip in line.lower() for skip in [
            'date', 'narration', 'balance', 'opening', 'closing',
            'statement', 'account', 'branch', 'address', 'phone',
            'nomination', 'page no', 'generated', 'hdfc bank',
            'signature', 'micr', 'ifsc', 'gstin', 'registered'
        ]):
            continue
        
        # must contain a number (amount)
        if not re.search(r'\d+[\.,]\d+', line):
            continue
        
        # deduplicate
        key = line[:40]
        if key in seen:
            continue
        seen.add(key)
        
        transactions.append(line)
    
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