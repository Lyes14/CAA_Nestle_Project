from m5stack import *
from m5stack_ui import *
from uiflow import *
import unit
import urequests
import ntptime
from libs.image_plus import *
from _thread import allocate_lock
import wifiCfg

# Creating screen and changing color
screen = M5Screen()
screen.clean_screen()
screen.set_screen_bg_color(0xd1d1d1)

### IMPORTANT - You need to change this with your deployed backend URL
backend_URL = "YOUR_BACKEND_URL"
### IMPORTANT - You need to change this with your deployed backend URL

pir_0 = unit.get(unit.PIR, unit.PORTB)
env3_0 = unit.get(unit.ENV3, unit.PORTA)
tvoc_0 = unit.get(unit.TVOC, unit.PORTC)

# Initial values for latitude and longitude (for Lausanne by default)
latitude = 46.51
longitude = 6.63
# Lock for safe thread management
location_lock = allocate_lock()

# Initial values for page_refresh function
active_page = 'weather'
iteration_count = 0
speech_cooldown = 6
cooldown_count = 5
alert_cooldown = 6
alert_cooldown_count = 4

###_______________________________________________________________________________________________________
###
### IMPORTANT - You need to change this with your WIFI credentials if you want to try this app - IMPORTANT
DEFAULT_WIFI_SSID = 'YOUR_WIFI_SSID'
DEFAULT_WIFI_PASSWORD = 'YOUR_WIFI_PASSWORD'
### IMPORTANT - You need to change this with your WIFI credentials if you want to try this app - IMPORTANT
### ______________________________________________________________________________________________________

# Connection to the default WIFI
wifiCfg.doConnect(DEFAULT_WIFI_SSID, DEFAULT_WIFI_PASSWORD)

# Init ntp client for fetching date and time
ntp = ntptime.client(host='ch.pool.ntp.org', timezone=2)

#Request to the backend for sending indoor data (sensors) to BigQuery
def send_data_to_backend(lat, lon):
    url = backend_URL + '/send_to_bigquery'
    headers = {'Content-Type': 'application/json'}
    if ntp:
        data = {
            "values": {
                "indoor_temp": float(env3_0.temperature),
                "indoor_humidity": float(env3_0.humidity),
                "indoor_pressure": float(env3_0.pressure),
                "indoor_airquality": float(400), #float(tvoc_0.eCO2),
                "date": ntp.formatDate('-'),
                "time": ntp.formatTime(':')
            },
            "lat": lat,
            "lon": lon
        }
        try:
            response = urequests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'failed', 'error': 'Failed to send data to backend'}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    else:
        return {'status': 'failed', 'error': 'Failed to get current time'}

#Request to the backend app for fetching the latest data in BigQuery
def fetch_weather_data():
    url = backend_URL + '/get_latest_data'
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            weather_data = response.json()['data']
            return weather_data
        else:
            print('Failed to fetch data: Status code', response.status_code)
            return None
    except Exception as e:
        print("Error fetching weather data:", str(e))
        return None

