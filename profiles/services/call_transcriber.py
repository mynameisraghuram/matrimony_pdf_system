import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio(file_path):
    """Transcribe audio file using OpenAI Whisper."""
    with open(file_path, "rb") as audio_file:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en",
        )
    return result.text


def summarize_transcript(transcript, profile_name=""):
    """Summarize a call transcript into key points for matrimony context."""
    prompt = f"""You are a CRM assistant for a matrimony service (Reddy & Reddy Matrimony).
A relationship manager just had a conversation with/about the client: {profile_name}.

Summarize this call transcript into:
1. **Key Points** - What was discussed (2-5 bullet points)
2. **Client Preferences** - Any new preferences or requirements mentioned
3. **Action Items** - What needs to be done next
4. **Suggested Follow-up** - When to follow up and why

Keep it concise and professional. Use bullet points.

Transcript:
{transcript}
"""
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        return response.output_text.strip()
    except Exception as e:
        return f"Summary could not be generated: {e}\n\nRaw transcript:\n{transcript}"
