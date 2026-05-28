import streamlit as st
import os
from dotenv import load_dotenv
from parser import get_transaction_dataframe
from categorizer import categorize_transactions
from agent import generate_roast
from dataset_builder import add_to_dataset, count_dataset_rows, get_dataset_stats
import tempfile
import pandas as pd

load_dotenv()

st.set_page_config(
    page_title="RupeeRoast 🔥",
    page_icon="🔥",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0a0a 0%, #111111 50%, #0d0d0d 100%);
    color: #ffffff;
}

/* hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* hero section */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem 1rem;
}
.hero-title {
    font-size: 4rem;
    font-weight: 900;
    background: linear-gradient(135deg, #ff6b35, #ff4444, #ff6b35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #888888;
    margin-bottom: 0.5rem;
}
.hero-tagline {
    font-size: 0.95rem;
    color: #555555;
    font-style: italic;
}

/* upload card */
.upload-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
}

/* metric cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}
.metric-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}
.metric-label {
    font-size: 0.75rem;
    color: #666666;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
}
.metric-value.red { color: #ff4444; }
.metric-value.green { color: #44ff88; }
.metric-value.yellow { color: #ffcc44; }

/* roast box */
.roast-container {
    background: linear-gradient(135deg, #1a0a0a, #1a1010);
    border: 1px solid #ff444433;
    border-left: 4px solid #ff4444;
    border-radius: 12px;
    padding: 1.8rem;
    margin: 1.5rem 0;
    position: relative;
}
.roast-header {
    font-size: 0.75rem;
    color: #ff4444;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 1rem;
    font-weight: 600;
}
.roast-text {
    font-size: 1rem;
    line-height: 1.8;
    color: #dddddd;
    white-space: pre-line;
}

/* section headers */
.section-header {
    font-size: 0.75rem;
    color: #555555;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 600;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1f1f1f;
}

/* category pills */
.category-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* badge */
.badge {
    background: #ff444422;
    color: #ff4444;
    border: 1px solid #ff444444;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 1rem;
}

/* buttons */
.stButton > button {
    background: linear-gradient(135deg, #ff4444, #ff6b35) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    letter-spacing: 1px !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(255, 68, 68, 0.4) !important;
}

/* label text */
.stSelectbox label, .stFileUploader label {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 1px !important;
}

p, label, .stMarkdown p {
    color: #e2e8f0 !important;
}

/* file uploader */
.stFileUploader > div {
    background: #1a1a1a !important;
    border: 2px dashed #2a2a2a !important;
    border-radius: 12px !important;
}
.stFileUploader > div:hover {
    border-color: #ff4444 !important;
}

/* dataframe */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* divider */
hr { border-color: #1f1f1f !important; }

/* spinner */
.stSpinner > div { border-top-color: #ff4444 !important; }

/* success/info boxes */
.stSuccess {
    background: #0a1a0a !important;
    border: 1px solid #44ff8844 !important;
    border-radius: 10px !important;
}
.stInfo {
    background: #0a0a1a !important;
    border: 1px solid #4444ff44 !important;
    border-radius: 10px !important;
}

/* chart */
.stBarChart { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;900&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

/* animated gradient background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    background-size: 400% 400%;
    animation: gradientShift 8s ease infinite;
    color: #ffffff;
    min-height: 100vh;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* grid overlay for robotic feel */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: 
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* hero */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem 1rem;
    position: relative;
}
.hero-title {
    font-size: 4.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #ff6b35, #ff4444, #ff8c69, #ffcc44);
    background-size: 300% 300%;
    animation: gradientShift 3s ease infinite;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.5rem;
    letter-spacing: -2px;
}
.hero-subtitle {
    font-size: 1.15rem;
    color: #a78bfa;
    margin-bottom: 0.4rem;
    font-weight: 600;
}
.hero-tagline {
    font-size: 0.9rem;
    color: #6b7280;
    font-style: italic;
}

/* glowing badge */
.badge {
    background: linear-gradient(135deg, #ff444422, #a78bfa22);
    color: #a78bfa;
    border: 1px solid #a78bfa44;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 1rem;
    letter-spacing: 1px;
    box-shadow: 0 0 20px #a78bfa22;
}

/* glowing divider */
.glow-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #ff4444, #a78bfa, transparent);
    margin: 2rem 0;
    border: none;
}

/* metric cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}
.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.4rem;
    text-align: center;
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #ff4444, #a78bfa);
}
.metric-label {
    font-size: 0.7rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.6rem;
    font-weight: 600;
}
.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
}
.metric-value.red { color: #ff4444; text-shadow: 0 0 20px #ff444466; }
.metric-value.green { color: #34d399; text-shadow: 0 0 20px #34d39966; }
.metric-value.yellow { color: #fbbf24; text-shadow: 0 0 20px #fbbf2466; }

/* roast box */
.roast-container {
    background: linear-gradient(135deg, rgba(255,68,68,0.08), rgba(167,139,250,0.08));
    border: 1px solid rgba(255,68,68,0.25);
    border-left: 4px solid #ff4444;
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 40px rgba(255,68,68,0.1);
    position: relative;
    overflow: hidden;
}
.roast-container::after {
    content: '🔥';
    position: absolute;
    top: 1rem;
    right: 1.5rem;
    font-size: 2rem;
    opacity: 0.3;
}
.roast-header {
    font-size: 0.7rem;
    color: #ff4444;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 1rem;
    font-weight: 700;
}
.roast-text {
    font-size: 1rem;
    line-height: 1.9;
    color: #e5e7eb;
    white-space: pre-line;
}

/* section headers */
.section-header {
    font-size: 0.7rem;
    color: #a78bfa;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-weight: 700;
    margin: 2.5rem 0 1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(167,139,250,0.2);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* robotic terminal style tip box */
.tip-box {
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(52,211,153,0.3);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    font-family: 'Space Grotesk', monospace;
    font-size: 0.9rem;
    color: #34d399;
    position: relative;
}
.tip-box::before {
    content: '>';
    margin-right: 8px;
    color: #34d399;
    font-weight: 700;
}

/* buttons */
.stButton > button {
    background: linear-gradient(135deg, #ff4444, #a78bfa) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem 2rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(255,68,68,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 35px rgba(255,68,68,0.5) !important;
}

/* selectbox */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 12px !important;
    color: white !important;
    backdrop-filter: blur(10px) !important;
    font-weight: 600 !important;
}

.stSelectbox > div > div > div {
    color: white !important;
    font-weight: 600 !important;
}

[data-baseweb="select"] * {
    color: white !important;
}

[data-baseweb="popover"] {
    background: #1e1b4b !important;
    border: 1px solid rgba(167,139,250,0.4) !important;
    border-radius: 12px !important;
}

[data-baseweb="menu"] {
    background: #1e1b4b !important;
    border-radius: 12px !important;
}

[data-baseweb="option"] {
    background: #1e1b4b !important;
    color: white !important;
    font-weight: 500 !important;
    padding: 10px 16px !important;
}

[data-baseweb="option"]:hover {
    background: rgba(167,139,250,0.2) !important;
    color: white !important;
}

/* file uploader */
.stFileUploader > div {
    background: rgba(255,255,255,0.03) !important;
    border: 2px dashed rgba(167,139,250,0.4) !important;
    border-radius: 16px !important;
    transition: all 0.3s ease !important;
}
.stFileUploader > div:hover {
    border-color: #ff4444 !important;
    background: rgba(255,68,68,0.05) !important;
}

/* progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #ff4444, #a78bfa) !important;
    border-radius: 10px !important;
}

/* dataframe */
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* success */
.stSuccess {
    background: rgba(52,211,153,0.08) !important;
    border: 1px solid rgba(52,211,153,0.3) !important;
    border-radius: 12px !important;
    color: #34d399 !important;
}

/* info */
.stInfo {
    background: rgba(167,139,250,0.08) !important;
    border: 1px solid rgba(167,139,250,0.3) !important;
    border-radius: 12px !important;
}

/* spinner */
.stSpinner > div {
    border-top-color: #a78bfa !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(#ff4444, #a78bfa);
    border-radius: 3px;
}
</style>
""", unsafe_allow_html=True)

# ── CONTROLS ──────────────────────────────────────────
col1, col2 = st.columns([1, 1])
with col1:
    language = st.selectbox(
    "🌐 Roast Language",
    ["Hinglish", "English", "Hindi", "Tamil", "Telugu", "Bengali", "Marathi", "Punjabi"],
    index=0
)
with col2:
    tone = st.selectbox(
        "🌶️ Savage Level",
        ["Brutal 💀", "Savage 🔥", "Gentle 😊"],
        index=1
    )

uploaded_file = st.file_uploader(
    "📄 Drop your bank statement PDF here",
    type=["pdf"],
    help="Supports HDFC, ICICI, SBI, Paytm UPI statements"
)

if uploaded_file is not None:
    with st.spinner("📖 Reading your financial crimes..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        df, raw_text = get_transaction_dataframe(tmp_path)
        os.unlink(tmp_path)

    st.success(f"✅ Found **{len(df)} transactions** ready to be judged")

    if st.button("🔥 ROAST MY FINANCES", use_container_width=True):

        progress = st.progress(0, text="Categorizing your chaos...")
        
        with st.spinner("🤖 AI is studying your bad decisions..."):
            transactions = df["raw_transaction"].tolist()
            progress.progress(30, text="Categorizing transactions...")
            categorized = categorize_transactions(transactions)
            progress.progress(70, text="Crafting your roast...")
            
            # pass tone to agent
            tone_map = {"Brutal 💀": "absolutely brutal and unhinged", "Savage 🔥": "savage and funny", "Gentle 😊": "gentle but honest"}
            roast, totals, total_spent, total_received = generate_roast(categorized, language=language)
            dataset_count = add_to_dataset(categorized)
            progress.progress(100, text="Done!")
            progress.empty()

        net = total_received - total_spent

        # ── METRICS ──
        st.markdown('<div class="section-header">💸 Your Financial Report Card</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Spent</div>
                <div class="metric-value red">₹{total_spent:,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Received</div>
                <div class="metric-value green">₹{total_received:,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Net Balance</div>
                <div class="metric-value {'green' if net >= 0 else 'red'}">₹{net:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── CHART ──
        st.markdown('<div class="section-header">📊 Where Your Money Escaped To</div>', unsafe_allow_html=True)
        if totals:
            chart_df = pd.DataFrame(
                list(totals.items()),
                columns=["Category", "Amount"]
            ).sort_values("Amount", ascending=False)
            st.bar_chart(chart_df.set_index("Category"), color="#ff4444")

        # ── ROAST ──
        st.markdown('<div class="section-header">🔥 Your Roast</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="roast-container">
            <div class="roast-header">⚡ RupeeRoast AI — Financial Intervention</div>
            <div class="roast-text">{roast}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── TOP SPENDS ──
        st.markdown('<div class="section-header">💀 Your Biggest Sins</div>', unsafe_allow_html=True)
        if categorized:
            tx_df = pd.DataFrame(categorized)
            tx_df = tx_df[tx_df["amount"] < 0].copy()
            tx_df["amount"] = tx_df["amount"].abs()
            tx_df = tx_df.sort_values("amount", ascending=False).head(10)
            tx_df["amount"] = tx_df["amount"].apply(lambda x: f"₹{x:,.2f}")
            tx_df.columns = [c.title() for c in tx_df.columns]
            st.dataframe(
                tx_df,
                use_container_width=True,
                hide_index=True
            )

        # dataset contribution
        st.markdown('<div class="section-header">🌐 Adaption Dataset Contribution</div>', unsafe_allow_html=True)
        stats = get_dataset_stats()
        if stats:
            col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", stats["total_records"])
        with col2:
            st.metric("Unique Merchants", stats["unique_merchants"])
        with col3:
            st.metric("Multilingual Entries", stats["multilingual_coverage"])
        if 'dataset_count' in dir():
            st.success(f"✅ Your statement added **{dataset_count} records** to the RupeeRoast multilingual dataset — powering India's financial AI!")
        else:
            st.success(f"✅ Dataset has **{stats['total_records']} records** powering India's financial AI!")

        # ── SHARE ──
        st.markdown('<div class="section-header">📱 Spread the Pain</div>', unsafe_allow_html=True)
        st.info("💀 Screenshot this and send it to your equally broke friends. Misery loves company.")
        
        
        