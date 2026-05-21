import requests


def auto_fix(code):

    prompt = f"""
You are an automatic Python code fixer.

STRICT RULES:
- Fix ALL Python syntax errors
- Fix indentation
- Fix brackets
- Fix misspelled Python functions
- Fix missing colons
- Return ONLY corrected Python code
- Do NOT explain anything
- Do NOT add markdown
- Do NOT add comments
- Do NOT add extra text
- Output must be executable Python only

BROKEN CODE:
{code}
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5-coder:1.5b",
                "prompt": prompt,
                "stream": False
            }
        )

        data = response.json()

        # ---------------- RESPONSE CHECK ----------------

        if "response" in data:

            fixed_code = data["response"]

            # Remove markdown if AI adds it
            fixed_code = fixed_code.replace("```python", "")
            fixed_code = fixed_code.replace("```", "")
            fixed_code = fixed_code.strip()

            return fixed_code

        elif "error" in data:

            return f"# ERROR: {data['error']}"

        else:

            return f"# UNKNOWN RESPONSE: {data}"

    except Exception as e:

        return f"# REQUEST FAILED: {str(e)}"