from flask import Flask, Response, request, jsonify, send_file
import os
from google.cloud import bigquery, texttospeech
from google.cloud.exceptions import NotFound
import requests
from numpy import float64
from datetime import datetime
import openai
import db_dtypes

# IMPORTANT
# IF YOU WANT TO DEPLOY THIS APP, YOU NEED TO WRITE YOUR API KEYS HERE
# OpenAI, OpenWeatherMap (free), OpenCage (free)
openai.api_key = "YOUR_OPENAI_API_KEY"
openweathermap_key = "YOUR_OPENWEATHERMAP_API_KEY"
opencage_key = "YOUR_OPENCAGE_API_KEY"

# IMPORTANT
# SPECIFY YOUR DATASET, TABLE AND PROJECT NAME HERE 
bigquery_dataset = "YOUR_BIGQUERY_DATASET"
bigquery_table = "YOUR_BIGQUERY_TABLE"
googlecloud_project = "YOUR_GCP_PROJECT"
bigquery_table_address = googlecloud_project + "." + bigquery_dataset + "." + bigquery_table

client = bigquery.Client()

app = Flask(__name__)

q = f"""
SELECT * FROM `{bigquery_table_address}` LIMIT 10
"""
query_job = client.query(q)
df = query_job.to_dataframe()

# IMPORTANT
# SPECIFY YOUR DATASET, TABLE AND PROJECT NAME HERE 
table_ref = client.dataset(bigquery_dataset, project=googlecloud_project).table(bigquery_table)
table = client.get_table(table_ref)

# In order to use BigQuery table schemes
schema_dtypes = {field.name: field.field_type for field in table.schema}

@app.route('/send_to_bigquery', methods=['POST'])
def send_to_bigquery():
    if request.method == 'POST':
        data = request.get_json(force=True)["values"]
        # Extract lat and lon from the data
        lat = request.get_json(force=True)["lat"]
        lon = request.get_json(force=True)["lon"]
        if lat is None or lon is None:
            return jsonify({"status": "failed", "error": "Latitude and longitude are required"}), 400

        # OpenWeatherMap API setup
        api_key = openweathermap_key
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"

        # Fetching data from OpenWeatherMap
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"status": "failed", "error": "Failed to fetch weather data"}), 500
        weather_data = response.json()
        
        # Adding weather data to 'data' dictionary
        data["outdoor_temp"] = weather_data["main"]["temp"]
        data["outdoor_humidity"] = weather_data["main"]["humidity"]
        data["outdoor_weather"] = weather_data["weather"][0]["main"]
        data["outdoor_icon"] = weather_data["weather"][0]["icon"]
        data["outdoor_pressure"] = weather_data["main"]["pressure"]
        data["outdoor_windspeed"] = weather_data["wind"]["speed"]

        # Building the BigQuery insertion query
        q = f"INSERT INTO `{bigquery_table_address}`"
        names = """"""
        values = """"""
        for k, v in data.items():
            names += f"""{k},"""
            if schema_dtypes[k] == 'FLOAT':
                values += f"""{v},"""
            elif schema_dtypes[k] == 'STRING':
                values += f"""'{v}',"""
            else:
                # string values in the query should be in single qutation!
                values += f"""'{v}',"""
        # Remove the last comma
        names = names[:-1]
        values = values[:-1]
        q += f"({names}) VALUES({values})"
        
        # Running the query
        try:
            query_job = client.query(q)
            query_job.result()  # Wait for the query to finish
            return jsonify({"status": "success", "data": data}), 200
        except Exception as e:
            return jsonify({"status": "failed", "error": str(e)}), 500

