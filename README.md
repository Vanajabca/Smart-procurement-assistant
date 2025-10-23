# Smart-procurement-assistant
# 💼 Procurement Intelligence Agent 🤖

**Procurement Intelligence Agent** is an **AI-powered decision-support system** that analyzes procurement requests using **policy-based reasoning**, **real-time forex and weather data**, and **Google Gemini AI** to deliver structured recommendations, risk assessments, and compliance insights — all through a modern, interactive **Streamlit dashboard**.

---

## 🚀 Key Features

✅ **AI-Driven Procurement Decisions** – Evaluates procurement requests using Gemini AI reasoning  
📑 **Policy-Aware Analysis** – Extracts and embeds insights from your procurement policy PDF using FAISS + Hugging Face  
💱 **Live Forex Rate Fetching** – Retrieves real-time USD → INR exchange rates via CoinGecko API  
🌦️ **Dynamic Weather Integration** – Uses OpenWeather API to consider environmental context  
🔔 **Automated Alerts** – Sends recommendation summaries to Telegram for quick decision-making  
🎨 **Modern Streamlit Dashboard** – Beautiful gradient UI with metrics and structured decision output  

---

## 🧩 System Architecture

```text
 ┌──────────────────────────────┐
 │ Procurement Request (Input)  │
 └──────────────┬───────────────┘
                │
                ▼
     ┌──────────────────────────┐
     │ Policy PDF Text Extraction│ ← PyPDF2
     └──────────────────────────┘
                │
                ▼
     ┌──────────────────────────┐
     │ Vector Embeddings (FAISS) │ ← HuggingFace Embeddings
     └──────────────────────────┘
                │
                ▼
     ┌──────────────────────────┐
     │ Gemini AI Reasoning Engine│ ← LangChain + Google GenAI
     └──────────────────────────┘
                │
                ▼
     ┌──────────────────────────┐
     │ Streamlit Visualization  │ ← Live Data + Risk Dashboard
     └──────────────────────────┘
                │
                ▼
     ┌──────────────────────────┐
     │ Telegram Notification Bot │
     └──────────────────────────┘
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/yourusername/procurement-intelligence-agent.git
cd procurement-intelligence-agent

2️⃣ Create a Virtual Environment
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create a .env file in your project root and add your API credentials:

GEMINI_API_KEY=your_gemini_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

5️⃣ Run the Application
streamlit run app.py

🧠 How It Works

The user enters a procurement request (e.g., “Should we import 500 equipment units from the USA?”).

The system:

Extracts and indexes content from the procurement policy PDF.

Fetches real-time forex and weather data.

Passes all this context to Gemini AI for structured reasoning.

The AI generates a decision report:

Recommendation

Risk Level (1–5)

Reasoning Summary

Policy Compliance Status

Next Steps

The results are displayed on-screen and sent to Telegram automatically.

🧾 Example Output
Decision: ✅ PROCEED
Risk Level: Low (1)
Reason: The procuremeninstantlwith the AMC policy and current forex rate is favorable.
Policy Compliapliant
Next Steps: Proceed with vendor selection and budget review.

📊 Dashboard Overview
Feature	Description
💱 Live Forex Metrics	Displays USD → INR conversion rate in real-time
🌤️ Weather Status	Shows city-specific temperature and conditions
🧮 AI Decision Panel	Shows recommendation, reasoning, and policy match
📨 Telegram Notifications	Delivers structured recommendation summary instantly.

🧰 Tech Stack

Component	Technology
Frontend / UI	Streamlit
AI Reasoning	Google Gemini via LangChain
Vector DB	FAISS
Embeddings	Hugging Face Sentence Transformers
Document Parsing	PyPDF2
APIs	OpenWeather, CoinGecko, Telegram Bot API
Environment Management	python-dotenv
Utilities	certifi, urllib3, logging, pytz, re

📦 Requirements

Create a requirements.txt with:

streamlit
langchain
langchain-google-genai
langchain-community
langchain-huggingface
PyPDF2
python-dotenv
requests
certifi
urllib3
pytz

🧑‍💻 Author

Developed by: Vanaja S
Powered by: Gemini AI ✨
💡Developed using Google Gemini, LangChain, and Streamlit
