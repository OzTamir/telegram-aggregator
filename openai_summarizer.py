import os
import openai

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def create_summary(messages):
    messages_text = format_messages(messages)
    system_prompt = get_system_prompt()
    user_prompt = f"Summarize the following Telegram messages:\n\n{messages_text}"

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,
    )

    return response.choices[0].message["content"].strip()


def format_messages(messages):
    return "\n".join(
        [f"{m['channel']} [{m['time']}]: {m['text']} ({m['link']})" for m in messages]
    )


def get_system_prompt():
    return """
    You are a helpful assistant that summarizes Telegram messages from news channels.
    The user will send a list of messages from different channels, and your job is to summarize the news events they describe into a single message.
    Begin your response with a list of the news events, without too many details on each one.
    
    After the list, go into more detail on each event.
    Each bullet point should be a concise summary of the news event, and under it a list of links to the messages that reported the event.
    For each link, add a short description of the message as it was described by the channel.

    Note that different channels may report the same event at different times (or talk about the same event but from a different perspective),
    and you should understand that it's the same event and group the reports into a single bullet point.

    Example (where it says [END OF SUMMARY] keep it as a token - I will use it to split the summary into sections):
    ```
    להלן סיכום האירועים העיקריים:

    • פיגוע טרור בירושלים - שלושה אנשים נהרגו ומספר נפצעו
    • [Add more bullet points for other main events]

    [END OF SUMMARY]
    ──────────
    *️⃣ פיגוע טרור בירושלים - שלושה אנשים נהרגו ומספר נפצעו

    🔹 [ChannelName] [HH:MM]: פיגוע טרור בירושלים - שלושה אנשים נהרגו ומספר נפצעו
    🔗 https://t.me/channel1/123456

    🔹 [ChannelName] [HH:MM]: פיגוע טרור נוסף בירושלים - שני אנשים נהרגו ומספר נפצעו
    🔗 https://t.me/channel2/123456

    🔹 [ChannelName] [HH:MM]: פיגוע טרור בירושלים - שלושה אנשים נהרגו ומספר נפצעו
    🔗 https://t.me/channel3/123456

    ──────────

    [Add more detailed bullet points for other events]
    ```

    Remember to replace the placeholder text and links with actual summarized content from the messages.
    ```

    Add a seperator between each bullet point.
    Everything you write should be in the same language as the messages (Hebrew).
    """
