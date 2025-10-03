import os
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def ask_gpt5(prompt, system="You are a medical assistant. Answer concisely."):
    """
    Calls GPT-5 Thinking mini.
    Returns dict: {"text": ..., "raw": ...}
    """
    if not OPENAI_API_KEY:
        return {"text": "GPT-5 placeholder response (set OPENAI_API_KEY to get real responses).", "raw": None}

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-5-thinking-mini",
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0.2
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        assistant_text = data["choices"][0]["message"]["content"].strip()
        return {"text": assistant_text, "raw": data}
    except Exception as e:
        return {"text": f"[GPT call failed: {str(e)}]", "raw": None}
