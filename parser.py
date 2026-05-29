import pdfplumber
import pandas as pd

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

    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

    for line in lines:

        if (
            "Paid to" in line
            or "Received from" in line
            or "Money sent" in line
        ):

            transactions.append(line)

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