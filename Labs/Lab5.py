import requests
import streamlit as st

# location in form City, State, Country
# e.g., Syracuse, NY, US
# default units is degrees Fahrenheit
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


st.title("Lab 5 – What to Wear")

api_key = st.secrets["OPEN_WEATHER_API_KEY"]

test_locations = ['Syracuse, NY, US', 'Lima, Peru']

for loc in test_locations:
    st.subheader(f"📍 {loc}")
    try:
        weather = get_current_weather(loc, api_key)
        st.write(f"**Temperature:** {weather['temperature']} °F")
        st.write(f"**Feels Like:** {weather['feels_like']} °F")
        st.write(f"**Min / Max:** {weather['temp_min']} °F / {weather['temp_max']} °F")
        st.write(f"**Humidity:** {weather['humidity']}%")
    except Exception as e:
        st.error(f"Error fetching weather for {loc}: {e}")