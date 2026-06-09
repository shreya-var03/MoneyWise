import pandas as pd
import re
import os

# ── 1. LOAD THE DATASET INTO MEMORY ──
DATASET_PATH = "rupeeroast_txn_categories.csv"
MERCHANT_MAP = {}

# We load the CSV once when the app starts and turn it into a fast lookup dictionary
if os.path.exists(DATASET_PATH):
    df = pd.read_csv(DATASET_PATH)
    for _, row in df.iterrows():
        # Clean the data: remove empty rows and make everything lowercase for easy matching
        if pd.notna(row['merchant']) and pd.notna(row['category']):
            clean_merchant = str(row['merchant']).strip().lower()
            clean_category = str(row['category']).strip().title()
            MERCHANT_MAP[clean_merchant] = clean_category
else:
    print(f"⚠️ Warning: {DATASET_PATH} not found in the folder! Make sure it is uploaded.")

def extract_amount(text):
    """Helper function to find the monetary amount in a raw bank string."""
    # Finds numbers with optional decimals (e.g., 1200, 15.50)
    matches = re.findall(r'\d+(?:\.\d+)?', str(text).replace(',', ''))
    if matches:
        return float(matches[-1]) 
    return 0.0

def categorize_transactions(raw_transactions, prebuilt_df=None):
    """
    Takes a list of raw transaction strings and returns a list of dictionaries 
    with clean merchants, amounts, and mapped categories instantly using the dataset.
    """
    print(f"Total transactions to process locally: {len(raw_transactions)}")
    categorized = []
    
    for tx in raw_transactions:
        tx_lower = str(tx).lower()
        amount = extract_amount(tx_lower)
        
        # Determine if it's a credit (+) or debit (-)
        if " cr " in tx_lower or " cr." in tx_lower or "credit" in tx_lower or " deposit" in tx_lower:
            amount = abs(amount)
        elif " dr " in tx_lower or " dr." in tx_lower or "debit" in tx_lower or " paid" in tx_lower:
            amount = -abs(amount)
        else:
            # Assume debit if it doesn't specify, as most bank statement entries are spends
            amount = -abs(amount)
        
        found_merchant = "Unknown"
        found_category = "Other"
        
        # ── 2. THE SMART DATASET LOOKUP ──
        # Check if any merchant from our CSV exists in the raw transaction string
        matched = False
        for merchant_name, category in MERCHANT_MAP.items():
            if merchant_name in tx_lower:
                found_merchant = merchant_name.title() # Capitalize it nicely (e.g., "Blinkit")
                found_category = category              # Map the exact category (e.g., "Groceries")
                matched = True
                break
                
        # ── 3. FALLBACK LOGIC (If the merchant isn't in the CSV) ──
        if not matched:
            # Try to grab the first word as the merchant name
            words = re.sub(r'[^a-zA-Z\s]', '', tx_lower).split()
            if len(words) > 0:
                # Exclude common bank words
                clean_words = [w for w in words if w not in ["upi", "cr", "dr", "neft", "imps", "rtgs", "to", "from", "inb"]]
                if clean_words:
                    found_merchant = clean_words[0].title()
            
            # Auto-categorize based on money flow
            if amount > 0:
                found_category = "Transfer In"
            else:
                found_category = "Transfer Out"

        # Append the beautifully formatted transaction
        categorized.append({
            "merchant": found_merchant,
            "category": found_category,
            "amount": amount
        })
        
    print("✅ Local categorization complete!")
    return categorized

if __name__ == "__main__":
    from parser import get_transaction_dataframe
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    if path:
        df, _ = get_transaction_dataframe(path)
        transactions = df["raw_transaction"].tolist()
        print(f"Total: {len(transactions)}")
        result = categorize_transactions(transactions)
        print(f"Categorized: {len(result)}")
        for item in result[:10]:
            print(item)