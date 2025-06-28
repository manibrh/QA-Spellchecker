import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def run_spellcheck_ai(segments):
    issues = []
    for segment in segments:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a localization QA specialist. "
                            "Identify spelling or grammar issues in the provided text. "
                            "Only report real issues, and skip segments that are fine."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Check this text: {segment}"
                    }
                ],
                temperature=0.2
            )

            reply = response.choices[0].message.content.strip()
            if "no issue" not in reply.lower():
                issues.append({
                    "Segment": segment,
                    "Issue Type": "Spelling/Grammar",
                    "Details": reply
                })

        except Exception as e:
            issues.append({
                "Segment": segment,
                "Issue Type": "API Error",
                "Details": str(e)
            })
    return issues
