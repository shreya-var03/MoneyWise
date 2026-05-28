import json
import os
import csv
import pandas as pd
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DATASET_FILE = "rupeeRoast_dataset.csv"

def translate_to_languages(transactions_sample):
    """Translate top transactions into Hindi and Hinglish for multilingual dataset"""
    
    sample = transactions_sample[:10]  # only translate top 10 to save tokens
    
    items_text = "\n".join([
        f"- {t.get('merchant', 'Unknown')}: {t.get('category', 'Other')} ₹{abs(t.get('amount', 0)):.0f}"
        for t in sample
    ])
    
    prompt = f"""For each of these Indian financial transactions, provide translations.
Return ONLY a JSON array. Each item must have:
- "merchant": original merchant name
- "category": category in English
- "category_hindi": category in Hindi (Devanagari)
- "category_hinglish": category in Hinglish
- "description_hindi": short description in Hindi
- "description_hinglish": short description in Hinglish

Transactions:
{items_text}

JSON array only. No markdown."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2000
    )
    
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    start = raw.find('[')
    end = raw.rfind(']') + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    
    import json
    return json.loads(raw)


def add_to_dataset(categorized_transactions):
    """Add categorized transactions to the growing dataset CSV"""
    
    file_exists = os.path.exists(DATASET_FILE)
    
    rows = []
    for t in categorized_transactions:
        if t.get("merchant") in ["Unknown", "", None]:
            continue
        if t.get("category") == "Other" and t.get("amount") == 0:
            continue
            
        rows.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d"),
            "merchant": t.get("merchant", ""),
            "category": t.get("category", ""),
            "amount_range": get_amount_range(abs(t.get("amount", 0))),
            "transaction_type": "debit" if t.get("amount", 0) < 0 else "credit",
            "country": "India",
            "currency": "INR",
            "merchant_type": get_merchant_type(t.get("category", "")),
            "category_hindi": "",
            "category_hinglish": "",
            "description_hindi": "",
            "description_hinglish": "",
            "source": "RupeeRoast"
        })
    
    # get translations for this batch
    try:
        print("🌐 Generating multilingual translations...")
        translations = translate_to_languages(
            [t for t in categorized_transactions if t.get("amount", 0) < 0]
        )
        
        # map translations back
        translation_map = {t.get("merchant", ""): t for t in translations}
        for row in rows:
            if row["merchant"] in translation_map:
                tr = translation_map[row["merchant"]]
                row["category_hindi"] = tr.get("category_hindi", "")
                row["category_hinglish"] = tr.get("category_hinglish", "")
                row["description_hindi"] = tr.get("description_hindi", "")
                row["description_hinglish"] = tr.get("description_hinglish", "")
    except Exception as e:
        print(f"Translation skipped: {e}")
    
    # write to CSV — deduplicate by merchant+category
    new_df = pd.DataFrame(rows)
    if os.path.exists(DATASET_FILE):
        existing = pd.read_csv(DATASET_FILE)
        if not new_df.empty:
            combined = pd.concat([existing, new_df], ignore_index=True)
            combined = combined.drop_duplicates(subset=["merchant", "category"], keep="last")
            combined.to_csv(DATASET_FILE, index=False)
    else:
        if not new_df.empty:
            fieldnames = [
                "timestamp", "merchant", "category", "amount_range",
                "transaction_type", "country", "currency", "merchant_type",
                "category_hindi", "category_hinglish",
                "description_hindi", "description_hinglish", "source"
            ]
            new_df = new_df.reindex(columns=fieldnames)
            new_df.to_csv(DATASET_FILE, index=False)

    print(f"✅ Added {len(rows)} rows to dataset. Total so far: {count_dataset_rows()}")
    return len(rows)

def get_amount_range(amount):
    if amount < 100: return "0-100"
    elif amount < 500: return "100-500"
    elif amount < 1000: return "500-1000"
    elif amount < 5000: return "1000-5000"
    elif amount < 10000: return "5000-10000"
    else: return "10000+"


def get_merchant_type(category):
    mapping = {
        "Food": "F&B",
        "Groceries": "Retail",
        "Transport": "Mobility",
        "Entertainment": "Leisure",
        "Shopping": "Retail",
        "Utilities": "Services",
        "Healthcare": "Medical",
        "Education": "EdTech",
        "Investment": "Finance",
        "Transfer In": "P2P",
        "Transfer Out": "P2P",
        "Personal Care": "Wellness",
    }
    return mapping.get(category, "Other")


def count_dataset_rows():
    if not os.path.exists(DATASET_FILE):
        return 0
    with open(DATASET_FILE, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f) - 1  # minus header


def get_dataset_stats():
    if not os.path.exists(DATASET_FILE):
        return None
    df = pd.read_csv(DATASET_FILE)
    return {
        "total_records": len(df),
        "unique_merchants": df["merchant"].nunique(),
        "categories": df["category"].value_counts().to_dict(),
        "multilingual_coverage": len(df[df["category_hindi"] != ""]),
    }


if __name__ == "__main__":
    stats = get_dataset_stats()
    if stats:
        print(f"Dataset stats: {json.dumps(stats, indent=2)}")
    else:
        print("No dataset yet — upload a statement first!")