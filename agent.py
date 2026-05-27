import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_roast(categorized_transactions, language="Hinglish"):
    totals = {}
    total_spent = 0
    total_received = 0
    
    for t in categorized_transactions:
        amt = t.get("amount", 0)
        cat = t.get("category", "Other")
        if amt < 0:
            total_spent += abs(amt)
            totals[cat] = totals.get(cat, 0) + abs(amt)
        else:
            total_received += amt

    # only send TOP 5 categories + top 8 transactions to save tokens
    top_categories = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:5]
    top_transactions = sorted(
        [t for t in categorized_transactions if t.get("amount", 0) < 0],
        key=lambda x: abs(x.get("amount", 0)),
        reverse=True
    )[:8]

    totals_text = "\n".join([f"- {cat}: ₹{amt:.0f}" for cat, amt in top_categories])
    tx_text = "\n".join([f"- {t['merchant']}: ₹{abs(t['amount']):.0f} ({t['category']})" 
                         for t in top_transactions])

    lang_instruction = {
        "Hindi": "Respond entirely in Hindi (Devanagari script).",
        "Hinglish": "Respond in Hinglish — casual mix of Hindi and English like a Gen Z Indian.",
        "English": "Respond in English."
    }.get(language, "")

    prompt = f"""You are RupeeRoast — savage, funny, brutally honest Indian finance coach. Zero chill. {lang_instruction}

Spending summary:
Total Spent: ₹{total_spent:.0f} | Total Received: ₹{total_received:.0f}

Top categories:
{totals_text}

Biggest transactions:
{tx_text}

Give:
1. ROAST (4-5 lines): Brutal, funny, specific. Name merchants and amounts.
2. WORST HABIT: One line calling out the biggest problem.
3. 3 SAVINGS TIPS: Specific and practical for India.
4. SAVINGS PREDICTION: How much they could save next month.
5. SCORE: Financial health score /10 with one-line judgement.

Be savage, be real, be memorable."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
        max_tokens=1000
    )

    return response.choices[0].message.content, totals, total_spent, total_received

if __name__ == "__main__":
    from parser import get_transaction_dataframe
    from categorizer import categorize_transactions
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    if path:
        df, _ = get_transaction_dataframe(path)
        categorized = categorize_transactions(df["raw_transaction"].tolist())
        roast, totals, spent, received = generate_roast(categorized)
        print(roast)