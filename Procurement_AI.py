import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
import requests
import certifi
import urllib3
import logging
import streamlit as st
import datetime
import pytz
import re
import time

# ----------------------
# SSL / HTTP setup
# ----------------------
os.environ["SSL_CERT_FILE"] = certifi.where()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

# ----------------------
# Load environment variables
# ----------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PDF_PATH = r"C:\Users\vanaja.subramani\AppData\Roaming\Python\Python313\site-packages\PROCUREMENT_POLICY.pdf"

# ----------------------
# Step 1: Extract and Vectorize Policy
# ----------------------
@st.cache_resource
def load_vectorstore():
    def extract_pdf_text(pdf_path):
        reader = PdfReader(pdf_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    embeddings = HuggingFaceEmbeddings(
        model_name=r"C:\Users\vanaja.subramani\AppData\Roaming\Python\Python313\site-packages\models",
        model_kwargs={"device": "cpu", "local_files_only": True}
    )
    pdf_text = extract_pdf_text(PDF_PATH)
    return FAISS.from_texts([pdf_text], embeddings)

vectorstore = load_vectorstore()

# ----------------------
# Step 2: APIs
# ----------------------
def get_forex_rate():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=usd&vs_currencies=inr", verify=False)
        data = response.json()
        return round(data['usd']['inr'], 2)
    except Exception as e:
        return f"Error fetching forex rate: {e}"

def get_weather(city="Chennai"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        if data.get("cod") != 200:
            return {"temp": None, "desc": f"City not found: {city}"}
        return {"temp": data["main"]["temp"], "desc": data["weather"][0]["description"].capitalize()}
    except Exception as e:
        return {"temp": None, "desc": f"Error fetching weather: {e}"}

# ----------------------
# Step 3: AI Reasoning
# ----------------------
def evaluate_purchase(request_text, forex_rate, weather_status):
    llm = ChatGoogleGenerativeAI(api_key=GEMINI_API_KEY, model="gemini-2.0-flash")
    retriever = vectorstore.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

    policy_summary = qa_chain.invoke({"query": request_text})["result"]

    prompt = f"""
Procurement Request: "{request_text}"
Policy Summary: "{policy_summary}"
Forex (USD→INR): {forex_rate}
Weather: {weather_status}

Provide a concise structured procurement recommendation:
- Recommendation
- Risk Level (Low/Medium/High with score 1–5)
- Reason
- Policy Compliance (Compliant / Issues found)
- Next Steps
"""
    response = llm.invoke(prompt)
    if hasattr(response, "content"):
        return response.content
    return str(response)

# ----------------------
# Step 4: Telegram Output
# ----------------------
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for i in range(0, len(message), 4000):
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message[i:i+4000]}, verify=False)

# ----------------------
# Utility: Extract Risk and Decision
# ----------------------
def extract_risk_and_decision(ai_response):
    match = re.search(r"Risk Level.*?(Low|Medium|High).*?(\d)", ai_response, re.IGNORECASE)
    if not match:
        return "Unknown", "REVIEW", "#facc15"
    level, score = match.groups()
    score = int(score)
    if level.lower() == "low" or score <= 2:
        return "Low", "✅ PROCEED", "#0aa037f7"
    elif level.lower() == "medium" or score <= 3:
        return "Medium", "⚠️ NEED REVIEW", "#f1c30d"
    else:
        return "High", "❌ REJECTED", "#f30404"

# ----------------------
# Step 5: Streamlit UI
# ----------------------
st.set_page_config(page_title="Procurement Intelligence AI", page_icon="🤖", layout="wide")

# --- LIGHT THEME STYLING ---
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom right, #e0f7fa, #ffffff);
    color: #1a1a1a;
    font-family: 'Poppins', sans-serif;
}
.header { text-align: center; margin-top: 15px; }
.header h1 { color: #00796b; font-weight: 700; }
.header p { color: #004d40; font-size: 17px; }
textarea { background-color: #f1f8e9 !important; color: #1a1a1a !important; }
.stButton button { background: linear-gradient(90deg, #26a69a, #80cbc4); color: white; font-weight: 600; border-radius: 10px; padding: 10px 25px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>💼Procurement Intelligence Agent 🤖</h1>
    <p>AI-powered procurement insights with real-time forex, weather, and policy analysis</p>
</div>
""", unsafe_allow_html=True)

procurement_request = st.text_area("📦 Enter Procurement Request:", height=120, placeholder="Example: Should we import 500 equipment units from the USA?")
city_input = st.text_input("🌍 Enter City for Weather:", value="Chennai")

if st.button("🚀 Analyze Procurement Decision"):
    if not procurement_request.strip():
        st.warning("Please enter a procurement request.")
    else:
        with st.spinner("🔍 Evaluating policy, forex & weather..."):
            forex_rate = get_forex_rate()
            weather = get_weather(city_input)
            weather_summary = f"{weather['desc']}, {weather['temp']}°C"
            recommendation_text = evaluate_purchase(procurement_request, forex_rate, weather_summary)
            risk_level, decision, color = extract_risk_and_decision(recommendation_text)
            time_now = datetime.datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%B %d, %Y at %I:%M %p")

        # --- LIVE DATA OVERVIEW (Set 2 Style) ---
        st.subheader("📊 Live Data Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="💱 Forex Rate (USD/INR)", value=f"{forex_rate}", delta="Live")
        with col2:
            st.metric(label=f"🌤️ Weather ({city_input})", value=f"{weather['temp']}°C", delta=weather['desc'])
        with col3:
            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            st.metric(label=f"⏰ {current_time.strftime('%b %d, %Y')}", value=current_time.strftime("%I:%M %p"), delta="Updated")
        
        st.write("---")

        # --- COMBINED DECISION + RECOMMENDATION ---
        st.subheader("📋 Procurement Decision")
        st.markdown(f"""
        <div style="background-color:#ffffff; color:#1a1a1a; border-radius:12px; padding:25px; box-shadow:0 4px 15px rgba(0,0,0,0.1);">
            <h3 style="color:{color}; font-weight:700;">Decision: {decision}</h3>
            <p><b>Risk Level:</b> {risk_level}</p>
            <p><b>Generated on:</b> {time_now}</p>
            <hr>
            <div style="text-align:left; color:#1a1a1a;">
                {recommendation_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

        send_telegram_message(recommendation_text)
        st.success("✅ Recommendation & Decision sent to Telegram!")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00796b;'>Developed by Vanaja S | Powered by Gemini AI ✨</p>", unsafe_allow_html=True)