# Fetch last row in the BigQuery table
def fetch_latest_weather_data():
    query = f"""
    SELECT indoor_temp, indoor_humidity, indoor_pressure, indoor_airquality,
           outdoor_temp, outdoor_humidity, outdoor_weather, outdoor_icon, outdoor_pressure,
           outdoor_windspeed, date, time
    FROM `{bigquery_table_address}`
    ORDER BY date DESC, time DESC
    LIMIT 1
    """
    try:
        query_job = client.query(query)  # Make an API request.
        results = query_job.result()  # Wait for the query to complete.
        
        for row in results:
            return {
                "date": str(row.date),
                "time": str(row.time),
                "indoor_temp": row.indoor_temp,
                "indoor_humidity": row.indoor_humidity,
                "indoor_pressure": row.indoor_pressure,
                "indoor_airquality": row.indoor_airquality,
                "outdoor_temp": row.outdoor_temp,
                "outdoor_humidity": row.outdoor_humidity,
                "outdoor_weather": row.outdoor_weather,
                "outdoor_pressure": row.outdoor_pressure,
                "outdoor_windspeed": row.outdoor_windspeed,
                "outdoor_icon": row.outdoor_icon
            }
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

# Endpoint for fetching last row in BigQuery table
@app.route('/get_latest_data', methods=['GET'])
def get_latest_data():
    weather_data = fetch_latest_weather_data()
    
    if weather_data:
        return jsonify({"status": "success", "data": weather_data}), 200
    else:
        return jsonify({"status": "failed", "error": "No data found"}), 404
    
# Fetch all data in BigQuery table
def fetch_all_weather_data():
    query = f"""
    SELECT indoor_temp, indoor_humidity, indoor_pressure, indoor_airquality,
           outdoor_temp, outdoor_humidity, outdoor_weather, outdoor_icon, outdoor_pressure,
           outdoor_windspeed, date, time
    FROM `{bigquery_table_address}`
    ORDER BY date DESC, time DESC
    """
    try:
        query_job = client.query(query)  # Make an API request.
        results = query_job.result()  # Wait for the query to complete.
        data_list = []
        for row in results:
            data_list.append({
                "date": str(row.date),
                "time": str(row.time),
                "indoor_temp": row.indoor_temp,
                "indoor_humidity": row.indoor_humidity,
                "indoor_pressure": row.indoor_pressure,
                "indoor_airquality": row.indoor_airquality,
                "outdoor_temp": row.outdoor_temp,
                "outdoor_humidity": row.outdoor_humidity,
                "outdoor_weather": row.outdoor_weather,
                "outdoor_icon": row.outdoor_icon,
                "outdoor_pressure": row.outdoor_pressure,
                "outdoor_windspeed": row.outdoor_windspeed
            })
        return data_list
    except Exception as e:
        print(f"Error fetching all weather data: {e}")
        return None

# Endpoint for fetching all the data
@app.route('/get_all_weather_data', methods=['GET'])
def get_all_weather_data():
    all_weather_data = fetch_all_weather_data()
    
    if all_weather_data:
        return jsonify({"status": "success", "data": all_weather_data}), 200
    else:
        return jsonify({"status": "failed", "error": "No data found"}), 404

# Fetch hourly forecasts from OpenWeatherMap API
def fetch_weather_forecast(latitude, longitude):
    api_key = openweathermap_key
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecasts = []
        for item in data['list'][:5]:
            forecast = {
                'date': item['dt_txt'],
                'temperature': item['main']['temp'],
                'description': item['weather'][0]['description'],
                'humidity': item['main']['humidity'],
                'pressure': item['main']['pressure'],
                'windspeed': item['wind']['speed'],
                'icon': item['weather'][0]['icon']
            }
            forecasts.append(forecast)
        return forecasts
    else:
        return None
    