#Current weather display function, outdoor and indoor
def display_weather_data(weather_data):
    if weather_data:
        icon_url = "http://openweathermap.org/img/wn/" + weather_data['outdoor_icon'] + "@2x.png"    
        imageplus0 = M5ImagePlus(x=210, y=70, url=icon_url)
        M5Label("Outdoor", x=5, y=65, color=0x7066df, font=FONT_MONT_22)
        M5Label(str(round(weather_data['outdoor_temp'], 1)) + "°C", x=20, y=90, color=0x000, font=FONT_MONT_34)
        M5Label("Hum: " + str(round(weather_data['outdoor_humidity'])) + "%", x=20, y=130, color=0x000)
        M5Label(weather_data['outdoor_weather'], x=140, y=150, color=0x000)
        M5Label("Wind: " + str(round(weather_data['outdoor_windspeed'], 1))  + "m/s", x=20, y=150, color=0x000)
        M5Label("Pres: " + str(round(weather_data['outdoor_pressure'])) + "hPa", x=100, y=130, color=0x000)
        M5Label("____________________________________________________", x=0, y=155, color=0x7066df)
        M5Label("Indoor", x=10, y=170, color=0x7066df, font=FONT_MONT_22)
        M5Label(str(round(weather_data['indoor_temp'], 1)) + "°C", x=20, y=190, color=0x000, font=FONT_MONT_34)
        M5Label("Hum: " + str(round(weather_data['indoor_humidity'])) + "%", x=135, y=220, color=0x000)
        M5Label("Pres: " + str(round(weather_data['indoor_pressure'])) + "hPa", x=135, y=200, color=0x000)
        M5Label("CO2: " + str(round(weather_data['indoor_airquality'])) + "ppm", x=135, y=180, color=0x000)
        if weather_data['indoor_airquality'] > 1000 or weather_data['indoor_humidity'] < 35:
          M5Label("X", x=263, y=185, color=0xd72323, font=FONT_MONT_38)
        else:
          M5Label("O", x=260, y=185, color=0x36d723, font=FONT_MONT_38)
        
    else:
        M5Label('No data available', x=20, y=60, color=0xff0000)

#Request to the backend app for fetching the hourly forecast data
def fetch_weather_forecast(lat, lon):
    url =  backend_URL + '/get_weather_forecast'
    data = {'lat': lat, 'lon': lon}
    try:
        response = urequests.post(url, json=data)
        if response.status_code == 200:
            forecast_data = response.json()['forecast']
            return forecast_data
        else:
            print('Failed to fetch forecast data: Status code', response.status_code)
            return None
    except Exception as e:
        print("Error fetching forecast data:", str(e))
        return None

#Weather forecast display function, next 9-12 hours weather conditions
def display_weather_forecast(forecasts):
    if not forecasts:
        M5Label('No forecast data available', x=20, y=60, color=0xff0000)
        return

    base_url = "http://openweathermap.org/img/wn/"
    x_positions = [-10, 70, 150, 230]

    for i in range(4):
        icon_url = base_url + forecasts[i]['icon'] + "@2x.png"
        imageplus = M5ImagePlus(x_positions[i], 60, url=icon_url)
        M5Label(str(forecasts[i]['date']).split()[1][:2] + "H", x=x_positions[i] + 25, y=140, color=0x000, font=FONT_MONT_22)
        M5Label(str(forecasts[i]['temperature']) + "°C", x=x_positions[i] + 25, y=165, color=0x000)
        M5Label("H:" + str(forecasts[i]['humidity']) + "%", x=x_positions[i] + 25, y=180, color=0x000)
        M5Label("W:" + str(round(forecasts[i]['windspeed'], 1)) + "m/s", x=x_positions[i] + 25, y=195, color=0x000)

    M5Label("H=Humidity, W=Wind Speed", x=5, y=220)

