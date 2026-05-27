import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def categorize_single_batch(batch):
    transactions_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(batch)])
    
    prompt = f"""Categorize these Indian bank transactions. Return ONLY a JSON array.

Each item must have:
- "description": short name (max 5 words)
- "amount": number (negative=withdrawal, positive=deposit)
- "category": one of [Food, Transport, Entertainment, Shopping, Transfer In, Transfer Out, Utilities, Healthcare, Education, Investment, Other]
- "merchant": merchant or person name

Transactions:
{transactions_text}

JSON array only. No markdown. No explanation."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=3000
    )
    
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    
    start = raw.find('[')
    end = raw.rfind(']') + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    
    return json.loads(raw)

def categorize_transactions(transactions_list):
    # bigger batches = fewer API calls = faster
    batch_size = 25
    batches = [transactions_list[i:i+batch_size] 
               for i in range(0, len(transactions_list), batch_size)]
    
    all_categorized = []
    
    for i, batch in enumerate(batches):
        print(f"Batch {i+1}/{len(batches)}...")
        try:
            result = categorize_single_batch(batch)
            all_categorized.extend(result)
        except Exception as e:
            print(f"Batch {i+1} failed: {e}")
            for t in batch:
                all_categorized.append({
                    "description": t[:40],
                    "amount": 0,
                    "category": "Other",
                    "merchant": "Unknown"
                })
    
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
        print(f"Done: {len(result)}")