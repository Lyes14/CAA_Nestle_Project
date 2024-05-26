<h1 align="center">Project - CAA 2024 - Team Nestlé</h1>
<p align="center">
<img src="https://www.rts.ch/2017/10/10/10/13/8987311.image" width="1000" height="250"/> <br>
 </p>
 
## Team members 
* Elias Amine Sam
* Hamza Khalif


## 🚧   Project Description  
Our project aims to develop an integrated indoor/outdoor weather monitoring system using M5Stack IoT devices and sensors, complemented by a cloud-based dashboard. By leveraging the capabilities of these devices and cloud services, we aim to provide users with comprehensive weather data and alerts, empowering them to make informed decisions and stay prepared for changing weather conditions.

### 🔑 Key Components:

* **Hardware**: We will utilize the M5Stack Core2 IoT device along with the ENVIII sensor (humidity & temperature), air quality sensor, and motion sensor. These components will be seamlessly integrated into our solution to collect indoor measurements and detect human activity.

* **Data Collection**: Our system will gather indoor measurements from the sensors and outdoor weather data from various APIs, including the OpenWeatherMap API. This data will be stored and managed using Google Cloud's BigQuery service, ensuring efficient retrieval and analysis.

* **User Interfaces**: We will develop two distinct user interfaces:
    - On-Device Interface: 
        - The M5Stack IoT device will feature a user-friendly interface displaying outdoor temperature, indoor temperature, humidity etc and weather forecasts. Additionally, it will use presence sensor to deliver timely alerts and updates.

    - Cloud-Based Dashboard: 
        - A web-based dashboard built using Streamlit will allow users to monitor weather conditions remotely. This dashboard will retrieve data from BigQuery, providing insights into current and historical weather data and can display forecasts depending on the selected city. 
You can access it by clicking [here](https://frontend-app-vm2g7tx3va-oa.a.run.app/) : 


## 📙  Repository contents

#### This github repository contains the following folders:
* **M5 Flow code** : Python code designed for the M5Stack device's interface. It displays differents metrics (indoor temperature, indoor humidity, air quality etc.) from the backend server. It incorporates an alert system that will provide a summary of both the current weather conditions and future forecasts by using Text-to-Speech technology and syncs with the backend upon startup for up-to-date information.
* **Backend** : Python backend code to handle weather data by using Flask and Google Cloud BigQuery. It provides endpoints for fetching, storing, and processing weather information from different sources. The backend interacts with the OpenWeatherMap API to retrieve current weather data and forecast weather data based on latitude and longitude coordinates. It also integrates with Google Cloud BigQuery to store and retrieve historical weather records. This backend uses also OpenAi to implement a Text-to-Speech on the M5Stack.
* **Frontend**: Python code to create an interactive dashboard and visualize weather data, historical data, and upcoming forecasts. The interface utilizes Streamlit for layout and displays weather data in the form of metrics,images and chart.

## 🚀   Deployment 
 

## 🤝   Contributions
* Elias Amine Sam : Backend implementation and handling M5Stack user interface
* Hamza Khalif : Backend implementation and Frontend cloud based dashboard

## ▶️   Video  
Click 👉 [here](lien de la video) to see the video. 
