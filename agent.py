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
    lang_codes = {
        "Hinglish": "en",
        "English": "en",
        "Hindi": "hi",
        "Tamil": "ta",
        "Telugu": "te",
        "Bengali": "bn",
        "Marathi": "mr",
        "Punjabi": "pa"
    }
    
    gtts_lang = lang_codes.get(language, "en")
    tld = "co.in" if gtts_lang == "en" else "com"

    try:
        tts = gTTS(text=text, lang=gtts_lang, tld=tld, slow=False)
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

    top_categories = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:5]
    top_transactions = sorted(
        [t for t in categorized_transactions if t.get("amount", 0) < 0],
        key=lambda x: abs(x.get("amount", 0)),
        reverse=True
    )[:8]

    totals_text = "\n".join([f"- {cat}: ₹{amt:.0f}" for cat, amt in top_categories])
    tx_text = "\n".join([f"- {t['merchant']}: ₹{abs(t['amount']):.0f} ({t['category']})" for t in top_transactions])

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

    # ── 1. EXPLICITLY DEFINE THE PROMPT ──
    system_prompt = f"""
    You are a highly analytical and empathetic financial coach. Analyze the spending patterns and output your response entirely in {language}.
    {lang_instruction}
    
    You MUST reply in valid JSON format using exactly these keys:
    {{
        "review": "Write exactly 3 distinct bullet points summarizing their financial health. Each bullet point MUST be 15 to 25 words long. You MUST separate each point with double newlines. Format EXACTLY like this: \\n\\n* [First point, 15-25 words.] \\n\\n* [Second point, 15-25 words.] \\n\\n* [Third point, 15-25 words.]",
        
        "worst_habit": "Write exactly 3 distinct bullet points explaining areas for optimization. Each bullet point MUST be 15 to 25 words long. You MUST separate each point with double newlines. Format EXACTLY like this: \\n\\n* [First point, 15-25 words.] \\n\\n* [Second point, 15-25 words.] \\n\\n* [Third point, 15-25 words.]",
        
        "savings_tips": [
            "Write an actionable tip (exactly 15-25 words).",
            "Write an actionable tip (exactly 15-25 words).",
            "Write an actionable tip (exactly 15-25 words)."
        ]
    }}
    CRITICAL INSTRUCTION: You must strictly adhere to the 15-25 word count per point to ensure they are the correct visual length. You MUST use double newlines (\\n\\n) between bullet points in the review and worst_habit strings so the UI renders them on separate lines.
    """
    
    user_prompt = f"Total Spent: ₹{total_spent}\nTotal Received: ₹{total_received}\n\nTop Categories:\n{totals_text}\n\nTop Transactions:\n{tx_text}"

    # ── 2. MAKE THE API CALL ──
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=8192,
            temperature=0.6  # Perfect balance for length and formatting
        )
        
        raw_content = response.choices[0].message.content
        analysis_data = json.loads(raw_content)
        return analysis_data, totals, total_spent, total_received
        
    except Exception as e:
        if "429" in str(e):
            fallback_data = {
                "review": "We've reached our daily processing limit, but from a quick glance, you're doing well.",
                "worst_habit": "We can always optimize discretionary spending.",
                "savings_tips": [
                    "Prioritize essential bills at the start of the month.",
                    "Track small daily UPI transactions—they add up quickly.",
                    "Set aside a small emergency fund, even if it's just ₹500 a month."
                ],
                "financial_health_score": 75
            }
            return fallback_data, totals, total_spent, total_received
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