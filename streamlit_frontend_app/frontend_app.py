#Libraries importation

import streamlit as st
import requests
from datetime import datetime,timedelta
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt 


# Initial configuration

# IMPORTANT - YOU NEED TO PUT YOUR DEPLOYED BACKEND URL HERE
BASE_URL = "YOUR_BACKEND_URL"

#Fetch data from the backend or OpenCage API
def fetch_data(url, params=None):
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

#Fetch historical weather data from the backend.
def fetch_historical_weather_data():
    response = requests.get(f"{BASE_URL}/get_all_weather_data")
    if response.status_code == 200:
        return response.json()['data']
    else:
        return []
    
#Fetch weather forecast from the backend using provided latitude and longitude.
def get_weather_forecast(latitude, longitude):
    url = f"{BASE_URL}/get_weather_forecast"
    response = requests.post(url, json={"lat": latitude, "lon": longitude})
    return response.json() if response.status_code == 200 else {"status": "failed"}

#Fetch daily forecast at noon
def get_daily_forecast(latitude, longitude):
    response = requests.post(f"{BASE_URL}/get_daily_forecast", json={"lat": latitude, "lon": longitude})
    return response.json() if response.status_code == 200 else {"status": "failed"}

#Display weather forecast.
def display_forecast(forecast, title):
    if forecast.get('status') == 'success':
        st.subheader(title)
        cols = st.columns(len(forecast['forecast']))
        data = []
        for col, day in zip(cols, forecast['forecast']):
            with col:
                formatted_date = datetime.strptime(day['date'], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")
                st.write(formatted_date)
                icon_url = f"http://openweathermap.org/img/wn/{day['icon']}@2x.png"
                st.image(icon_url, width=100)
                st.write(f"🌡️{day['temperature']}°C")
                st.write(f"💧{day['humidity']}%")
                st.write(f"💨{day['windspeed']}m/s")
                data.append({'Date': formatted_date, 'Temperature': day['temperature']})

        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'], format="%d.%m.%Y %H:%M")
        fig = px.bar(df, x='Date', y='Temperature', title=f"{title} Over Time", labels={'Temperature': 'Temperature (°C)'}, color='Temperature', height=400, width=800)
        fig.update_layout(xaxis_title="Date", yaxis_title="Temperature (°C)", xaxis_tickformat="%d %b %H:%M", bargap=0.1, plot_bgcolor='rgba(0,0,0,0)')
        fig.update_xaxes(
            tickvals=df['Date'],  # Position ticks
            ticktext=[d.strftime('%d %b %H:%M') for d in df['Date']]  # Text ticks
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Failed to fetch weather forecast.")

#Provide weather recommendation based on the current outdoor weather condition.
def get_weather_recommendation(outdoor_weather):
    if outdoor_weather == "Rain":
        return "🌧️ It's raining! Remember to bring an umbrella and wear waterproof clothing."
    elif outdoor_weather == "Clouds":
        return "🌥️ The sky is cloudy. Take a raincoat in case it rains and dress accordingly."
    elif outdoor_weather == "Clear":
        return "🌞 It's clear sky! Enjoy the beautiful weather for an outdoor walk."
    else:
        return "Current weather conditions are variable. Make sure to check detailed forecasts to plan your day."

# Fetch coordinates for a given city using the backend
def get_coordinates(city):
    params = {"city": city}
    url = f"{BASE_URL}/get_coordinates"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get('lat'), data.get('lng')
    return None, None  # Returns None if something fails

# Fetch city suggestions using the backend based on the user's query
def get_city_suggestions(query):
    params = {"query": query}
    url = f"{BASE_URL}/get_city_suggestions"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return []

# Ensure session state for favorites is initialized
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# Fetching current weather data
current_weather = fetch_data(f"{BASE_URL}/get_latest_data")
if current_weather and current_weather.get('status') == 'success':
    data = current_weather['data']

# Formating of Date and Time fetched from the backend
backend_date = datetime.strptime(data['date'], "%Y-%m-%d").strftime("%A, %B %d, %Y")
backend_time = datetime.strptime(data['time'], "%H:%M:%S").strftime("%I:%M %p")

# Splitting the interface into three part (Current weather data, historical data, Weather forecast)
st.sidebar.header("There are three sections :")
st.sidebar.write("1 - The Current Weather section allows you to view the most recent data in a dashboard (BigQuery data). This includes data captured by the sensors of the M5Stack device as well as weather data obtained from the OpenWeatherMap API.")
st.sidebar.write("2 - The Historical Data section presents a collection of weather data stored in BigQuery (one data point per hour). Users can select a day and focus on specific features (e.g., outdoor humidity).")
st.sidebar.write("3 - The Weather Forecasts section aims to present the weather predictions for a specific location. There are two available options: you can either obtain forecasts for the next 9-12 hours or for the next 5 days. Additionally, it is possible to save certain locations as favorites to facilitate ease of use.")
page = st.sidebar.selectbox("Menu", ["1 - Current Weather","2 - Historical Data","3 - Weather Forecasts"])

# Configuration of the Current Weather page
if page == "1 - Current Weather":

    # Header with formatted date and time
    st.markdown("""
    <style>
        .reportview-container .main .block-container {
            padding-top: 2rem;
        }
        .data-section, .forecast-section {
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .data-section {
            background-color: #f0f2f6;
        }
        .forecast-section {
            background-color: #e2e2f0;
        }
        .separator {
            height: 4px;
            background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
            margin: 20px 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # Displaying Current weather data
    if current_weather and current_weather.get('status') == 'success':
        data = current_weather['data']
        st.markdown(f"""
            <div class='data-section'>
                <h1 style='text-align: center; color: #333;'>Weather Data Dashboard</h1>
                <h2 style='text-align: center; color: #666;'>
                <span style='color: red;'>Last update:</span> {backend_date} - {backend_time}
                </h2>
            </div>
        """, unsafe_allow_html=True)

        # Retrieving OpenWeather icons
        icon_code = data.get('outdoor_icon')  
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png" 

        # Three columns for displaying current weather data
        st.title("Current Weather")
        col1, col2, col3 = st.columns([1.7, 1.7, 1.7])
        
        with col1:
            st.markdown(f"<img src='{icon_url}' alt='Weather Icon' style='height: 100px;'>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='font-size: 36px;'>{data['outdoor_temp']}°C</h3>", unsafe_allow_html=True)

        # Adding recommandation sentence based on the outdoor weather
        recommendation = fetch_data(f"{BASE_URL}/get_latest_data").get('data').get('outdoor_weather')
        if recommendation:
            recommendation = get_weather_recommendation(recommendation)
        else:
            recommendation = "Impossible de récupérer les données météorologiques actuelles."

        recommendation_style = """
        <style>
        .recommendation-box {
                text-align: center;
                margin-top: 10px;  /* Adjust the top margin to ensure it's below other elements */
                color: #ff6347;  /* Using a red color for the font */
                border: 2px solid #ff6347;  /* Red border as per your screenshot */
                padding: 10px;
                border-radius: 5px;  /* Optional: adds rounded corners to the border */
            }
        </style>
        """
        recommendation_text = get_weather_recommendation(data['outdoor_weather'])  

        with col2:
            st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
            st.markdown(f"<h4> 🏠Indoor Conditions</h4>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>🌡️Temperature:</strong> {data['indoor_temp']} °C</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>💧Humidity:</strong> {data['indoor_humidity']}%</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>📏Pressure:</strong> {data['indoor_pressure']} hPa </div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>🌬️CO2:</strong> {data['indoor_airquality']} ppm</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(recommendation_style, unsafe_allow_html=True)
            st.markdown(f"<div class='recommendation-box'>{recommendation_text}</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
            st.markdown(f"<h4>🌳Outdoor Conditions</h4>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>🌡️Temperature:</strong> {data['outdoor_temp']} °C</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>💧Humidity:</strong> {data['outdoor_humidity']}%</div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>📏Pressure:</strong> {data['outdoor_pressure']} hPa </div>", unsafe_allow_html=True)
            st.markdown(f"<div><strong>💨Wind Speed:</strong> {data['outdoor_windspeed']}m/s</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

# Configuration of the Historical data page
if page == "2 - Historical Data":
    st.title("Historical Data")

    # Fetching of the historical data
    data = fetch_historical_weather_data()  
    df = pd.DataFrame(data)

    
    date = st.date_input("Choose a date", datetime.today())

    df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S')

    # Filter data for the selected date and group by hour and for each our it display three values
    filtered_data = df[df['date'] == date.strftime("%Y-%m-%d")]
    grouped = filtered_data.groupby(filtered_data['time'].dt.hour).tail(3)

    # Labels Mapping for the optons
    labels = {
        "indoor_temp": "Indoor temperature (°C)",
        "indoor_humidity": "Indoor humidity (%)",
        "indoor_pressure": "Indoor pressure (hPa)",
        "indoor_airquality": "Indoor air quality (CO2 ppm)",
        "outdoor_temp": "Outdoor temperature (°C)",
        "outdoor_humidity": "Outdoor humidity (%)",
        "outdoor_pressure": "Outdoor pressure (hPa)",
        "outdoor_windspeed": "Outdoor wind speed (m/s)"
    }

    options = list(labels.keys())
    selected_options = st.multiselect("Choose the types of data to display", options, format_func=lambda x: labels[x])

    # Button for displaying the data
    if st.button("Show Data"):
        # Checking if the grouped data are empty
        if grouped.empty:
            st.write("No data available for this date.")
        else:
            for option in selected_options:
                fig, ax = plt.subplots() #Chart Visualization
                # Ensure that the data is in a DataFrame and sort by 'time'
                grouped['time'] = pd.to_datetime(grouped['time'], format='%H:%M')  
                sorted_group = grouped.sort_values('time')  

                # Extract the sorted hours and data for the chart
                hours = sorted_group['time'].dt.strftime('%H:%M')
                values = sorted_group[option]

                ax.plot(hours, values, marker='o', linestyle='-', color='#add8e6', label=f"{labels[option]} on {date.strftime('%Y-%m-%d')}")
                ax.scatter(hours, values, color='red')

                ax.set_xlabel("Hour")
                ax.set_ylabel(labels[option])
                ax.set_title(f"{labels[option]} on {date.strftime('%d %b %Y')}")
                plt.xticks(rotation=45, ha='right')  
                ax.grid(True, linestyle='--', alpha=0.7)  

                # Ensure that the y-axis could show also negative values
                ymin, ymax = min(values), max(values)
                ax.set_ylim([ymin - 1, ymax + 1])  

                plt.tight_layout()

                st.pyplot(fig)
    st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

# Configuration of the Weather forecast page
elif page == "3 - Weather Forecasts":
    st.title("Weather Forecasts")
    city_query = st.text_input("Enter a city name", "Lausanne") #By default, here we chose Lausanne
    suggestions = get_city_suggestions(city_query)  
    city = st.selectbox("Did you mean:", options=suggestions, index=0) if suggestions else None

    # Check if a city is selected and handle its weather forecasting.
    if city:
        # Fetching coordinates (latitude, longitude) for the selected city. Based on that, it returns the corresponding forecast
        lat, lng = get_coordinates(city)  
        if lat and lng:
            if st.button("Get hourly forecast"):
                forecast = get_weather_forecast(lat, lng)
                display_forecast(forecast, "Hourly forecast")
            
            if st.button("Get daily forecast"):
                forecast = get_daily_forecast(lat, lng)
                display_forecast(forecast, "Daily forecast")

            # Managing favorite cities: allows the user to add, display the weather, or remove a city from favorites.
            if city not in st.session_state.get('favorites', []):
                if st.button("Add to Favorites"):
                    if 'favorites' not in st.session_state:
                        st.session_state['favorites'] = []
                    st.session_state.favorites.append(city)
                    st.sidebar.success(f"{city} added to favorites!")
        else:
            st.error("Could not find coordinates for the city.")
    else:
        st.info("Please enter a city name and select a valid option.")

    # Displaying Favorites city on the sidebar and selecting them to display weather forecast or removing them fo our favorites lists
    st.sidebar.title("Favorites")
    if 'favorites' in st.session_state and st.session_state.favorites:
        favorite_city = st.sidebar.selectbox("Select a Favorite City", st.session_state.favorites)
        if st.sidebar.button("Show Weather"):
            lat, lng = get_coordinates(favorite_city)
            if lat and lng:
                forecast = get_weather_forecast(lat, lng)
                display_forecast(forecast, f"Weather Forecast for {favorite_city}")
        if st.sidebar.button("Remove Favorite"):
            st.session_state.favorites.remove(favorite_city)
            st.sidebar.success("Favorite removed!")