import streamlit as st
import requests
import openai


def lab5():
        def get_current_weather(location):
            API_key = st.secrets["weather_key"]

            if "," in location:
                location = location.split(",")[0].strip()

            urlbase = "https://api.openweathermap.org/data/2.5/"
            urlweather = f"weather?q={location}&appid={API_key}"
            url = urlbase + urlweather

            response = requests.get(url)
            data = response.json()
            temp = data["main"]["temp"] - 273.15
            feels_like = data["main"]["feels_like"] - 273.15
            temp_min = data["main"]["temp_min"] - 273.15
            temp_max = data["main"]["temp_max"] - 273.15
            humidity = data["main"]["humidity"]
            weather_description = data["weather"][0]["description"]

            return {
                "location": location,
                "temperature": round(temp, 2),
                "temp_min": round(temp_min, 2),
                "temp_max": round(temp_max, 2),
                "weather_description": weather_description,
                "feels_like": round(feels_like, 2),
                "humidity": round(humidity, 2),
            }


        def get_suggestion(weather_data):
            openai_api_key = st.secrets["api_key"]
            openai.api_key = openai_api_key

            prompt = (
                f"The current weather in {weather_data['location']} is "
                f"{weather_data['temperature']}°C with a feel-like temperature of "
                f"{weather_data['feels_like']}°C. The weather description is "
                f"{weather_data['weather_description']}. "
                "What kind of clothes should I wear today?"
            )

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Or "gpt-4" if available
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=100,
                temperature=0.7,
            )

            suggestion = response.choices[0].message.content.strip()
            return suggestion


        st.title("Travel Weather & Suggestion Bot")

        location = st.text_input(
            "Enter a city (e.g., Syracuse, NY or London, England):", "Syracuse, NY"
        )

        if location:
            weather_data = get_current_weather(location)

            if weather_data:
                st.write(f"Location: {weather_data['location']}")
                st.write(f"Temperature: {weather_data['temperature']}°C")
                st.write(f"Feels Like: {weather_data['feels_like']}°C")
                st.write(f"Weather: {weather_data['weather_description']}")

                suggestion = get_suggestion(weather_data)
                st.write(f"Suggested Clothes: {suggestion}")
            else:
                st.error("Unable to fetch weather data.")
