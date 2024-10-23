import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

def get_coordinates(city):
    """Holt die Koordinaten einer Stadt von der Geocoding API"""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=de"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            return data["results"][0]["latitude"], data["results"][0]["longitude"]
    return None, None

def get_weather_forecast(lat, lon):
    """Holt die Wettervorhersage von der Open-Meteo API"""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,precipitation_probability,weathercode"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&timezone=auto&forecast_days=7"
    )
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def weather_code_to_text(code):
    """Konvertiert den Wetter-Code in lesbaren Text"""
    weather_codes = {
        0: "Klar",
        1: "Überwiegend klar",
        2: "Teilweise bewölkt",
        3: "Bedeckt",
        45: "Neblig",
        48: "Dichter Nebel",
        51: "Leichter Nieselregen",
        53: "Mäßiger Nieselregen",
        55: "Starker Nieselregen",
        61: "Leichter Regen",
        63: "Mäßiger Regen",
        65: "Starker Regen",
        71: "Leichter Schneefall",
        73: "Mäßiger Schneefall",
        75: "Starker Schneefall",
        95: "Gewitter"
    }
    return weather_codes.get(code, "Unbekannt")

# Streamlit App Layout
st.title("🌤️ Wetter-Vorhersage App")

# Eingabefeld für die Stadt
city = st.text_input("Geben Sie eine Stadt ein:", "Berlin")

if city:
    lat, lon = get_coordinates(city)
    
    if lat and lon:
        weather_data = get_weather_forecast(lat, lon)
        
        if weather_data:
            st.subheader(f"Wettervorhersage für {city}")
            
            # Tägliche Übersicht
            daily_data = pd.DataFrame({
                'Datum': pd.to_datetime(weather_data['daily']['time']),
                'Max Temp': weather_data['daily']['temperature_2m_max'],
                'Min Temp': weather_data['daily']['temperature_2m_min'],
                'Niederschlag': weather_data['daily']['precipitation_sum']
            })
            
            # Temperatur-Verlauf Graph
            fig_temp = px.line(daily_data, 
                             x='Datum', 
                             y=['Max Temp', 'Min Temp'],
                             title='Temperaturverlauf',
                             labels={'value': 'Temperatur (°C)', 'variable': 'Typ'})
            st.plotly_chart(fig_temp)
            
            # Stündliche Vorhersage für heute
            hourly_data = pd.DataFrame({
                'Zeit': pd.to_datetime(weather_data['hourly']['time'][:24]),
                'Temperatur': weather_data['hourly']['temperature_2m'][:24],
                'Regenwahrscheinlichkeit': weather_data['hourly']['precipitation_probability'][:24],
                'Wetter': [weather_code_to_text(code) for code in weather_data['hourly']['weathercode'][:24]]
            })
            
            # Aktuelle Bedingungen
            current_hour = datetime.now().hour
            current_temp = hourly_data.iloc[current_hour]['Temperatur']
            current_weather = hourly_data.iloc[current_hour]['Wetter']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Aktuelle Temperatur", f"{current_temp:.1f}°C")
            with col2:
                st.metric("Aktuelles Wetter", current_weather)
            
            # Stündliche Vorhersage Tabelle
            st.subheader("Stündliche Vorhersage für heute")
            st.dataframe(hourly_data.set_index('Zeit'))
            
        else:
            st.error("Fehler beim Abrufen der Wetterdaten.")
    else:
        st.error("Stadt nicht gefunden. Bitte versuchen Sie es mit einer anderen Stadt.")