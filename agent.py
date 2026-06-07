import os
import json
import tempfile

from gtts import gTTS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_audio(text, language):
    """Converts the text review into a playable audio file with the correct accent."""
    
    # Map your UI languages to gTTS language codes
    lang_codes = {
        "Hinglish": "en", # Indian English accent
        "English": "en",
        "Hindi": "hi",
        "Tamil": "ta",
        "Telugu": "te",
        "Bengali": "bn",
        "Marathi": "mr",
        "Punjabi": "pa"
    }
    
    # Default to Indian English ('co.in') if not found, else use the specific language
    gtts_lang = lang_codes.get(language, "en")
    tld = "co.in" if gtts_lang == "en" else "com"

    try:
        # Create the audio object
        tts = gTTS(text=text, lang=gtts_lang, tld=tld, slow=False)
        
        # Save to a temporary file
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio.name)
        return temp_audio.name
    except Exception as e:
        print(f"Audio generation failed: {e}")
        return None

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
        "Hinglish": "Respond in Hinglish — a warm, supportive mix of Hindi and English.",
        "English": "Respond in English.",
        "Tamil": "Respond entirely in Tamil script.",
        "Telugu": "Respond entirely in Telugu script.",
        "Bengali": "Respond entirely in Bengali (Bangla) script.",
        "Marathi": "Respond entirely in Marathi (Devanagari script).",
        "Punjabi": "Respond entirely in Punjabi (Gurmukhi script).",
    }.get(language, "Respond in English.")

    prompt = f"""
You are an empathetic, insightful, and encouraging financial coach specializing in Indian personal finance. 
Analyze the following summary of transactions and provide a constructive financial review.

CRITICAL RULES:
1. Distinguish between fixed/essential needs (Rent, Insurance, Medical, Utilities) and discretionary lifestyle wants (Zomato, Swiggy, Clubs, Shopping).
2. NEVER criticize or judge spending on healthcare, medicine, rent, education, or family support. Acknowledge these as vital responsibilities.
3. Focus your constructive feedback entirely on optimization—where they can cut back on unnecessary subscriptions, dining out, or impulsive UPI spending without sacrificing their quality of life.
4. Keep the tone warm, motivational, and culturally relatable to a young Indian user. {lang_instruction}

Spending summary:
Total Spent: ₹{total_spent:.0f} | Total Received: ₹{total_received:.0f}

Top categories:
{totals_text}

Biggest transactions:
{tx_text}

You must respond strictly with a valid JSON object matching this schema:
{{
    "review": "A paragraph of warm, constructive feedback highlighting what they are doing right, validating their essential expenses, and gently pointing out where they can save.",
    "worst_habit": "Identify the primary category of discretionary leakage (e.g., 'Late-night food ordering micro-transactions'). If none exists, highlight a positive saving habit.",
    "savings_tips": [
        "Constructive tip 1 focused on mindful spending.",
        "Constructive tip 2 focused on smart budgeting tools.",
        "Constructive tip 3 focused on long-term wealth building."
    ],
    "financial_health_score": 85
}}
"""
   
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, # Lowered temperature for perfect JSON stability
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        raw_content = response.choices[0].message.content
        analysis_data = json.loads(raw_content)
        
        return analysis_data, totals, total_spent, total_received
        
    except Exception as e:
        if "429" in str(e):
            fallback_data = {
                "review": "We've reached our daily processing limit, but from a quick glance, you're managing your core expenses well. Remember that spending on essentials like health, education, and rent is an investment in your well-being.",
                "worst_habit": "We can always optimize discretionary spending like food delivery or impulse shopping.",
                "savings_tips": [
                    "Prioritize essential bills at the start of the month.",
                    "Track small daily UPI transactions—they add up quickly.",
                    "Set aside a small emergency fund, even if it's just ₹500 a month."
                ],
                "financial_health_score": 75
            }
            return fallback_data, totals, total_spent, total_received
        
        # If it's NOT a 429, we safely raise the original exception
        raise e

if __name__ == "__main__":
    from parser import get_transaction_dataframe
    from categorizer import categorize_transactions
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    if path:
        df, _ = get_transaction_dataframe(path)
        categorized = categorize_transactions(df["raw_transaction"].tolist())
        analysis_data, totals, spent, received = generate_roast(categorized)
        print(json.dumps(analysis_data, indent=2))