# Endpoint for fetching hourly forecasts
@app.route('/get_weather_forecast', methods=['POST'])
def get_weather_forecast():
    data = request.get_json()
    latitude = data.get('lat')
    longitude = data.get('lon')
    
    if not latitude or not longitude:
        return jsonify({'status': 'error', 'message': 'Latitude and longitude are required.'}), 400
    
    forecasts = fetch_weather_forecast(latitude, longitude)
    
    if forecasts is not None:
        return jsonify({'status': 'success', 'forecast': forecasts}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to fetch weather data'}), 500

# Fetch daily forecasts (noon) from OpenWeatherMap API 
def fetch_noon_forecasts(latitude, longitude):
    api_key = openweathermap_key
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        noon_forecasts = []
        count = 0
        
        for item in data['list']:
            if '12:00:00' in item['dt_txt']:
                if count < 5:  # Limit of 5
                    forecast = {
                        'date': item['dt_txt'],
                        'temperature': item['main']['temp'],
                        'description': item['weather'][0]['description'],
                        'humidity': item['main']['humidity'],
                        'pressure': item['main']['pressure'],
                        'windspeed': item['wind']['speed'],
                        'icon': item['weather'][0]['icon']
                    }
                    noon_forecasts.append(forecast)
                    count += 1
                else:
                    break
        return noon_forecasts
    else:
        return None

# Endpoint for fetching daily forecasts
@app.route('/get_daily_forecast', methods=['POST'])
def get_noon_forecast():
    data = request.get_json()
    latitude = data.get('lat')
    longitude = data.get('lon')
    
    if not latitude or not longitude:
        return jsonify({'status': 'error', 'message': 'Latitude and longitude are required.'}), 400
    
    forecasts = fetch_noon_forecasts(latitude, longitude)
    
    if forecasts is not None:
        return jsonify({'status': 'success', 'forecast': forecasts}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to fetch weather data'}), 500

# Endpoint for getting coordinates with city name using OpenCage API
@app.route('/get_coordinates', methods=['GET'])
def get_coordinates():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City is required"}), 400
    
    params = {"q": city, "key": opencage_key, "limit": 1, "no_annotations": 1}
    url = "https://api.opencagedata.com/geocode/v1/json"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get('results')
        if results:
            geometry = results[0].get('geometry')
            if geometry:
                return jsonify({"lat": geometry['lat'], "lng": geometry['lng']}), 200
    return jsonify({"error": "Failed to fetch coordinates"}), 500

# Endpoint for getting city suggestions from OpenCage API
@app.route('/get_city_suggestions', methods=['GET'])
def get_city_suggestions():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {"q": query, "key": opencage_key, "limit": 5, "min_confidence": 3, "no_annotations": 1}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        suggestions = response.json()
        return jsonify([place['formatted'] for place in suggestions['results']]), 200
    return jsonify([]), 500

# Endpoint for generating a current weather summary using OpenAI API
@app.route('/current_weather_summary', methods=['GET'])
def current_weather_summary():
    weather_data = fetch_latest_weather_data()
    prompt = f"<context> You are going to generate a message to be read by a Text to speech API, so only use letters no special character and no digits <context> <instructions> Summarize the current weather conditions in a single sentence, focus only on the outdoor measures which are outdoor_humidity, outdoor_temp and outdoor_weather <instructions> <format> Do not include any special character, only letters, for the hours write them like this example : nine AM, same for degree celsius, Maximum of 25 words <format>: {weather_data}"
    
    summary = ask_gpt(prompt)
    return jsonify({'summary': summary})

# Endpoint for generating a weather forecasts alert using OpenAI API
@app.route('/weather_forecast_alert', methods=['POST'])
def weather_forecast_alert():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    forecast_data = fetch_weather_forecast(lat, lon)
    prompt = f"<context> You are going to generate a message to be read by a Text to speech API, so only use letters no special character and no digits <context> <instructions> Generate a short alert message based on the following weather forecast data <instructions> <format> Do not include any special character, only letters, for the hours write them like this example : nine AM, same for degree celsius, Maximum of 25 words <format> : {forecast_data}"
    
    alert_message = ask_gpt(prompt)
    return jsonify({'alert': alert_message})

# Request to the OpenAI API
def ask_gpt(prompt):
    model_choice = "gpt-3.5-turbo-0125"
    try:
        response = openai.ChatCompletion.create(
            model=model_choice,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"An error occurred: {e}"
    
# Endpoint for generating T2S using Google TTS API
@app.route('/generate-speech', methods=['POST'])
def generate_speech():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    return Response(response.audio_content, mimetype='audio/wav')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)