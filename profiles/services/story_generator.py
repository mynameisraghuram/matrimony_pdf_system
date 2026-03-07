import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_prompt(profile):
    return f"""
You are writing a respectful matrimonial profile summary.

Rules:
- Use only the provided facts.
- Do not invent any information.
- Keep it professional, polished, and natural.
- Keep it between 100 and 180 words.
- Output exactly one paragraph.

Profile data:
Full name: {profile.get('full_name', '')}
Marital status: {profile.get('marital_status', '')}
Height: {profile.get('height', '')}
Education: {profile.get('graduation', '')}, {profile.get('masters', '')}
Designation: {profile.get('designation', '')}
Company: {profile.get('company_name', '')}
Salary: {profile.get('salary', '')}
Job location: {profile.get('job_location', '')}
Father name: {profile.get('father_name', '')}
Mother name: {profile.get('mother_name', '')}
Siblings: {profile.get('siblings', '')}
Preferences: {profile.get('career_preferences', '')}, {profile.get('education_preference', '')}
"""


def fallback_summary(profile):
    name = profile.get("full_name") or "This candidate"
    job = profile.get("designation") or "professional"
    location = profile.get("job_location") or "their current location"
    return f"{name} is presented as a well-rounded and respectful individual currently working as a {job} in {location}. The profile reflects a balanced personal and professional background, along with clearly stated family values and partner preferences. This summary has been generated from the available submitted information only."


def generate_story(profile):
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=build_prompt(profile)
        )
        return response.output_text.strip()
    except Exception:
        return fallback_summary(profile)