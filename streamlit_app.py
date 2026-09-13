import os
import random
import base64
import requests
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

API_KEYS = [
    os.getenv("GROQ_KEY_1", ""),
    os.getenv("GROQ_KEY_2", ""),
    os.getenv("GROQ_KEY_3", ""),
    os.getenv("GROQ_KEY_4", ""),
    os.getenv("GROQ_KEY_5", ""),
    os.getenv("GROQ_KEY_6", "")
]

MODEL = "llama-3.2-11b-vision-preview"
URL = "https://api.groq.com/openai/v1/chat/completions"

def get_key():
    return random.choice(API_KEYS)

def web_search(query, num=10):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers, timeout=10)
        results = []
        for line in r.text.split("\n"):
            if 'class="result__title"' in line or 'class="result__snippet"' in line:
                text = line.split(">")[1].split("<")[0] if ">" in line else ""
                if text and len(results) < num:
                    results.append({"title": text, "snippet": "", "link": "#"})
        return results if results else [{"title": "No results", "snippet": "", "link": "#"}]
    except Exception as e:
        return [{"title": "Search error", "snippet": str(e), "link": "#"}]

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp { background: #0a0a0f; }
</style>
"""

st.set_page_config(page_title="STRAFE", initial_sidebar_state="collapsed")
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("⚡ STRAFE")
st.caption("Llama-3.2 Vision + Web Search | Direct & Raw")

uploaded = st.file_uploader("📷 Upload Image (optional)", type=["png", "jpg", "jpeg"])
prompt = st.text_area("Ask STRAFE anything...", height=80)
web_search_on = st.checkbox("🔍 Enable Web Search", value=True)

if st.button(" SEND", use_container_width=True):
    if not prompt and not uploaded:
        st.warning("Add an image or a prompt!")
    else:
        content = []
        if uploaded:
            img_bytes = uploaded.read()
            b64 = base64.b64encode(img_bytes).decode()
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })
        content.append({"type": "text", "text": prompt})
        
        api_messages = [{"role": "user", "content": content}]
        
        headers = {
            "Authorization": f"Bearer {get_key()}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL,
            "messages": api_messages,
            "max_tokens": 1024
        }
        
        with st.spinner(" STRAFE is thinking..."):
            r = requests.post(URL, json=payload, headers=headers, timeout=60)
            result = r.json()
            response_text = result["choices"][0]["message"]["content"]
            
            if web_search_on and "[SEARCH:" in response_text:
                search_query = response_text.split("[SEARCH:")[1].split("]")[0]
                api_messages.append({"role": "assistant", "content": response_text})
                
                with st.status("🔍 Searching the web..."):
                    search_results = web_search(search_query, num_results=10)
                    
                    if search_results and search_results[0]["title"] not in ["No results", "Search error"]:
                        context = "Here are the web search results you requested:\n\n"
                        for res_item in search_results[:10]:
                            context += f"- {res_item['title']}: {res_item['snippet']} (Link: {res_item['link']})\n"
                        context += "\nNow continue your response using this information."
                        
                        api_messages.append({"role": "system", "content": context})
                        
                        headers2 = {
                            "Authorization": f"Bearer {get_key()}",
                            "Content-Type": "application/json"
                        }
                        payload2 = {
                            "model": MODEL,
                            "messages": api_messages,
                            "max_tokens": 1024
                        }
                        r2 = requests.post(URL, json=payload2, headers=headers2, timeout=60)
                        result2 = r2.json()
                        response_text = result2["choices"][0]["message"]["content"]
        
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.markdown(f"** STRAFE:**\n\n{response_text}")