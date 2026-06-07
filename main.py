import streamlit as st
import os
import tempfile
import pandas as pd
import json

from dotenv import load_dotenv
from parser import get_transaction_dataframe
from categorizer import categorize_transactions
from agent import generate_roast
from dataset_builder import add_to_dataset, count_dataset_rows, get_dataset_stats

st.set_page_config(
    page_title="MoneyWise | AI Finance Coach",
    page_icon="💡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── GLOBAL LOCALIZATION DICTIONARY ──
translations = {
    "English": {
        "subtitle": "India's Smart & Empathetic AI Finance Coach",
        "tagline": "Upload your statement. Get actionable insights. Build your wealth.",
        "upload": "📄 Drop your bank statement PDF here",
        "demo": "🚀 Load Demo Statement (Safe for Live Pitch)",
        "analyze": "🌱 ANALYZE MY FINANCES",
        "spinner": "🤖 AI is carefully reviewing your financial patterns...",
        "report_card_header": "💸 Your Financial Report Card",
        "total_spent": "Total Spent",
        "total_received": "Total Received",
        "net_balance": "Net Balance",
        "chart_header": "📊 Where Your Money Escaped To",
        "insights_header": "✨ Your Financial Insights",
        "optimization_key": "⚠️ Key Area for Optimization:",
        "actionable_steps": "💡 Actionable Steps",
        "top_expenditures": "💸 Top Expenditures",
        "merchant": "Merchant",
        "category": "Category",
        "amount": "Amount",
        "dataset_header": "🌐 Adaption Dataset Contribution",
        "total_records": "Total Records",
        "unique_merchants": "Unique Merchants",
        "dataset_size": "Dataset Size",
        "languages_label": "Languages",
        "rows": "rows",
        "contribution_success": "✅ Your statement added **{} records** to the MoneyWise multilingual dataset — powering India's financial AI!",
        "dataset_generic": "✅ Dataset is powering India's financial AI!",
        "footer_1": "MoneyWise contributes categorized financial records to the <strong style='color: #a78bfa;'>Adaption</strong> platform.",
        "footer_2": "Empowering the next generation of multilingual AI datasets for Bharat. 🇮🇳",
        "demo_loaded": "✅ Demo data loaded! 48 transactions ready to pitch.",
        "analyzing_securely": "📊 Analyzing your spending patterns securely...",
        "found_transactions": "✅ Found **{} transactions** successfully loaded",
        "progress_start": "Categorizing your transactions thoughtfully...",
        "progress_mid": "Categorizing transactions...",
        "audio_prep": "🎙️ Preparing your personalized audio coaching session...",
        "categories": {
            "Groceries": "Groceries", "Food": "Food", "Entertainment": "Entertainment", 
            "Transport": "Transport", "Salary": "Salary", "Shopping": "Shopping", 
            "Utilities": "Utilities", "Healthcare": "Healthcare", "Miscellaneous": "Miscellaneous"
        }
    },
    "Hinglish": {
        "subtitle": "India ka Smart & Empathetic AI Finance Coach",
        "tagline": "Apna statement upload karo. Actionable insights pao. Wealth build karo.",
        "upload": "📄 Apna bank statement PDF yahan drop karein",
        "demo": "🚀 Demo Statement Load Karo (Pitch Safe)",
        "analyze": "🌱 MERI FINANCES ANALYZE KARO",
        "spinner": "🤖 AI aapke financial patterns ko dhyaan se review kar raha hai...",
        "report_card_header": "💸 Aapka Financial Report Card",
        "total_spent": "Total Kharcha",
        "total_received": "Total Aamdani",
        "net_balance": "Net Balance",
        "chart_header": "📊 Paisa Kahan Gaya?",
        "insights_header": "✨ Aapke Financial Insights",
        "optimization_key": "⚠️ Dhyan Dene Wali Baat:",
        "actionable_steps": "💡 Actionable Steps",
        "top_expenditures": "💸 Sabse Bade Kharche",
        "merchant": "Merchant",
        "category": "Category",
        "amount": "Amount",
        "dataset_header": "🌐 Adaption Dataset Contribution",
        "total_records": "Total Records",
        "unique_merchants": "Unique Merchants",
        "dataset_size": "Dataset Size",
        "languages_label": "Languages",
        "rows": "rows",
        "contribution_success": "✅ Aapke statement ne MoneyWise dataset mein **{} records** add kiye — India ke financial AI ko power karte hue!",
        "dataset_generic": "✅ Dataset India ke financial AI ko power kar raha hai!",
        "footer_1": "MoneyWise apne records <strong style='color: #a78bfa;'>Adaption</strong> platform ko contribute karta hai.",
        "footer_2": "Bharat ke multilingual AI datasets ko empower karte hue. 🇮🇳",
        "demo_loaded": "✅ Demo data loaded! 48 transactions pitch ke liye ready hain.",
        "analyzing_securely": "📊 Aapke spending patterns securely analyze ho rahe hain...",
        "found_transactions": "✅ **{} transactions** successfully load ho gaye",
        "progress_start": "Aapke transactions categorize kiye jaa rahe hain...",
        "progress_mid": "Transactions categorize ho rahe hain...",
        "audio_prep": "🎙️ Aapka personalized audio coaching session prepare ho raha hai...",
        "categories": {
            "Groceries": "Kirana", "Food": "Khana", "Entertainment": "Entertainment", 
            "Transport": "Transport", "Salary": "Salary", "Shopping": "Shopping", 
            "Utilities": "Bills", "Healthcare": "Dawayaan", "Miscellaneous": "Baaki Kharcha"
        }
    },
    "Hindi": {
        "subtitle": "भारत का स्मार्ट और एम्पैथेटिक AI फाइनेंस कोच",
        "tagline": "अपना स्टेटमेंट अपलोड करें। सही दिशा पाएं। अपनी संपत्ति बढ़ाएं।",
        "upload": "📄 अपना बैंक स्टेटमेंट PDF यहाँ ड्रॉप करें",
        "demo": "🚀 डेमो स्टेटमेंट लोड करें (लाइव पिच के लिए सुरक्षित)",
        "analyze": "🌱 मेरे वित्त का विश्लेषण करें",
        "spinner": "🤖 AI आपके वित्तीय पैटर्न की सावधानीपूर्वक समीक्षा कर रहा है...",
        "report_card_header": "💸 आपका वित्तीय रिपोर्ट कार्ड",
        "total_spent": "कुल खर्च",
        "total_received": "कुल प्राप्तियां",
        "net_balance": "शुद्ध शेष",
        "chart_header": "📊 आपका पैसा कहाँ गया",
        "insights_header": "✨ आपके वित्तीय इनसाइट्स",
        "optimization_key": "⚠️ सुधार का मुख्य क्षेत्र:",
        "actionable_steps": "💡 उठाए जाने वाले कदम",
        "top_expenditures": "💸 सबसे बड़े खर्चे",
        "merchant": "व्यापारी",
        "category": "श्रेणी",
        "amount": "रकम",
        "dataset_header": "🌐 एडॉप्शन डेटासेट योगदान",
        "total_records": "कुल रिकॉर्ड",
        "unique_merchants": "अद्वितीय व्यापारी",
        "dataset_size": "डेटासेट आकार",
        "languages_label": "भाषाएं",
        "rows": "पंक्तियाँ",
        "contribution_success": "✅ आपके स्टेटमेंट ने MoneyWise बहुभाषी डेटासेट में **{} रिकॉर्ड** जोड़े — भारत के वित्तीय AI को सशक्त बनाते हुए!",
        "dataset_generic": "✅ डेटासेट भारत के वित्तीय AI को सशक्त बना रहा है!",
        "footer_1": "MoneyWise वर्गीकृत वित्तीय रिकॉर्ड <strong style='color: #a78bfa;'>Adaption</strong> प्लेटफॉर्म को योगदान करता है।",
        "footer_2": "भारत के लिए बहुभाषी AI डेटासेट की अगली पीढ़ी को सशक्त बनाना। 🇮🇳",
        "demo_loaded": "✅ डेमो डेटा लोड हो गया! 48 ट्रांजेक्शन पिच के लिए तैयार हैं।",
        "analyzing_securely": "📊 आपके खर्च करने के पैटर्न का सुरक्षित रूप से विश्लेषण किया जा रहा है...",
        "found_transactions": "✅ **{} ट्रांजेक्शन** सफलतापूर्वक लोड हो गए",
        "progress_start": "आपके ट्रांजेक्शन्स को विचारपूर्वक वर्गीकृत किया जा रहा है...",
        "progress_mid": "ट्रांजेक्शन्स को वर्गीकृत किया जा रहा है...",
        "audio_prep": "🎙️ आपका व्यक्तिगत ऑडियो कोचिंग सत्र तैयार किया जा रहा है...",
        "categories": {
            "Groceries": "किराना", "Food": "भोजन", "Entertainment": "मनोरंजन", 
            "Transport": "परिवहन", "Salary": "वेतन", "Shopping": "खरीदारी", 
            "Utilities": "उपयोगिताएँ", "Healthcare": "स्वास्थ्य सेवा", "Miscellaneous": "अन्य"
        }
    },
    "Bengali": {
        "subtitle": "ভারতের স্মার্ট এবং এমপ্যাথেটিক এআই ফাইন্যান্স কোচ",
        "tagline": "আপনার স্টেটমেন্ট আপলোড করুন। সঠিক অন্তর্দৃষ্টি পান। আপনার সম্পদ গড়ে তুলুন।",
        "upload": "📄 আপনার ব্যাঙ্ক স্টেটমেন্ট PDF এখানে ড্রপ করুন",
        "demo": "🚀 ডেমো স্টেটমেন্ট লোড করুন (লাইভ পিচের জন্য নিরাপদ)",
        "analyze": "🌱 আমার ফাইন্যান্স বিশ্লেষণ করুন",
        "spinner": "🤖 AI আপনার আর্থিক ধরনগুলি মনোযোগ সহকারে পর্যালোচনা করছে...",
        "report_card_header": "💸 আপনার আর্থিক রিপোর্ট কার্ড",
        "total_spent": "মোট খরচ",
        "total_received": "মোট প্রাপ্তি",
        "net_balance": "নেট ব্যালেন্স",
        "chart_header": "📊 আপনার টাকা কোথায় গেল",
        "insights_header": "✨ আপনার আর্থিক অন্তর্দৃষ্টি",
        "optimization_key": "⚠️ উন্নতির মূল ক্ষেত্র:",
        "actionable_steps": "💡 পদক্ষেপযোগ্য উপায়",
        "top_expenditures": "💸 শীর্ষ ব্যয়",
        "merchant": "মার্চেন্ট",
        "category": "বিভাগ",
        "amount": "পরিমাণ",
        "dataset_header": "🌐 অ্যাডাপশন ডেটাসেট অবদান",
        "total_records": "মোট রেকর্ড",
        "unique_merchants": "অনন্য মার্চেন্ট",
        "dataset_size": "ডেটাসেট আকার",
        "languages_label": "ভাষা",
        "rows": "সারি",
        "contribution_success": "✅ আপনার স্টেটমেন্ট MoneyWise ডেটাসেটে **{} রেকর্ড** যোগ করেছে — ভারতের এআই-কে শক্তিশালী করে!",
        "dataset_generic": "✅ ডেটাসেট ভারতের আর্থিক এআই-কে শক্তিশালী করছে!",
        "footer_1": "MoneyWise <strong style='color: #a78bfa;'>Adaption</strong> প্ল্যাটফর্মে আর্থিক রেকর্ড অবদান রাখে।",
        "footer_2": "ভারতের জন্য বহুভাষিক এআই ডেটাসেটের পরবর্তী প্রজন্মকে ক্ষমতায়ন করা হচ্ছে। 🇮🇳",
        "demo_loaded": "✅ ডেমো ডেটা লোড হয়েছে! 48টি লেনদেন পিচের জন্য প্রস্তুত।",
        "analyzing_securely": "📊 আপনার খরচের ধরন নিরাপদে বিশ্লেষণ করা হচ্ছে...",
        "found_transactions": "✅ **{}টি লেনদেন** সফলভাবে লোড হয়েছে",
        "progress_start": "আপনার লেনদেনগুলি সাবধানে শ্রেণীবদ্ধ করা হচ্ছে...",
        "progress_mid": "লেনদেনগুলি শ্রেণীবদ্ধ করা হচ্ছে...",
        "audio_prep": "🎙️ আপনার ব্যক্তিগতকৃত অডিও কোচিং সেশন প্রস্তুত করা হচ্ছে...",
        "categories": {
            "Groceries": "মুদি", "Food": "খাবার", "Entertainment": "বিনোদন", 
            "Transport": "পরিবহন", "Salary": "বেতন", "Shopping": "কেনাকাটা", 
            "Utilities": "ইউটিলিটি", "Healthcare": "স্বাস্থ্যসেবা", "Miscellaneous": "অন্যান্য"
        }
    },
    "Marathi": {
        "subtitle": "भारताचा स्मार्ट आणि एम्पॅथेटिक एआय फायनान्स कोच",
        "tagline": "तुमचे स्टेटमेंट अपलोड करा. योग्य मार्गदर्शन मिळवा. तुमची संपत्ती वाढवा.",
        "upload": "📄 तुमचे बँक स्टेटमेंट PDF येथे ड्रॉप करा",
        "demo": "🚀 डेमो स्टेटमेंट लोड करा (लाइव्ह पिचसाठी सुरक्षित)",
        "analyze": "🌱 माझ्या वित्ताचे विश्लेषण करा",
        "spinner": "🤖 AI तुमच्या आर्थिक सवयींचे काळजीपूर्वक पुनरावलोकन करत आहे...",
        "report_card_header": "💸 तुमचे आर्थिक रिपोर्ट कार्ड",
        "total_spent": "एकूण खर्च",
        "total_received": "एकूण जमा",
        "net_balance": "निव्वळ शिल्लक",
        "chart_header": "📊 तुमचे पैसे कुठे गेले",
        "insights_header": "✨ तुमचे आर्थिक विश्लेषण",
        "optimization_key": "⚠️ सुधारणेचे मुख्य क्षेत्र:",
        "actionable_steps": "💡 करण्यासारख्या गोष्टी",
        "top_expenditures": "💸 सर्वाधिक खर्च",
        "merchant": "व्यापारी",
        "category": "श्रेणी",
        "amount": "रक्कम",
        "dataset_header": "🌐 अडॉप्शन डेटासेट योगदान",
        "total_records": "एकूण रेकॉर्ड",
        "unique_merchants": "अद्वितीय व्यापारी",
        "dataset_size": "डेटासेट आकार",
        "languages_label": "भाषा",
        "rows": "ओळी",
        "contribution_success": "✅ तुमच्या स्टेटमेंटने MoneyWise डेटासेटमध्ये **{} रेकॉर्ड** जोडले — भारताच्या आर्थिक AI ला सामर्थ्यवान बनवत आहे!",
        "dataset_generic": "✅ डेटासेट भारताच्या आर्थिक AI ला सामर्थ्यवान बनवत आहे!",
        "footer_1": "MoneyWise <strong style='color: #a78bfa;'>Adaption</strong> प्लॅटफॉर्मवर आर्थिक रेकॉर्डचे योगदान देते.",
        "footer_2": "भारतासाठी बहुभाषिक AI डेटासेटच्या पुढील पिढीचे सक्षमीकरण. 🇮🇳",
        "demo_loaded": "✅ डेमो डेटा लोड झाला! 48 व्यवहार पिचसाठी तयार आहेत.",
        "analyzing_securely": "📊 तुमच्या खर्चाच्या पद्धतींचे सुरक्षितपणे विश्लेषण केले जात आहे...",
        "found_transactions": "✅ **{} व्यवहार** यशस्वीरित्या लोड झाले",
        "progress_start": "तुमच्या व्यवहारांचे विचारपूर्वक वर्गीकरण केले जात आहे...",
        "progress_mid": "व्यवहारांचे वर्गीकरण केले जात आहे...",
        "audio_prep": "🎙️ तुमचे वैयक्तिकृत ऑडिओ कोचिंग सत्र तयार केले जात आहे...",
        "categories": {
            "Groceries": "किराणा", "Food": "अन्न", "Entertainment": "मनोरंजन", 
            "Transport": "वाहतूक", "Salary": "पगार", "Shopping": "खरेदी", 
            "Utilities": "उपयुक्तता", "Healthcare": "आरोग्य सेवा", "Miscellaneous": "इतर"
        }
    },
    "Tamil": {
        "subtitle": "இந்தியாவின் ஸ்மார்ட் மற்றும் அக்கறையுள்ள AI நிதி பயிற்சியாளர்",
        "tagline": "உங்கள் அறிக்கையைப் பதிவேற்றவும். செயல்படக்கூடிய நுண்ணறிவுகளைப் பெறுங்கள். உங்கள் செல்வத்தை உருவாக்குங்கள்.",
        "upload": "📄 உங்கள் வங்கி அறிக்கை PDF ஐ இங்கே விடவும்",
        "demo": "🚀 டெமோ அறிக்கையை ஏற்றவும் (நேரடி பிட்ச்சிற்கு பாதுகாப்பானது)",
        "analyze": "🌱 எனது நிதிகளை பகுப்பாய்வு செய்",
        "spinner": "🤖 AI உங்கள் நிதி முறைகளை கவனமாக மதிப்பாய்வு செய்கிறது...",
        "report_card_header": "💸 உங்கள் நிதி அறிக்கை அட்டை",
        "total_spent": "மொத்த செலவு",
        "total_received": "மொத்த வரவு",
        "net_balance": "நிகர இருப்பு",
        "chart_header": "📊 உங்கள் பணம் எங்கே சென்றது",
        "insights_header": "✨ உங்கள் நிதி நுண்ணறிவுகள்",
        "optimization_key": "⚠️ மேம்படுத்துவதற்கான முக்கிய பகுதி:",
        "actionable_steps": "💡 எடுக்க வேண்டிய நடவடிக்கைகள்",
        "top_expenditures": "💸 அதிக செலவுகள்",
        "merchant": "வியாபாரி",
        "category": "வகை",
        "amount": "தொகை",
        "dataset_header": "🌐 அடாப்ஷன் தரவுத்தொகுப்பு பங்களிப்பு",
        "total_records": "மொத்த பதிவுகள்",
        "unique_merchants": "தனித்துவமான வியாபாரிகள்",
        "dataset_size": "தரவுத்தொகுப்பு அளவு",
        "languages_label": "மொழிகள்",
        "rows": "வரிசைகள்",
        "contribution_success": "✅ உங்கள் அறிக்கை MoneyWise தரவுத்தொகுப்பில் **{} பதிவுகளைச்** சேர்த்துள்ளது!",
        "dataset_generic": "✅ தரவுத்தொகுப்பு இந்தியாவின் நிதி AI ஐ மேம்படுத்துகிறது!",
        "footer_1": "MoneyWise <strong style='color: #a78bfa;'>Adaption</strong> தளத்திற்கு நிதி பதிவுகளை வழங்குகிறது.",
        "footer_2": "பாரதத்திற்கான பன்மொழி AI தரவுத்தொகுப்புகளின் அடுத்த தலைமுறையை மேம்படுத்துகிறது. 🇮🇳",
        "demo_loaded": "✅ டெமோ தரவு ஏற்றப்பட்டது! 48 பரிவர்த்தனைகள் பிட்ச்சிற்கு தயார்.",
        "analyzing_securely": "📊 உங்கள் செலவு முறைகள் பாதுகாப்பாக பகுப்பாய்வு செய்யப்படுகின்றன...",
        "found_transactions": "✅ **{} பரிவர்த்தனைகள்** வெற்றிகரமாக ஏற்றப்பட்டன",
        "progress_start": "உங்கள் பரிவர்த்தனைகள் கவனமாக வகைப்படுத்தப்படுகின்றன...",
        "progress_mid": "பரிவர்த்தனைகள் வகைப்படுத்தப்படுகின்றன...",
        "audio_prep": "🎙️ உங்கள் தனிப்பயனாக்கப்பட்ட ஆடியோ பயிற்சி அமர்வு தயாராகிறது...",
        "categories": {
            "Groceries": "மளிகை", "Food": "உணவு", "Entertainment": "பொழுதுபோக்கு", 
            "Transport": "போக்குவரத்து", "Salary": "சம்பளம்", "Shopping": "ஷாப்பிங்", 
            "Utilities": "பயன்பாடுகள்", "Healthcare": "சுகாதாரம்", "Miscellaneous": "மற்றவை"
        }
    },
    "Telugu": {
        "subtitle": "భారతదేశపు స్మార్ట్ మరియు సానుభూతిగల AI ఫైనాన్స్ కోచ్",
        "tagline": "మీ స్టేట్‌మెంట్‌ను అప్‌లోడ్ చేయండి. కార్యాచరణ అంతర్దృష్టులను పొందండి. మీ సంపదను పెంచుకోండి.",
        "upload": "📄 మీ బ్యాంక్ స్టేట్‌మెంట్ PDFని ఇక్కడ వదలండి",
        "demo": "🚀 డెమో స్టేట్‌మెంట్‌ను లోడ్ చేయండి (లైవ్ పిచ్ కోసం సురక్షితం)",
        "analyze": "🌱 నా ఫైనాన్స్‌ను విశ్లేషించండి",
        "spinner": "🤖 AI మీ ఆర్థిక నమూనాలను జాగ్రత్తగా సమీక్షిస్తోంది...",
        "report_card_header": "💸 మీ ఆర్థిక నివేదిక కార్డ్",
        "total_spent": "మొత్తం ఖర్చు",
        "total_received": "మొత్తం ఆదాయం",
        "net_balance": "నికర బ్యాలెన్స్",
        "chart_header": "📊 మీ డబ్బు ఎక్కడికి వెళ్ళింది",
        "insights_header": "✨ మీ ఆర్థిక అంతర్దృష్టులు",
        "optimization_key": "⚠️ ఆప్టిమైజేషన్ కోసం ముఖ్యమైన ప్రాంతం:",
        "actionable_steps": "💡 తీసుకోదగిన చర్యలు",
        "top_expenditures": "💸 అత్యధిక ఖర్చులు",
        "merchant": "వ్యాపారి",
        "category": "వర్గం",
        "amount": "మొత్తం",
        "dataset_header": "🌐 అడాప్షన్ డేటాసెట్ సహకారం",
        "total_records": "మొత్తం రికార్డులు",
        "unique_merchants": "ప్రత్యేక వ్యాపారులు",
        "dataset_size": "డేటాసెట్ పరిమాణం",
        "languages_label": "భాషలు",
        "rows": "వరుసలు",
        "contribution_success": "✅ మీ స్టేట్‌మెంట్ MoneyWise డేటాసెట్‌కు **{} రికార్డులను** జోడించింది!",
        "dataset_generic": "✅ డేటాసెట్ భారతదేశ ఆర్థిక AI ని శక్తివంతం చేస్తుంది!",
        "footer_1": "MoneyWise <strong style='color: #a78bfa;'>Adaption</strong> ప్లాట్‌ఫారమ్‌కు ఆర్థిక రికార్డులను అందిస్తుంది.",
        "footer_2": "భారత్ కోసం బహుభాషా AI డేటాసెట్‌ల భవిష్యత్తు తరానికి సాధికారత. 🇮🇳",
        "demo_loaded": "✅ డెమో డేటా లోడ్ చేయబడింది! 48 లావాదేవీలు పిచ్ కోసం సిద్ధంగా ఉన్నాయి.",
        "analyzing_securely": "📊 మీ ఖర్చు విధానాలు సురక్షితంగా విశ్లేషించబడుతున్నాయి...",
        "found_transactions": "✅ **{} లావాదేవీలు** విజయవంతంగా లోడ్ చేయబడ్డాయి",
        "progress_start": "మీ లావాదేవీలు జాగ్రత్తగా వర్గీకరించబడుతున్నాయి...",
        "progress_mid": "లావాదేవీలు వర్గీకరించబడుతున్నాయి...",
        "audio_prep": "🎙️ మీ వ్యక్తిగతీకరించిన ఆడియో కోచింగ్ సెషన్ సిద్ధమవుతోంది...",
        "categories": {
            "Groceries": "కిరాణా", "Food": "ఆహారం", "Entertainment": "వినోదం", 
            "Transport": "రవాణా", "Salary": "జీతం", "Shopping": "షాపింగ్", 
            "Utilities": "యుటిలిటీస్", "Healthcare": "ఆరోగ్య సంరక్షణ", "Miscellaneous": "ఇతర"
        }
    },
    "Punjabi": {
        "subtitle": "ਭਾਰਤ ਦਾ ਸਮਾਰਟ ਅਤੇ ਹਮਦਰਦ AI ਫਾਈਨਾਂਸ ਕੋਚ",
        "tagline": "ਆਪਣੀ ਸਟੇਟਮੈਂਟ ਅਪਲੋਡ ਕਰੋ। ਕਾਰਵਾਈਯੋਗ ਸੂਝ ਪ੍ਰਾਪਤ ਕਰੋ। ਆਪਣੀ ਦੌਲਤ ਬਣਾਓ।",
        "upload": "📄 ਆਪਣੀ ਬੈਂਕ ਸਟੇਟਮੈਂਟ PDF ਇੱਥੇ ਛੱਡੋ",
        "demo": "🚀 ਡੈਮੋ ਸਟੇਟਮੈਂਟ ਲੋਡ ਕਰੋ (ਲਾਈਵ ਪਿਚ ਲਈ ਸੁਰੱਖਿਅਤ)",
        "analyze": "🌱 ਮੇਰੇ ਵਿੱਤ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ",
        "spinner": "🤖 AI ਤੁਹਾਡੇ ਵਿੱਤੀ ਪੈਟਰਨਾਂ ਦੀ ਧਿਆਨ ਨਾਲ ਸਮੀਖਿਆ ਕਰ ਰਿਹਾ ਹੈ...",
        "report_card_header": "💸 ਤੁਹਾਡਾ ਵਿੱਤੀ ਰਿਪੋਰਟ ਕਾਰਡ",
        "total_spent": "ਕੁੱਲ ਖਰਚ",
        "total_received": "ਕੁੱਲ ਆਮਦਨ",
        "net_balance": "ਸ਼ੁੱਧ ਬਕਾਇਆ",
        "chart_header": "📊 ਤੁਹਾਡਾ ਪੈਸਾ ਕਿੱਥੇ ਗਿਆ",
        "insights_header": "✨ ਤੁਹਾਡੀਆਂ ਵਿੱਤੀ ਸੂਝਾਂ",
        "optimization_key": "⚠️ ਸੁਧਾਰ ਦਾ ਮੁੱਖ ਖੇਤਰ:",
        "actionable_steps": "💡 ਚੁੱਕਣ ਯੋਗ ਕਦਮ",
        "top_expenditures": "💸 ਸਭ ਤੋਂ ਵੱਡੇ ਖਰਚੇ",
        "merchant": "ਵਪਾਰੀ",
        "category": "ਸ਼੍ਰੇਣੀ",
        "amount": "ਰਕਮ",
        "dataset_header": "🌐 ਅਡਾਪਸ਼ਨ ਡੇਟਾਸੈਟ ਯੋਗਦਾਨ",
        "total_records": "ਕੁੱਲ ਰਿਕਾਰਡ",
        "unique_merchants": "ਵਿਲੱਖਣ ਵਪਾਰੀ",
        "dataset_size": "ਡੇਟਾਸੈਟ ਆਕਾਰ",
        "languages_label": "ਭਾਸ਼ਾਵਾਂ",
        "rows": "ਕਤਾਰਾਂ",
        "contribution_success": "✅ ਤੁਹਾਡੀ ਸਟੇਟਮੈਂਟ ਨੇ MoneyWise ਡੇਟਾਸੈਟ ਵਿੱਚ **{} ਰਿਕਾਰਡ** ਸ਼ਾਮਲ ਕੀਤੇ!",
        "dataset_generic": "✅ ਡੇਟਾਸੈਟ ਭਾਰਤ ਦੇ ਵਿੱਤੀ AI ਨੂੰ ਸ਼ਕਤੀ ਪ੍ਰਦਾਨ ਕਰ ਰਿਹਾ ਹੈ!",
        "footer_1": "MoneyWise <strong style='color: #a78bfa;'>Adaption</strong> ਪਲੇਟਫਾਰਮ ਨੂੰ ਵਿੱਤੀ ਰਿਕਾਰਡ ਪ੍ਰਦਾਨ ਕਰਦਾ ਹੈ।",
        "footer_2": "ਭਾਰਤ ਲਈ ਬਹੁ-ਭਾਸ਼ਾਈ AI ਡੇਟਾਸੈਟਾਂ ਦੀ ਅਗਲੀ ਪੀੜ੍ਹੀ ਨੂੰ ਸ਼ਕਤੀ ਪ੍ਰਦਾਨ ਕਰਨਾ। 🇮🇳",
        "demo_loaded": "✅ ਡੈਮੋ ਡੇਟਾ ਲੋਡ ਹੋ ਗਿਆ! 48 ਟ੍ਰਾਂਜੈਕਸ਼ਨ ਪਿਚ ਲਈ ਤਿਆਰ ਹਨ।",
        "analyzing_securely": "📊 ਤੁਹਾਡੇ ਖਰਚੇ ਦੇ ਪੈਟਰਨਾਂ ਦਾ ਸੁਰੱਖਿਅਤ ਢੰਗ ਨਾਲ ਵਿਸ਼ਲੇਸ਼ਣ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ...",
        "found_transactions": "✅ **{} ਟ੍ਰਾਂਜੈਕਸ਼ਨ** ਸਫਲਤਾਪੂਰਵਕ ਲੋਡ ਹੋ ਗਏ",
        "progress_start": "ਤੁਹਾਡੇ ਟ੍ਰਾਂਜੈਕਸ਼ਨਾਂ ਨੂੰ ਧਿਆਨ ਨਾਲ ਸ਼੍ਰੇਣੀਬੱਧ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ...",
        "progress_mid": "ਟ੍ਰਾਂਜੈਕਸ਼ਨਾਂ ਨੂੰ ਸ਼੍ਰੇਣੀਬੱਧ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ...",
        "audio_prep": "🎙️ ਤੁਹਾਡਾ ਵਿਅਕਤੀਗਤ ਆਡੀਓ ਕੋਚਿੰਗ ਸੈਸ਼ਨ ਤਿਆਰ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ...",
        "categories": {
            "Groceries": "ਕਰਿਆਨੇ", "Food": "ਭੋਜਨ", "Entertainment": "ਮਨੋਰੰਜਨ", 
            "Transport": "ਆਵਾਜਾਈ", "Salary": "ਤਨਖਾਹ", "Shopping": "ਖਰੀਦਦਾਰੀ", 
            "Utilities": "ਉਪਯੋਗਤਾਵਾਂ", "Healthcare": "ਸਿਹਤ ਸੰਭਾਲ", "Miscellaneous": "ਹੋਰ"
        }
    }
}

# ── SIDEBAR SETTINGS ──
with st.sidebar:
    st.markdown("### ⚙️ Coach Settings")
    language = st.selectbox(
        "🌐 App Language", 
        ["English", "Hindi", "Hinglish", "Bengali", "Marathi", "Tamil", "Telugu", "Punjabi"]
    )
    tone = st.selectbox(
        "🌱 Coaching Style", 
        ["Supportive 💚", "Direct & Honest ⚖️", "Motivational 🚀"]
    )

# Lock in the current language translations (defaults to English if not found)
t = translations.get(language, translations["English"])

# Single, merged hero section keeping the badge and the new positive branding
st.markdown(f"""
<div class="hero">
    <div style="margin-bottom:1rem">
        <span class="badge">🇮🇳 Built for Bharat • Powered by Adaptive Data</span>
    </div>
    <div class="hero-title">
        MoneyWise <span style="-webkit-text-fill-color: initial; color: initial;">💡</span>
    </div>
    <div class="hero-subtitle">{t['subtitle']}</div>
    <div class="hero-tagline">{t['tagline']}</div>
</div>
""", unsafe_allow_html=True)

# ── MASTER CSS INJECTION ──
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
#MainMenu, footer { visibility: hidden; }

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

uploaded_file = st.file_uploader(
    t['upload'], 
    type=["pdf"],
    help="Supports HDFC, ICICI, SBI, Paytm UPI statements. PII is scrubbed locally."
)

use_demo = st.button(t['demo'], use_container_width=True)

# ── 1. FILE UPLOAD & MEMORY MANAGEMENT ──
if use_demo:
    demo_transactions = [
        "12/05/2026 UPI-ZOMATO [UPI_REDACTED] -450",
        "13/05/2026 UPI-SWIGGY [UPI_REDACTED] -600",
        "14/05/2026 NEFT CR SALARY TECH CORP 85000",
        "15/05/2026 UPI-BLINKIT [UPI_REDACTED] -1200",
        "18/05/2026 UPI-BOOKMYSHOW [UPI_REDACTED] -800",
        "20/05/2026 UPI-UBER [UPI_REDACTED] -350"
    ] * 8 
    
    st.session_state['active_df'] = pd.DataFrame(demo_transactions, columns=["raw_transaction"])
    
    # Wipe old analysis from memory when loading new data
    st.session_state['analyze_clicked'] = False
    if 'categorized_data' in st.session_state: del st.session_state['categorized_data']
    if 'last_settings' in st.session_state: del st.session_state['last_settings']
    st.success(t["demo_loaded"])

elif uploaded_file is not None:
    # Check memory to prevent re-parsing the PDF on every widget click!
    # Check memory to prevent re-parsing the PDF on every widget click!
    if 'last_uploaded' not in st.session_state or st.session_state['last_uploaded'] != uploaded_file.name:
        with st.spinner(t["analyzing_securely"]):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
                
            parsed_df, raw_text = get_transaction_dataframe(tmp_path)
            os.unlink(tmp_path)
            
            st.session_state['active_df'] = parsed_df
            st.session_state['last_uploaded'] = uploaded_file.name
            
            # Wipe old analysis from memory
            st.session_state['analyze_clicked'] = False
            if 'categorized_data' in st.session_state: del st.session_state['categorized_data']
            if 'last_settings' in st.session_state: del st.session_state['last_settings']
            
        st.success(t["found_transactions"].format(len(parsed_df)))
    else:
        st.success(t["found_transactions"].format(len(st.session_state['active_df'])))

# ── 2. DASHBOARD EXECUTION & RENDERING ──
if 'active_df' in st.session_state and not st.session_state['active_df'].empty:
    
    # When clicked, tell memory that the dashboard should be visible
    if st.button(t['analyze'], use_container_width=True): 
        st.session_state['analyze_clicked'] = True
        
    # If the dashboard is flagged as visible in memory, keep rendering it!
    if st.session_state.get('analyze_clicked', False):
        df = st.session_state['active_df']
        
        # STEP A: Categorize Transactions (Runs strictly ONCE per file)
        if 'categorized_data' not in st.session_state:
            progress = st.progress(0, text=t["progress_start"])
            transactions = df["raw_transaction"].tolist()
            progress.progress(30, text=t["progress_mid"])
            
            st.session_state['categorized_data'] = categorize_transactions(transactions)
            st.session_state['dataset_count'] = add_to_dataset(st.session_state['categorized_data']) 
            progress.empty()

        # STEP B: Generate AI Insights (Runs ONLY if Language/Tone changes)
        current_settings = f"{language}_{tone}"
        if 'analysis_data' not in st.session_state or st.session_state.get('last_settings') != current_settings:
            with st.spinner(t['spinner']):
                categorized = st.session_state['categorized_data']
                
                tone_map = {
                    "Supportive 💚": "warm and supportive", 
                    "Direct & Honest ⚖️": "direct and honest", 
                    "Motivational 🚀": "highly motivational"
                }
                
                analysis_data, totals, total_spent, total_received = generate_roast(categorized, language=language)
                
                # Save the new translations into memory
                st.session_state['analysis_data'] = analysis_data
                st.session_state['totals'] = totals
                st.session_state['total_spent'] = total_spent
                st.session_state['total_received'] = total_received
                st.session_state['last_settings'] = current_settings

        # ── PULL DATA FROM MEMORY TO RENDER UI ──
        categorized = st.session_state['categorized_data']
        analysis_data = st.session_state['analysis_data']
        totals = st.session_state['totals']
        total_spent = st.session_state['total_spent']
        total_received = st.session_state['total_received']
        net = total_received - total_spent

        # ── METRICS ──
        st.markdown(f'<div class="section-header">{t["report_card_header"]}</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">{t["total_spent"]}</div>
                <div class="metric-value red">₹{total_spent:,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">{t["total_received"]}</div>
                <div class="metric-value green">₹{total_received:,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">{t["net_balance"]}</div>
                <div class="metric-value {'green' if net >= 0 else 'red'}">₹{net:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── CHART ──
        st.markdown(f'<div class="section-header">{t["chart_header"]}</div>', unsafe_allow_html=True)
        if totals:
            chart_df = pd.DataFrame(
                list(totals.items()),
                columns=[t["category"], t["amount"]]
            ).sort_values(t["amount"], ascending=False)
        
            # BULLETPROOF TRANSLATION LOGIC (Cleans hidden AI spaces before translating)
            chart_df[t["category"]] = chart_df[t["category"]].astype(str).str.strip().str.title()
            chart_df[t["category"]] = chart_df[t["category"]].apply(lambda x: t.get("categories", {}).get(x, x))

            import plotly.express as px
            fig = px.bar(
                chart_df,
                x=t["category"],
                y=t["amount"],
                color_discrete_sequence=["#a78bfa"],
            )
            # Add translated axis titles
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.03)",
                font_color="#ffffff",
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#aaaaaa"), title=t["category"]),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#aaaaaa"), title=t["amount"]),
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, key="unique_spending_chart_123")

        # ── 1. TEXT OUTPUT ──
        st.markdown(f"""
        <div class="roast-container">
            <h3 style='color: #a78bfa; margin-top: 0;'>{t["insights_header"]}</h3>
            <p style='line-height: 1.6; font-size: 1.1rem;'>{analysis_data.get('review', 'Analysis complete.')}</p>
            <hr style='border-color: rgba(167, 139, 250, 0.2); margin: 1.5rem 0;'>
            <p><strong>{t["optimization_key"]}</strong> {analysis_data.get('worst_habit', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        # ── 2. SAVINGS TIPS LOOP ──
        st.markdown(f"<h4 style='padding-top: 1rem;'>{t['actionable_steps']}</h4>", unsafe_allow_html=True)
        for tip in analysis_data.get('savings_tips', []):
            st.info(f"✅ {tip}")

        # ── 3. AUDIO REVIEW ──
        with st.spinner(t["audio_prep"]):
            from agent import generate_audio
            review_text = analysis_data.get('review', '')
            clean_text_for_audio = review_text.replace("**", "")
            
            audio_path = generate_audio(clean_text_for_audio, language)
            
            if audio_path:
                st.audio(audio_path, format="audio/mp3")
                os.unlink(audio_path)

        # ── TOP SPENDS ──
        st.markdown(f'<div class="section-header">{t["top_expenditures"]}</div>', unsafe_allow_html=True)
        if categorized:
            tx_df = pd.DataFrame(categorized)
            tx_df = tx_df[tx_df["amount"] < 0].copy()
            tx_df["amount"] = tx_df["amount"].abs()
            tx_df = tx_df.sort_values("amount", ascending=False).head(10)
            tx_df = tx_df[["merchant", "category", "amount"]].copy()
            tx_df["amount"] = tx_df["amount"].apply(lambda x: f"₹{x:,.2f}")
            
            # BULLETPROOF TRANSLATION LOGIC (Cleans hidden AI spaces before translating)
            tx_df["category"] = tx_df["category"].astype(str).str.strip().str.title()
            tx_df["category"] = tx_df["category"].apply(lambda x: t.get("categories", {}).get(x, x))
            
            # Set the column headers
            tx_df.columns = [t["merchant"], t["category"], t["amount"]]
            st.dataframe(tx_df, use_container_width=True, hide_index=True)

        # ── DATASET CONTRIBUTION ──
        st.markdown(f'<div class="section-header">{t["dataset_header"]}</div>', unsafe_allow_html=True)
        stats = get_dataset_stats()
        if stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t["total_records"], stats["total_records"])
            with col2:
                st.metric(t["unique_merchants"], stats["unique_merchants"])
            with col3:
                st.metric(t["dataset_size"], f"{stats['total_records']} {t['rows']}")
                st.metric(t["languages_label"], "14 🇮🇳")
                
        if 'dataset_count' in st.session_state:
            st.success(t["contribution_success"].format(st.session_state['dataset_count']))
        else:
            st.success(t["dataset_generic"])

        # ── FOOTER / CREDITS ──
        st.markdown(f"""
        <div class="glow-divider"></div>
        <div style="text-align: center; padding: 2rem 0; color: #6b7280; font-size: 0.85rem;">
            <p>{t["footer_1"]}</p>
            <p style="font-size: 0.75rem; opacity: 0.7;">{t["footer_2"]}</p>
        </div>
        """, unsafe_allow_html=True)