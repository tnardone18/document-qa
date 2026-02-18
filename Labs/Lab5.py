import json
import requests
import streamlit as st
from openai import OpenAI

# ── Weather helper ──────────────────────────────────────────────────
def get_current_weather(location, api_key, units='imperial'):
    url = (
        f'https://api.openweathermap.org/data/2.5/weather'
        f'?q={location}&appid={api_key}&units={units}'
    )
    response = requests.get(url)

    if response.status_code == 401:
        raise Exception('Authentication failed: Invalid API key (401 Unauthorized)')
    if response.status_code == 404:
        error_message = response.json().get('message')
        raise Exception(f'404 error: {error_message}')

    data = response.json()
    temp       = data['main']['temp']
    feels_like = data['main']['feels_like']
    temp_min   = data['main']['temp_min']
    temp_max   = data['main']['temp_max']
    humidity   = data['main']['humidity']

    return {
        'location':    location,
        'temperature': round(temp, 2),
        'feels_like':  round(feels_like, 2),
        'temp_min':    round(temp_min, 2),
        'temp_max':    round(temp_max, 2),
        'humidity':    round(humidity, 2),
    }


# ── Tool definition for OpenAI function calling ────────────────────
weather_tool = {
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country, e.g. 'Syracuse, NY, US'",
                },
            },
            "required": ["location"],
        },
    },
}


# ── Run the conversation with tool use ─────────────────────────────
def get_clothing_advice(user_input, api_key_weather):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful fashion and weather advisor. "
                "When the user asks what to wear, use the get_current_weather tool "
                "to look up the weather. Then, based on the weather data:\n"
                "1. Suggest appropriate clothes to wear today.\n"
                "2. Suggest outdoor activities that are appropriate for the current weather.\n"
                "Keep your response practical, specific, and friendly."
            ),
        },
        {"role": "user", "content": user_input},
    ]

    # First call – the model may request a tool call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=[weather_tool],
        tool_choice="auto",
        max_tokens=400,
    )

    msg = response.choices[0].message

    # If the model invoked the tool, execute it and send the result back
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        location = args.get("location", "Syracuse, NY, US")
        weather = get_current_weather(location, api_key_weather)

        messages.append(msg)                       # assistant's tool‑call message
        messages.append({                          # tool result
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(weather),
        })

        # Second call – model produces the final advice
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=[weather_tool],
            tool_choice="auto",
            max_tokens=400,
        )
        return response.choices[0].message.content, weather

    # If no tool call was made, just return the text
    return msg.content, None


# ── Streamlit UI ────────────────────────────────────────────────────
st.title("Lab 5 – What to Wear")

api_key_weather = st.secrets["OPEN_WEATHER_API_KEY"]

location = st.text_input("Enter a city (e.g., Syracuse, NY, US):")

if st.button("Get Advice") and location:
    with st.spinner("Fetching weather and generating advice..."):
        try:
            prompt = f"What should I wear today in {location}?"
            advice, weather = get_clothing_advice(prompt, api_key_weather)

            if weather:
                st.subheader(f"📍 {weather['location']}")
                st.write(f"**Temperature:** {weather['temperature']} °F")
                st.write(f"**Feels Like:** {weather['feels_like']} °F")
                st.write(f"**Min / Max:** {weather['temp_min']} °F / {weather['temp_max']} °F")
                st.write(f"**Humidity:** {weather['humidity']}%")
                st.divider()

            st.subheader("👕 What to Wear")
            st.write(advice)

        except Exception as e:
            st.error(f"Error: {e}")