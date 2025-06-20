import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
import openai
import PyPDF2

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

# Load API key from environment or hardcode here
openai.api_key = "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"

# Load PDF content
pocket_text = load_pocket_text()

# Ask GPT with context-restricted answers
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

# Logging quiz attempts
def log_response(step, case, selected, correct, gpt_feedback):
    log_entry = {
        "timestamp": datetime.now(),
        "step": step,
        "case": case,
        "selected": selected,
        "correct": correct,
        "gpt_feedback": gpt_feedback
    }
    df = pd.DataFrame([log_entry])
    if os.path.exists("quiz_log.csv"):
        df.to_csv("quiz_log.csv", mode='a', header=False, index=False)
    else:
        df.to_csv("quiz_log.csv", index=False)

# Streamlit interface setup
st.set_page_config(page_title="SmartRounds: Hyponatremia Tutor", layout="centered")
st.title("🧠 SmartRounds: Hyponatremia Teaching Module")

if "step" not in st.session_state:
    st.session_state.step = 1

def next_step():
    st.session_state.step += 1

# Step 1
if st.session_state.step == 1:
    st.header("Step 1: Serum Osmolality – Classify Hyponatremia")
    st.markdown("""
**Case 1**  
A 70-year-old woman presents with nausea and mild confusion.  
Labs:  
- Serum sodium = 120 mmol/L  
- Serum osmolality = 260 mOsm/kg  

What type of hyponatremia does she have?
""")
    options = [
        "1. Isotonic hyponatremia",
        "2. Hypertonic hyponatremia",
        "3. Hypotonic hyponatremia"
    ]
    correct = "3. Hypotonic hyponatremia"
    selected = st.radio("Choose your answer:", options, key="q1")
    if st.button("Submit", key="submit1"):
        if selected == correct:
            st.success("✅ Correct!")
            explanation = ask_gpt("Why is hyponatremia with sodium 120 and osmolality 260 classified as hypotonic?")
        else:
            st.error("❌ Not quite.")
            explanation = ask_gpt(f"Why is sodium 120 and osmolality 260 not isotonic or hypertonic? They chose: {selected}")
        st.markdown("#### 🧠 GPT Explanation:")
        st.info(explanation)
        log_response("Step 1", "Case 1", selected, selected == correct, explanation)
        st.button("Next", on_click=next_step)

# Step 2
elif st.session_state.step == 2:
    st.header("Step 2: Urine Osmolality – Assess ADH Activity")
    st.markdown("""
**Case 2**  
A 65-year-old man with low sodium has:  
- Serum osmolality = 260  
- Urine osmolality = 80  

What does this suggest about ADH activity?
""")
    options = [
        "1. ADH is not active → suggestive of primary polydipsia or low solute intake",
        "2. ADH is highly active → suggestive of SIADH",
        "3. Urine osmolality is not helpful here"
    ]
    correct = options[0]
    selected = st.radio("Choose your answer:", options, key="q2")
    if st.button("Submit", key="submit2"):
        if selected == correct:
            st.success("✅ Correct!")
            explanation = ask_gpt("Why does urine osmolality of 80 indicate ADH is not active?")
        else:
            st.error("❌ Try again.")
            explanation = ask_gpt(f"Why is ADH not considered active with urine osmolality of 80? They chose: {selected}")
        st.markdown("#### 🧠 GPT Explanation:")
        st.info(explanation)
        log_response("Step 2", "Case 2", selected, selected == correct, explanation)
        st.button("Next", on_click=next_step)

# Step 3
elif st.session_state.step == 3:
    st.header("Step 3: Urine Sodium – Assess Volume Status")
    st.markdown("""
**Case 3**  
A 75-year-old woman has low sodium.  
Findings:  
- Serum osmolality = 260  
- Urine osmolality = 500  
- Urine sodium = 10  
She has dry mucous membranes and orthostatic hypotension.

What is the likely volume status?
""")
    options = [
        "1. Hypovolemia → low urine Na due to RAAS activation",
        "2. SIADH → low urine Na",
        "3. Volume status unclear without weight"
    ]
    correct = options[0]
    selected = st.radio("Choose your answer:", options, key="q3")
    if st.button("Submit", key="submit3"):
        if selected == correct:
            st.success("✅ Correct!")
            explanation = ask_gpt("Why do low urine sodium and orthostatic symptoms suggest hypovolemia?")
        else:
            st.error("❌ Think RAAS.")
            explanation = ask_gpt(f"Why does low urine sodium in this case not suggest SIADH? They chose: {selected}")
        st.markdown("#### 🧠 GPT Explanation:")
        st.info(explanation)
        log_response("Step 3", "Case 3", selected, selected == correct, explanation)
        st.button("Next", on_click=next_step)

# Step 4 – Summary Table
elif st.session_state.step == 4:
    st.header("Step 4: Diagnostic Framework Summary (From Pocket Nephrology)")
    st.markdown("""
| **Test**              | **Finding**                        | **Interpretation**                                       |
|-----------------------|-------------------------------------|-----------------------------------------------------------|
| Serum Osm             | > 295                              | Hypertonic hyponatremia (e.g., hyperglycemia, mannitol)   |
|                       | 275–295                            | Isotonic (pseudohyponatremia: lab artifact)               |
|                       | < 275                              | Hypotonic → proceed to next step                          |
| Urine Osm             | < 100                              | ADH not active → primary polydipsia, low solute intake    |
|                       | > 100                              | ADH active → volume depletion, SIADH, endocrine causes     |
| Urine Na              | < 20                               | Volume depletion (vomiting, diarrhea, diuretics early)    |
|                       | > 40                               | SIADH, adrenal insufficiency, hypothyroidism              |
""")
    st.success("📘 This table reflects the Pocket Nephrology stepwise approach to diagnosing hyponatremia.")
    st.button("Next: Final Quiz & Survey", on_click=next_step)

# Step 5 – Final Quiz
elif st.session_state.step == 5:
    st.header("Step 5: Final Quiz & Feedback")
    st.markdown("""
🎉 You’ve completed the guided hyponatremia module!  

Now test your knowledge and share feedback:

📌 [Take the Final Quiz](https://docs.google.com/forms/d/e/1FAIpQLSctPN-os8uZJc0Iwvpq4iafBuB-H600e5jqgDJBtk-AYrnRvg/viewform?usp=header)  
📌 [Complete the Feedback Survey](https://docs.google.com/forms/d/e/1FAIpQLSctPN-os8uZJc0Iwvpq4iafBuB-H600e5jqgDJBtk-AYrnRvg/viewform?usp=header)

To help us improve:
- In ChatGPT, click ⋮ > "Share & Export"
- Paste the session link in the survey form

Thank you for participating!
""")

# GPT Follow-up Box
st.markdown("#### 💬 Still have questions?")
followup = st.text_input("Ask GPT to clarify something based on this case:")
if st.button("Ask"):
    if followup.strip():
        followup_response = ask_gpt(followup)
        st.markdown("#### 🧠 GPT Follow-up Answer:")
        st.info(followup_response)
    else:
        st.warning("Please type a question before clicking Ask.")
