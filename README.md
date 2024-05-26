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
# IoT Application Deployment Guide with Backend on Google Cloud

This guide will walk you through the steps required to deploy an IoT application using Google Cloud, Streamlit, and M5Stack. You will start by creating a dataset and a table in Google Cloud BigQuery.

## Preliminary Step: Creating a Dataset and Table in BigQuery

In a Google Cloud project, go to BigQuery, then create a table by clicking on "Add". Here is an example: (screenshot to be added)
Next, define the schema like this: (screenshot to be added)

## Deployment Steps

The deployment is separated into three stages: the backend app, the Streamlit app, and finally, installing the code on the M5Stack.

### 1. Backend

1. Download the 3 files from the `flask_backend_app` directory and store them in the same folder.
2. Open the `backend_app.py` file. In this file, you will need to provide your personal keys for the OpenAI, OpenWeatherMap, and OpenCage APIs. You will also need to specify your Google Cloud project name, your dataset, and the table in BigQuery.
3. After this, you can follow the `deployment_tutorial` notebook to deploy the backend on Google Cloud Run. Make sure to copy and save the URL of your deployed backend.

### 2. Streamlit App

1. Download the 3 files from the `streamlit_frontend_app` directory and store them in the same folder.
2. Open the `frontend_app.py` file. Specify the URL of your backend at the beginning of the code.
3. Once this is done, similar to the backend, you can deploy the frontend on Cloud Run.

### 3. M5Stack

1. Finally, prepare your M5Stack device by connecting the 3 necessary sensors: ENVIII, TVOC eCO2, and PIR. Then configure it on your Wi-Fi to allow it to download the code.
2. Download the `M5Flow_UI.py` code and copy it into M5Flow. After this, you will need to modify the backend URL at the top of the code and also provide your Wi-Fi credentials. Finally, click on Download to upload your code to the M5Stack.

Congratulations! You can now start the device and it will begin sending data to BigQuery. You can then analyze this data via the Streamlit app.

 

## 🤝   Contributions
* Elias Amine Sam : Backend implementation and handling M5Stack user interface
* Hamza Khalif : Backend implementation and Frontend cloud based dashboard

## ▶️   Video  
Click 👉 [here](lien de la video) to see the video. 