#Settings page display function, we can modify specific parameters like latitude, longitude and cooldown
def display_settings():
    global latitude
    global longitude
    global lat_label
    global lon_label
    global speech_cooldown
    global cooldown_label
    global alert_cooldown
    global alert_label
    
    M5Label("____________________________________________________", x=0, y=115)
    M5Label("____________________________________________________", x=0, y=170)

    lat_label = M5Label("Lat: " + str(latitude), x=130, y=75, color=0x000)
    lon_label = M5Label("Lon: " + str(longitude), x=130, y=100, color=0x000)
    cooldown_label = M5Label("Sum. cooldown: " + str(speech_cooldown) + "0s", x=90, y=135, color=0x000)
    alert_label = M5Label("Alert cooldown: " + str(alert_cooldown) + "0s", x=90, y=160, color=0x000)
    
    # Latitude buttons
    lat_minus_1_00 = M5Btn(x=30, y=75, w=30, h=20, bg_c=0x9c260d, text='--', text_c=0xffffff)
    lat_minus_0_01 = M5Btn(x=70, y=75, w=30, h=20, bg_c=0xff0000, text='-', text_c=0xffffff)
    lat_plus_0_01 = M5Btn(x=220, y=75, w=30, h=20, bg_c=0x00ff00, text='+', text_c=0xffffff)
    lat_plus_1_00 = M5Btn(x=260, y=75, w=30, h=20, bg_c=0x14820c, text='++', text_c=0xffffff)

    lat_minus_1_00.pressed(lambda: adjust_latitude(-1.00))
    lat_minus_0_01.pressed(lambda: adjust_latitude(-0.01))
    lat_plus_0_01.pressed(lambda: adjust_latitude(0.01))
    lat_plus_1_00.pressed(lambda: adjust_latitude(1.00))

    # Longitude buttons
    lon_minus_1_00 = M5Btn(x=30, y=100, w=30, h=20, bg_c=0x9c260d, text='--', text_c=0xffffff)
    lon_minus_0_01 = M5Btn(x=70, y=100, w=30, h=20, bg_c=0xff0000, text='-', text_c=0xffffff)
    lon_plus_0_01 = M5Btn(x=220, y=100, w=30, h=20, bg_c=0x00ff00, text='+', text_c=0xffffff)
    lon_plus_1_00 = M5Btn(x=260, y=100, w=30, h=20, bg_c=0x14820c, text='++', text_c=0xffffff)

    lon_minus_1_00.pressed(lambda: adjust_longitude(-1.00))
    lon_minus_0_01.pressed(lambda: adjust_longitude(-0.01))
    lon_plus_0_01.pressed(lambda: adjust_longitude(0.01))
    lon_plus_1_00.pressed(lambda: adjust_longitude(1.00))
    
    # Cooldown buttons
    cooldown_minus_1 = M5Btn(x=30, y=132, w=30, h=20, bg_c=0xff0000, text='-', text_c=0xffffff)
    cooldown_plus_1 = M5Btn(x=260, y=132, w=30, h=20, bg_c=0x00ff00, text='+', text_c=0xffffff)

    cooldown_minus_1.pressed(lambda: adjust_cooldown(-1))
    cooldown_plus_1.pressed(lambda: adjust_cooldown(1))
    
    # Alert buttons
    alert_minus_1 = M5Btn(x=30, y=160, w=30, h=20, bg_c=0xff0000, text='-', text_c=0xffffff)
    alert_plus_1 = M5Btn(x=260, y=160, w=30, h=20, bg_c=0x00ff00, text='+', text_c=0xffffff)

    alert_minus_1.pressed(lambda: adjust_alert(-1))
    alert_plus_1.pressed(lambda: adjust_alert(1))

def adjust_latitude(amount):
    global latitude
    with location_lock:
      latitude += amount
      lat_label.set_text("Lat: " + str(round(latitude, 2)))

def adjust_longitude(amount):
    global longitude
    with location_lock:
      longitude += amount
      lon_label.set_text("Lon: " + str(round(longitude, 2)))
      
def adjust_cooldown(amount):
    global speech_cooldown
    speech_cooldown += amount
    cooldown_label.set_text("Sum. cooldown: " + str(speech_cooldown) + "0s")

def adjust_alert(amount):
    global alert_cooldown
    alert_cooldown += amount
    alert_label.set_text("Alert cooldown: " + str(alert_cooldown) + "0s")
  
#Request to the backend app for fetching a openAI generated message for current weather summary
def fetch_weather_summary():
    url =  backend_URL + '/current_weather_summary'
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            summary_data = response.json()
            return summary_data['summary']
        else:
            print("Failed to fetch data: Status code", response.status_code)
            return "Failed to fetch data"
    except Exception as e:
        print("Request failed:", str(e))
        return "Request failed"
        
