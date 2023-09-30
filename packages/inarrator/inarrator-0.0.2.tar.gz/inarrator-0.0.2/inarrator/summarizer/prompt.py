"""PROMPTS FOR OUR EMAIL-SUMMARIZER"""
HUGGING_FACE_EMAIL_PROMPT = """Your main task is to summarize an email content.
Please make sure to include the main email content and summarize the main
points. Summarize the following Email Content:

FROM: {fro}
TO: {to}
SUBJECT: {subject}
BODY: {body}

Use the following format:
FROM: This is the person who send the email: {fro}
Summarized-Email-Conten: Email-Summarized Content
"""
STUFF_EMAIL_PROMPT = """
Please summarize the following emails:

{emails}

Summary:
"""
