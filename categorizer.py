import os
import json
from groq import Groq
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def categorize_single_batch(batch_with_index):
    index, batch = batch_with_index
    transactions_text = "\n".join(batch)
    
    prompt = f"""
You are a smart Indian finance assistant.
Analyze these transactions from an Indian bank statement and categorize each one.

Transactions:
{transactions_text}

For each transaction, create an object with:
- "description": the original transaction text (shortened, max 6 words)
- "amount": extract the rupee amount as a number (negative for money sent/paid/withdrawn, positive for received/deposited)
- "category": one of these: Food, Transport, Entertainment, Shopping, Transfer In, Transfer Out, Utilities, Healthcare, Education, Investment, Groceries, Personal Care, Other
- "merchant": the actual merchant or person name (e.g. "Zomato", "Blinkit", "Uber", "Manan Singhal"). Be specific — don't say "Unknown" if you can figure it out from the text.

Rules:
- UPI-ZOMATO = Food, merchant Zomato
- UPI-BLINKIT = Groceries, merchant Blinkit  
- UPI-SWIGGY = Food, merchant Swiggy
- UPI-UBER = Transport, merchant Uber
- UPI-AMAZON = Shopping, merchant Amazon
- UPI-MCDONALDS = Food, merchant McDonalds
- UPI-DOMINOS = Food, merchant Dominos
- UPI-BASKIN = Food, merchant Baskin Robbins
- UPI-BOOKMYSHOW = Entertainment, merchant BookMyShow
- UPI-JIO = Utilities, merchant Jio
- PETROLEUM/FUEL/PETROL = Transport
- NEFT CR / IMPS deposit = Transfer In
- SALARY/LETZPAY/DNS = Transfer In (salary)
- JYOTI BROKING = Investment
- IRFC/APY = Investment
- INTEREST PAID = Transfer In
- If person name in UPI, use their name as merchant

Return a JSON object containing a single key "transactions" mapped to the array of these objects.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=4000,
        response_format={"type": "json_object"} # Forces native JSON output
    )
    
    raw = response.choices[0].message.content
    data = json.loads(raw)
    
    return index, data.get("transactions", [])


import time

def categorize_single_batch_with_retry(batch_with_index, retries=3):
    index, batch = batch_with_index
    for attempt in range(retries):
        try:
            return categorize_single_batch((index, batch))
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                wait_time = 15 * (attempt + 1)
                print(f"⏳ Batch {index+1} rate limited — waiting {wait_time}s then retrying...")
                time.sleep(wait_time)
            else:
                print(f"❌ Batch {index+1} error: {e}")
                break
    
    print(f"❌ Batch {index+1} failed after {retries} retries — using fallback")
    return index, [{
        "description": t[:40],
        "amount": 0,
        "category": "Other",
        "merchant": "Unknown"
    } for t in batch]


def categorize_transactions(transactions_list, prebuilt_df=None):
    batch_size = 50
    batches = [transactions_list[i:i+batch_size] 
               for i in range(0, len(transactions_list), batch_size)]
    
    print(f"Total transactions: {len(transactions_list)}")
    print(f"Total batches: {len(batches)} — running with rate limit protection...")
    
    results = [None] * len(batches)
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(categorize_single_batch_with_retry, (i, batch)): i 
            for i, batch in enumerate(batches)
        }
        
        for future in as_completed(futures):
            try:
                index, result = future.result()
                results[index] = result
                print(f"✅ Batch {index+1}/{len(batches)} done")
            except Exception as e:
                index = futures[future]
                print(f"❌ Batch {index+1} final failure: {e}")
                results[index] = [{
                    "description": t[:40],
                    "amount": 0,
                    "category": "Other",
                    "merchant": "Unknown"
                } for t in batches[index]]
    
    all_categorized = []
    for r in results:
        if r:
            all_categorized.extend(r)
    
    return all_categorized


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