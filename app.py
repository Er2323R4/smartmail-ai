import streamlit as st
from prompts import TONES, write_prompt, rewrite_prompt, SUMMARY_SYSTEM
from llm import generate
from checker import check_text

st.set_page_config(page_title="SmartMail AI", page_icon="✉️", layout="centered")
st.title("SmartMail AI")
st.caption("Turn quick notes into professional emails in seconds.")

with st.sidebar:
    st.header("Settings")
    provider = st.radio("AI model", ["Gemini", "Groq"])
    use_checker = st.checkbox("Spelling & grammar check", value=True)
    st.info("Please do not paste confidential or personal information.")


def show_result(text, used):
    """Run the grammar check, then display the result."""
    changes = []
    if use_checker:
        text, changes = check_text(text)
    st.success(f"Done, written by {used}")
    st.code(text, language=None, wrap_lines=True)  # built-in copy button
    if changes:
        with st.expander(f"{len(changes)} correction(s) applied"):
            for c in changes:
                st.write("•", c)


tab1, tab2, tab3 = st.tabs(["Write an email", "Rewrite my text", "Summarize a thread"])

# ---------- Tab 1: write ----------
with tab1:
    recipient = st.text_input("Who is this email for?", placeholder="e.g. my lecturer, a client")
    intent = st.text_input("What is the goal?", placeholder="e.g. request a deadline extension")
    points = st.text_area("Key points (one per line)", height=150,
                          placeholder="- I was sick last week\n- Need 3 more days for the report")
    tone = st.selectbox("Tone", list(TONES.keys()), key="tone_write")

    if st.button("Generate email", type="primary"):
        if not points.strip():
            st.warning("Please enter at least one key point.")
        else:
            user_msg = f"Recipient: {recipient}\nGoal: {intent}\nKey points:\n{points}"
            with st.spinner("Writing your email..."):
                try:
                    text, used = generate(write_prompt(tone), user_msg, provider)
                    show_result(text, used)
                except Exception as e:
                    st.error(str(e))

# ---------- Tab 2: rewrite ----------
with tab2:
    original = st.text_area("Paste the text you want to improve", height=200)
    tone2 = st.selectbox("Rewrite in this tone", list(TONES.keys()), key="tone_rewrite")

    if st.button("Rewrite", type="primary"):
        if not original.strip():
            st.warning("Please paste some text first.")
        else:
            with st.spinner("Rewriting..."):
                try:
                    text, used = generate(rewrite_prompt(tone2), original, provider)
                    show_result(text, used)
                except Exception as e:
                    st.error(str(e))

# ---------- Tab 3: summarize ----------
with tab3:
    thread = st.text_area("Paste the email thread", height=250)

    if st.button("Summarize", type="primary"):
        if not thread.strip():
            st.warning("Please paste an email thread first.")
        else:
            with st.spinner("Reading the thread..."):
                try:
                    summary, used = generate(SUMMARY_SYSTEM, thread, provider)
                    st.success(f"Done, written by {used}")
                    st.markdown(summary)
                except Exception as e:
                    st.error(str(e))