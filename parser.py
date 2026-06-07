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

# Regex patterns to detect dates and sensitive PII
date_pattern = re.compile(r"^\d{2}[/-]\w{2,3}[/-]\d{2,4}")
phone_pattern = re.compile(r"\b\d{10}\b")
acct_pattern = re.compile(r"\b\d{12,18}\b")
upi_pattern = re.compile(r"[a-zA-Z0-9.\-_]+@[a-zA-Z]+")

def clean_pii(text):
    """Strips sensitive information from the transaction line"""
    text = phone_pattern.sub("[PHONE_REDACTED]", text)
    text = acct_pattern.sub("[ACCOUNT_REDACTED]", text)
    text = upi_pattern.sub("[UPI_REDACTED]", text)
    return text

def parse_transactions(raw_text):
    transactions = []
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

    for line in lines:
        # Catch UPI formats OR standard tabular bank formats
        if (
            "Paid to" in line
            or "Received from" in line
            or "Money sent" in line
            or date_pattern.match(line)
        ):
            # Scrub the PII before saving it
            safe_line = clean_pii(line)
            transactions.append(safe_line)

    return transactions


def get_transaction_dataframe(pdf_path):

    raw_text = extract_transactions(pdf_path)

    print("\n==============================")
    print("FIRST 3000 CHARACTERS:")
    print(raw_text[:3000])
    print("==============================\n")

    transactions = parse_transactions(raw_text)

    print("TOTAL TRANSACTIONS FOUND:", len(transactions))

    df = pd.DataFrame(
        transactions,
        columns=["raw_transaction"]
    )

    return df, raw_text