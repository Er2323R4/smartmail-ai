import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from google import genai
from google.genai import types

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def _key(name):
    """Read from Streamlit secrets (deployed) or .env (local)."""
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name)


def _setting(name, default):
    return _key(name) or default


def ask_gemini(system, user):
    client = genai.Client(api_key=_key("GEMINI_API_KEY"))
    resp = client.models.generate_content(
        model=_setting("GEMINI_MODEL", GEMINI_MODEL),
        contents=user,
        config=types.GenerateContentConfig(system_instruction=system),
    )
    return resp.text


def ask_groq(system, user):
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=_key("GROQ_API_KEY"),
    )
    resp = client.chat.completions.create(
        model=_setting("GROQ_MODEL", GROQ_MODEL),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content


MODELS = {"Gemini": ask_gemini, "Groq": ask_groq}


def generate(system, user, provider="Gemini"):
    """Try the chosen model first, then the other. Returns (text, model_used)."""
    order = [provider] + [n for n in MODELS if n != provider]
    errors = []
    for name in order:
        try:
            text = MODELS[name](system, user)
            if text and text.strip():
                return text.strip(), name
            errors.append(f"{name}: empty response")
        except Exception as e:
            errors.append(f"{name}: {str(e)[:250]}")
    raise RuntimeError("All models failed.\n\n" + "\n\n".join(errors))