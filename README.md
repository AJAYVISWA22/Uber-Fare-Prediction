# Uber Fare Prediction

This Streamlit application predicts Uber fares based on user input such as pickup location, dropoff location, date, time, and passenger count. It leverages machine learning models to estimate fares for different vehicle types (mini, xuv, premium xuv) and provides a map view of the route.

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Objective](#objective)
- [Libraries](#libraries)
- [Installation](#Prerequisites)
- [Approach](#Approach)
- [Results](#Results)
- [Data Set Explanation](#DataSetExplanation)
- [Model Training](#model-training)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Contact](#contact)

## Overview

This project aims to provide a user-friendly interface for predicting Uber fare amounts based on various inputs. The predictions are made using a pre-trained machine learning model, and the application provides an interactive map to visualize the route.

## Problem Statement

Develop a machine learning model to predict the fare amount for Uber rides based on various features extracted from the ride data. Additionally, create a Streamlit web application that allows users to input ride details and get a fare estimate.


## Objective

- Ride Fare Estimation: Providing fare estimates to users before booking rides.
- Dynamic Pricing: Adjusting fare estimates based on time of day, demand, and other factors.
- Resource Allocation: Optimizing fleet management by predicting high-demand areas and times.
- User Engagement: Enhancing user experience by offering accurate fare predictions.


## Libraries

The following libraries and modules are required for this project:
- Pandas
- urllib.parse
- pymongo
- geopy
- folium
- requests
- streamlit
- numpy
- pickle
- PIL

### Prerequisites

- Python
- Streamlit
- Pandas
- Folium
- Geopy
- Requests
- Pickle
- PIL


### Approach

1. Upload the given dataset to S3 bucket.
2. Pull the data from the corresponding S3 bucket.
3. Perform required preprocessing techniques (null value handling, dtype conversion, etc.).
4. Push the cleaned data to RDS server (MySQL) cloud database.
5. Pull the cleaned data from the cloud server.
6. Train the machine learning model and save the model.
7. Create an application for the saved model.
8. Create a user interface to get user input for model prediction.

### Results

1. **Trained Model**: A regression model capable of accurately predicting Uber ride fares.
2. **Web Application**: A functional Streamlit app that allows users to get fare estimates based on ride details.
3. **Evaluation Metrics**: Detailed performance metrics for the regression model.


### Data Set Explanation

1. **Content**: The dataset contains details of Uber rides including fare amount, pickup and dropoff locations, datetime of the ride, and the number of passengers.
2. **Preprocessing Steps**:
   - Handle missing values and outliers.
   - Extract features from pickup_datetime.
   - Calculate trip distances.
   - Segment data based on time of day (morning, afternoon, evening, night).
   - Segment data based on passenger count (mini, xuv, premium xuv).

## Model Training

The fare prediction model was trained using historical Uber trip data. The model was trained using features such as passenger count, pickup date and time, vehicle type, and trip distance. The trained model (`UBER_model.pkl`) is included in the repository for making predictions.

# Project Structure

- `UBER_FARE.py`: The main Streamlit application script.
- `requirements.txt`: List of Python dependencies required for the project.
- `IMAGES/`: Directory containing images for different vehicle types.
- `UBER_model.pkl`: Pre-trained machine learning model for fare prediction.
- `README.md`: Project documentation.

# Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch with a descriptive name.
3. Make your changes and commit them.
4. Push your changes to your fork.
5. Open a pull request to the main repository.


# Contact

If you have any questions or suggestions, feel free to contact me at ajayviswa22@gmail.com