#Request to the backend app for fetching a openAI generated message for forecast alert
def fetch_weather_forecast_alert(lat, lon):
  url =  backend_URL + '/weather_forecast_alert'
  data = {'lat': lat, 'lon': lon}
  try:
      response = urequests.post(url, json=data)
      if response.status_code == 200:
          alert_data = response.json()
          return alert_data['alert']
      else:
          print("Failed to fetch forecast alert: Status code", response.status_code)
          return "Failed to fetch forecast alert"
  except Exception as e:
      print("Request failed:", str(e))
      return "Request failed"
  
#Request to the backend app for fetching a .WAV file of text argument
def speech(text):
    if text:
      try:
        data = {'text' : text}
        url =  backend_URL + '/generate-speech'
        response = urequests.post(url, json=data)
        if response.status_code == 200:
            with open('res/test.wav', 'wb') as f:
                f.write(response.content)
            speaker.playWAV('res/test.wav', volume=6)
        else:
            print("Failed to fetch audio: ", response.status_code)
      except:
        print("Failed to fetch audio")
    else:
        print("No weather summary provided.")

def display_hour():
  M5Label(str(ntp.formatDate('-')), x=120, y=40, color=0x7066df)
  M5Label(str(ntp.formatTime(':'))[0:5], x=120, y=10, color=0x7066df, font=FONT_MONT_34)
  M5Label("____________________________________________________", x=0, y=50, color=0x7066df)

        
# Main loop function, display and refresh all pages, detect presence and run speech
def page_refresh():
    global iteration_count
    send_counter = 5

    while True:
        iteration_count += 1  # Increment each iteration
        send_counter += 1

        global speech_cooldown
        global cooldown_count
        global alert_cooldown
        global alert_cooldown_count
        global latitude
        global longitude
    
        # Check presence with PIR
        if pir_0.state == 1:
            rgb.setColorAll(0xff0000)
            # Check if cooldown is finished
            if cooldown_count >= speech_cooldown:
              try:
                  summary = fetch_weather_summary()
                  speech(summary)
                  cooldown_count = 0  # Reset cooldown
              except:
                  print("Failed audio fetch")
            if alert_cooldown_count >= alert_cooldown:
              try:
                  alert_text = fetch_weather_forecast_alert(latitude, longitude)
                  speech(alert_text)
                  alert_cooldown_count = 0  # Reset cooldown
              except:
                  print("Failed forecast alert audio fetch")
            rgb.setColorAll(0x000000)
        
    # Increment cooldown for summary and forecast alert
        if cooldown_count < speech_cooldown:
          cooldown_count += 1
          
        if alert_cooldown_count < alert_cooldown:
            alert_cooldown_count += 1
            
        try:
            global latitude, longitude
            global active_page

            # Send data to backend every minutes
            if send_counter % 6 == 0:
                result = send_data_to_backend(latitude, longitude)
                print("Data sent:", result)

            # Weather page is refreshed every ten seconds
            if active_page == "weather":
                screen.clean_screen()
                display_hour()
                data = fetch_weather_data()
                display_weather_data(data)

            # Forecast page is refreshed every minutes
            if iteration_count % 6 == 0 and active_page == "forecast":
                screen.clean_screen()
                display_hour()
                forecasts = fetch_weather_forecast(latitude, longitude)
                display_weather_forecast(forecasts)

            # Settings page is refreshed every minutes
            if iteration_count % 6 == 0 and active_page == "settings":
                screen.clean_screen()
                display_hour()
                display_settings()

        except Exception as e:
            M5Label("Error in page_refresh: " + str(e), x=80, y=90)

        wait(10)  # Wait 10 seconds until next iteration


def on_forecast_button_pressed():
  global active_page, iteration_count
  active_page = "forecast"
  iteration_count = 5
  
def on_weather_button_pressed():
  global active_page
  active_page = "weather"
  
def on_settings_button_pressed():
  global active_page, iteration_count
  active_page = "settings"
  iteration_count = 5

# Link between buttons and functions
def main():
  btnA.wasPressed(on_forecast_button_pressed)
  btnB.wasPressed(on_weather_button_pressed)
  btnC.wasPressed(on_settings_button_pressed)

# Execution
_thread.start_new_thread(page_refresh, ())
main()





