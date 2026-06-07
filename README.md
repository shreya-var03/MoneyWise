# MoneyWise

**India's Smart and Empathetic AI Finance Coach**

MoneyWise is a localized, privacy-first financial wellness platform designed for Bharat. Instead of merely tracking numbers or criticizing user spending, MoneyWise acts as an empathetic financial mentor. It parses bank statements locally, categorizes transactions using advanced AI, and delivers highly personalized, judgment-free financial coaching in 8 different regional languages.

Every statement uploaded also helps build Adaption, contributing to the next generation of open-source, multilingual financial datasets for India.


## Key Features

* **Empathetic AI Coaching:** Powered by Llama 3.3 (via Groq), the AI distinguishes between essential living costs (healthcare, rent) and discretionary spending, offering supportive, actionable advice instead of generic criticism.
* **True Full-Stack Localization:** Not just translated outputs. The entire UI—from buttons to chart axes to system notifications—instantly localizes into English, Hinglish, Hindi, Bengali, Marathi, Tamil, Telugu, and Punjabi.
* **Privacy-First Architecture:** Bank statements (PDFs) are parsed locally. Personally Identifiable Information (PII) is scrubbed completely before categorized data is ever sent to the LLM.
* **Multilingual Audio Coaching:** Generates localized Text-to-Speech (TTS) audio files so users can listen to their financial review natively.
* **Interactive Analytics:** Clean, dark-mode-optimized Plotly visualizations that break down spending habits seamlessly.
* **Adaption Dataset Contribution:** Anonymized, categorized transaction data is contributed back to a growing, open-source dataset to power the future of Indian financial AI.
* **Pitch-Ready Demo Mode:** One-click demo generation loading 48 pre-configured transactions for flawless, secure live presentations.


## Tech Stack

* **Frontend:** Streamlit (Custom CSS Dark Theme)
* **Backend Data Processing:** Python, Pandas
* **AI Engine:** Groq API (Llama-3.3-70b-versatile)
* **Visualizations:** Plotly Express
* **Audio Processing:** Google Text-to-Speech (gTTS)
* **PDF Parsing:** PyMuPDF / pdfplumber (via custom `parser.py`)


## Project Structure

* `main.py`: The core Streamlit dashboard, UI logic, state management, and master translation dictionary.
* `agent.py`: Handles the prompt engineering, Groq LLM API calls (JSON structured output), and gTTS audio generation.
* `categorizer.py`: Logic for grouping raw transaction strings into clean categories.
* `parser.py`: The local PDF parsing engine that extracts tables and scrubs PII.
* `dataset_builder.py`: Manages the contribution of anonymized transaction data to the Adaption dataset.


## Acknowledgements

MoneyWise relies on robust, language-native data to deliver its coaching. **We would like to expressly credit the Adaption platform**, from which we sourced the foundational linguistic dataset that makes our 8-language localization possible. Their work empowers the next generation of multilingual AI tools for Bharat.


## Why MoneyWise?

Most personal finance apps are either sterile dashboards or judgmental trackers that induce financial anxiety. **MoneyWise bridges the gap between raw data and financial literacy.** By offering empathetic, language-native coaching and acknowledging the reality of essential expenses like medical bills or rent, MoneyWise builds trust with the next billion internet users in India.
