import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut
import folium
import datetime
from streamlit_folium import st_folium
import requests
import pickle
import numpy as np
from PIL import Image

# Initialize the Nominatim geocoder
geolocator = Nominatim(user_agent="location_app")

# Function to determine vehicle type based on passenger count
def segment_passenger_count(count):
    if count <= 2:
        return 'mini'
    elif 3 <= count <= 4:
        return 'xuv'
    else:
        return 'premium xuv'

# Function to determine time of day based on the hour
def segment_time_of_day(hour):
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'

# Function to extract features
def features(passenger_count, pickup_date, pickup_time, distance, vehicle_type):
    day_name_mapping = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
    time_of_day_mapping = {'morning': 0, 'afternoon': 1, 'evening': 2, 'night': 3}
    vehicle_type_mapping = {'mini': 0, 'xuv': 1, 'premium xuv': 2}

    year = pickup_date.year
    month = pickup_date.month
    day = pickup_date.day
    day_name = pickup_date.strftime('%A')
    day_name = day_name_mapping[day_name]
    week_of_year = pickup_date.isocalendar()[1]
    hour = pickup_time.hour
    minutes = pickup_time.minute
    
    vehicle_type = vehicle_type_mapping[vehicle_type]
    
    time_of_day = segment_time_of_day(hour)
    time_of_day = time_of_day_mapping[time_of_day]
    
    distance_km = distance
    
    return np.array([[
        passenger_count,
        year,
        month,
        day,
        day_name,
        week_of_year,
        hour,
        minutes,
        time_of_day,
        vehicle_type,
        distance_km
    ]])

# Function to predict fare amount
def fare_predict(user_data):
    try:
        with open('UBER_model.pkl', 'rb') as f:
            model = pickle.load(f)
        y_pred = model.predict(user_data)
        fare_amount = float(y_pred[0])
        fare_amount = round(fare_amount, 2)
        return fare_amount
    except FileNotFoundError:
        st.error("Model file not found. Please ensure the model file is present.")
        return None
    except Exception as e:
        st.error(f"Error predicting fare: {e}")
        return None

# Function to get fare amount for different vehicle types
def get_fare_for_all_vehicle_types(passenger_count, pickup_date, pickup_time, distance):
    
    if passenger_count <= 4:
        vehicle_types = ['mini','xuv','premium xuv']
    else:                                        # passenger_count is 5 or 6
        vehicle_types = ['premium xuv']

    fare_amounts = {}

    for vehicle_type in vehicle_types:
        feat_data = features(passenger_count, pickup_date, pickup_time, distance, vehicle_type)
        fare_amount = fare_predict(feat_data)
        fare_amounts[vehicle_type] = fare_amount

    return fare_amounts

# Function to fetch location suggestions
def fetch_suggestions(query):
    try:
        suggestions = geolocator.geocode(query, exactly_one=False, limit=5)
        return suggestions if suggestions else []
    except GeocoderTimedOut:
        return []

# Function to get location details
def get_location_details(suggestion):
    if suggestion:
        lat = suggestion.latitude
        lon = suggestion.longitude
        address = suggestion.address
        return lat, lon, address
    else:
        return None, None, "No details available"

# Function to get OSRM route
def get_osrm_route(pickup, dropoff):
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    coordinates = f"{pickup[1]},{pickup[0]};{dropoff[1]},{dropoff[0]}"
    url = f"{base_url}{coordinates}?overview=full&geometries=geojson"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        route = data["routes"][0]["geometry"]["coordinates"]
        route = [[coord[1], coord[0]] for coord in route]
        return route
    else:
        st.error("Failed to fetch route from OSRM.")
        return None

# Function to create a map with the route
def create_map(pickup, dropoff, route_coordinates):
    pickup_lat, pickup_lng = map(float, pickup.split(','))
    dropoff_lat, dropoff_lng = map(float, dropoff.split(','))

    m = folium.Map(location=[(pickup_lat + dropoff_lat) / 2, (pickup_lng + dropoff_lng) / 2], zoom_start=13)

    folium.Marker(location=[pickup_lat, pickup_lng], popup="Pickup Location", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=[dropoff_lat, dropoff_lng], popup="Dropoff Location", icon=folium.Icon(color='red')).add_to(m)
    folium.PolyLine(locations=route_coordinates, color="black", weight=2.5).add_to(m)

    return m

# Function to get location from user input
def location_finder(user_input, label):
    if user_input:
        suggestions = fetch_suggestions(user_input)
        suggestion_names = [suggestion.address for suggestion in suggestions]

        if suggestion_names:
            selected_suggestion = st.selectbox(f"Select a suggestion for {label}", suggestion_names)
            
            if selected_suggestion:
                selected_suggestion_details = next(
                    (s for s in suggestions if s.address == selected_suggestion), None)
                lat, lon, address = get_location_details(selected_suggestion_details)
                
                if lat and lon:
                    return f"{lat},{lon}"
                else:
                    st.write(f"{label} Details not found")
                    return None
        else:
            st.write(f"No suggestions found for {label}")
            return None

