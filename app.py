import streamlit as st
import pandas as pd
import os
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv
import openai
import PyPDF2

# Load environment variables
load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"]
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_REPO = os.getenv("GITHUB_REPO")

# Load PDF content from local file
def load_pocket_text(pdf_path="Hyponatremia_PocketNephrology_Pages218_225.pdf"):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"Error loading PDF: {e}"

pocket_text = load_pocket_text()

def ask_gpt(user_input):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a nephrology tutor. Only use the following text as your source:\n\n" + pocket_text},
            {"role": "user", "content": user_input}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

def push_to_github(file_name, file_content):
    try:
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/logs/{file_name}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        message = f"Add session log {file_name}"
        data = {
            "message": message,
            "content": base64.b64encode(file_content.encode()).decode("utf-8")
        }
        response = requests.put(url, json=data, headers=headers)
        if response.status_code == 201:
            return "✅ Session log uploaded to GitHub."
        else:
            return f"❌ Failed to upload log: {response.json()}"
    except Exception as e:
        return f"❌ GitHub upload error: {e}"

st.set_page_config(page_title="Hyponatremia GPT Tutor", layout="centered")
st.title("💬 Hyponatremia Learning Module (GPT Tutor)")

if "step" not in st.session_state:
    st.session_state.step = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "responses" not in st.session_state:
    st.session_state.responses = []
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = True

if st.session_state.show_sidebar:
    with st.sidebar:
        st.header("📋 Navigation")
        for i, (case_text, _) in enumerate([
            ("Step 1", ""),
            ("Step 2", ""),
            ("Step 3", ""),
            ("Step 4", ""),
            ("Bonus Case", ""),
            ("Challenge Case", "")
        ]):
            if st.button(case_text, key=f"sidebar_{i}"):
                st.session_state.step = i

def next_step():
    st.session_state.step += 1

def run_case(case_text, question_prompt):
    st.markdown(case_text)
    user_input = st.text_input("Your response:", key=f"input_{st.session_state.step}")
    if st.button("Submit", key=f"submit_{st.session_state.step}"):
        gpt_response = ask_gpt(question_prompt + "\nUser answer: " + user_input)
        st.session_state.chat_history.append((user_input, gpt_response))
        st.session_state.responses.append({
            "step": st.session_state.step,
            "case": case_text,
            "answer": user_input,
            "feedback": gpt_response,
            "timestamp": datetime.now().isoformat()
        })
        st.markdown("#### 🧠 GPT Feedback:")
        st.info(gpt_response)
        takehome = ask_gpt("Give a one-line take-home point for:\n" + gpt_response)
        st.markdown("**📌 Take-home Point:**")
        st.success(takehome)
        st.button("Next", on_click=next_step)

step_prompts = [
    ("""🔹 Step 1 – Classify Hyponatremia by Serum Osmolality\n\n**Case 1A:**\nA 60-year-old man presents with fatigue and poor appetite.\nNa: 128, Glucose: 100, Serum Osm: 285 mOsm/kg\n\nHow would you classify his hyponatremia?""", "Classify the hyponatremia based on osmolality."),
    ("""🔹 Step 2 – Urine Osmolality: Assess ADH Activity\n\n**Case 2A:**\n70F with Na 118, Serum Osm 250, Urine Osm 90 mOsm/kg\n\nWhat does this urine osmolality suggest about ADH activity?""", "Interpret ADH activity from urine osmolality of 90 mOsm/kg."),
    ("""🔹 Step 3 – Urine Sodium: Assess Volume Status\n\n**Case 3A:**\n50M, Serum Osm 260, Urine Osm 450, Urine Na 10, BP 100/65, K 2.8\n\nWhat is the most likely cause of hyponatremia?""", "Diagnose cause based on urine sodium and volume status."),
    ("""🔹 Step 4 – Endocrine Evaluation\n\n**Case 3B:**\n65F on prednisone, Na 125, K 5.0, Cortisol 1.5, TSH normal\nUrine Osm 620, Urine Na 60\n\nWhat is the most likely cause of her hyponatremia?""", "Interpret this endocrine profile in the setting of hyponatremia."),
    ("""🔹 Bonus Case\n\n**Case 4:**\n45F on carbamazepine, Na 122, Serum Osm 260, Urine Osm 550, Urine Na 55\nCortisol and TSH normal\n\nWhat is the likely cause?""", "Explain diagnosis based on labs and carbamazepine use."),
    ("""🔹 Challenge Case\n\n**Case 5:**\n55M with cirrhosis, Na 124, Serum Osm 255, Urine Osm 480, Urine Na 10\nAscites and leg edema present.\n\nWhat is the cause of hyponatremia?""", "Explain why this case is hypervolemic hyponatremia.")
]

if st.session_state.step < len(step_prompts):
    case_text, prompt = step_prompts[st.session_state.step]
    run_case(case_text, prompt)
else:
    st.success("🎉 You've completed the GPT-based module!")
    st.markdown("""
✅ [Final Quiz Link](https://docs.google.com/forms/d/e/1FAIpQLSez8wsB11GlxQQXZJTcg9f4Tl2UVWVVOfIyaJ5DAvBf--ZjGg/viewform)  
✅ [Feedback Survey](https://docs.google.com/forms/d/e/1FAIpQLSctPN-os8uZJc0Iwvpq4iafBuB-H600e5jqgDJBtk-AYrnRvg/viewform)
    """)
    df = pd.DataFrame(st.session_state.responses)
    st.download_button("📥 Download Session Log", df.to_csv(index=False), file_name="hyponatremia_session_log.csv")

    if st.button("📤 Upload Session Log to GitHub"):
        filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        result = push_to_github(filename, df.to_csv(index=False))
        st.info(result)

    st.markdown("#### 💬 Still have questions?")
    followup = st.text_input("Ask GPT something else:", key="followup")
    if st.button("Ask GPT", key="ask_followup"):
        if followup.strip():
            answer = ask_gpt(followup)
            st.markdown("#### 🧠 GPT says:")
            st.info(answer)
        else:
            st.warning("Please enter a question.")