def display_fare_amounts(fare_amounts):
    for vehicle_type, fare in fare_amounts.items():
        if vehicle_type == 'mini':
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                st.image("IMAGES/mini.png", width=200)
            with col2:
                st.markdown(f"""
                <div style="display: flex; align-items: center;">
                    <div>
                        <strong style="font-size: 1.5em;">Uber Mini</strong><br>
                        <span style="font-size: 1.2em;">Affordable compact rides</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div style="font-size: 2em; text-align: right; color: #4CAF50;">${fare}</div>
                """, unsafe_allow_html=True)

        elif vehicle_type == 'xuv':
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                st.image("IMAGES/xuv.png", width=200)
            with col2:
                st.markdown(f"""
                <div style="display: flex; align-items: center;">
                    <div>
                        <strong style="font-size: 1.5em;">XUV</strong><br>
                        <span style="font-size: 1.2em;">Comfortable sedans, top-quality drivers</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div style="font-size: 2em; text-align: right; color: #4CAF50;">${fare}</div>
                """, unsafe_allow_html=True)

        elif vehicle_type == 'premium xuv':
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                st.image("IMAGES/premium_xuv.png", width=200)
            with col2:
                st.markdown(f"""
                <div style="display: flex; align-items: center;">
                    <div>
                        <strong style="font-size: 1.5em;">Premium XUV</strong><br>
                        <span style="font-size: 1.2em;">Premium SUVs with top-notch services</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div style="font-size: 2em; text-align: right; color: #4CAF50;">${fare}</div>
                """, unsafe_allow_html=True)



# Input page to get ride details from user
def Input_page():
    st.title("Get a Ride")
    st.subheader("Enter ride details")

    col1, col2 = st.columns([1, 4])

    with col1:
        pickup_location_name = st.text_input("Pickup Location")
        dropoff_location_name = st.text_input("Dropoff Location")
        pickup_location = location_finder(pickup_location_name, "Pickup")
        dropoff_location = location_finder(dropoff_location_name, "Dropoff")

        if pickup_location and dropoff_location:
            pickup_lat, pickup_lng = map(float, pickup_location.split(','))
            dropoff_lat, dropoff_lng = map(float, dropoff_location.split(','))
            distance = geodesic((pickup_lat, pickup_lng), (dropoff_lat, dropoff_lng)).km
        else:
            distance = None  # Set to None if locations are not available

        current_date = datetime.date.today()
        pickup_date = st.date_input("Pickup Date", current_date)
        pickup_time = st.time_input("Pickup Time")
        passenger_count = st.number_input("Passenger Count", min_value=1, max_value=6)

        if st.button("Get Ride Details"):
            if pickup_location and dropoff_location:
                route_coordinates = get_osrm_route((pickup_lat, pickup_lng), (dropoff_lat, dropoff_lng))
                if route_coordinates:
                    st.session_state.map = create_map(pickup_location, dropoff_location, route_coordinates)

                    fare_amounts = get_fare_for_all_vehicle_types(passenger_count, pickup_date, pickup_time, distance)
                   
                    st.session_state.fare_amounts = fare_amounts
               
    with col2:
        if pickup_location and dropoff_location:
            st.write("Ride Details:")
            col1, col2, col3 = st.columns(3)
            col1.write(f"Pickup: {pickup_location}")
            col2.write(f"Dropoff: {dropoff_location}")
            col3.write(f"Distance: {distance:.2f} km")

            # Display map
            if st.session_state.map:
                st_folium(st.session_state.map, height=600, width=1000)
        else:
            st.write("Please enter all details and press 'Get Ride Details' to see the results.")
    
    # Check if fare_amounts is not None before formatting it
    if st.session_state.fare_amounts:
        display_fare_amounts(st.session_state.fare_amounts)

# Main function to run the Streamlit app
def streamlit_app():
    st.set_page_config(layout="wide")

    # Initialize session state variables
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False
    if "map" not in st.session_state:
        st.session_state.map = None
    if "fare_amounts" not in st.session_state:
        st.session_state.fare_amounts = None

    try:
        image = Image.open("IMAGES/Ride-with-Uber.webp")
    except FileNotFoundError:
        st.error("Image file not found. Please check the path.")
        image = None

    col1, col2 = st.columns([2, 3])

    if not st.session_state.button_clicked:
        with col1:
            st.title("Go anywhere with Uber")
            st.subheader("Request a ride, hop in, and go.")
            st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
            
            if st.button("See prices"):
                st.session_state.button_clicked = True

        with col2:
            if image:
                st.image(image, width=550)
    else:
        Input_page()

# Run the Streamlit app
streamlit_app()
