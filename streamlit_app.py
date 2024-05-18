# -*- coding: utf-8 -*-
"""
Created on Sat May 18 12:26:21 2024

@author: User
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import streamlit as st
from geopy.geocoders import Nominatim 
from geopy.extra.rate_limiter import RateLimiter
import requests

# Initialize Nominatim API
geolocator = Nominatim(user_agent="geoapiExercises")
geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)

# Function to reverse geocode
def reverse_geocode(point):
    location = geocode(point, exactly_one=True)
    return location.address if location else "Unknown"

# Streamlit application
st.title('Fuel Transaction Analysis')

# Initialize an empty DataFrame
df = pd.DataFrame()

# Sidebar for user input
st.sidebar.title('User Input')

# 1. Read a CSV file and store it into a pandas DataFrame
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if uploaded_file:
# if file_path:
    try:
        df = pd.read_csv(uploaded_file)
        # df = pd.read_csv(file_path)
        st.success('File loaded successfully')
        
        # 2. Filter the data based on a given AccountNo
        account_no = st.text_input('Enter AccountNo to filter', 'AC00000011')
        filtered_df = df[df['AccountNo'] == account_no]
        
        # Display the filtered data
        st.subheader('Filtered Data')
        st.write(filtered_df)
        
        # 3. Calculate and show the total fuel transaction counts
        total_transactions = len(filtered_df)
        st.write(f'Total fuel transaction counts: {total_transactions}')
        
        # 4. Calculate and show the total fuel transaction amount in MYR
        total_amount_myr = filtered_df['Amount'].astype(float).sum()
        st.write(f'Total fuel transaction amount in MYR: {total_amount_myr}')
        
        # 5. Calculate and show the top three spending vehicles
        top_vehicles = filtered_df.groupby('VehicleRegistrationNo')['Amount'].sum().nlargest(3)
        st.subheader('Top three spending vehicles:')
        st.write(top_vehicles)
        
        # 6. Calculate and show the top three spending drivers
        top_drivers = filtered_df.groupby('DriverFullName')['Amount'].sum().nlargest(3)
        st.subheader('Top three spending drivers:')
        st.write(top_drivers)
        
        # 7. Mapping the location of each transaction and show it in the table
        # Convert to GeoDataFrame
        filtered_df['Latitude'] = filtered_df['GPSCoordinatelatitude'].astype(float)
        filtered_df['Longitude'] = filtered_df['GPSCoordinateLongitude'].astype(float)
        geometry = [Point(xy) for xy in zip(filtered_df['Longitude'], filtered_df['Latitude'])]
        geo_df = gpd.GeoDataFrame(filtered_df, geometry=geometry)
        

        # Reverse geocode the locations
        st.subheader('Geocoding GPS Coordinates...')
        #geo_df['Location'] = geo_df.apply(lambda row: reverse_geocode(row['Latitude'], row['Longitude']), axis=1)
        geo_df['Location'] = geo_df['geometry'].apply(lambda x: reverse_geocode((x.y, x.x)))

        
        # Display GeoDataFrame with location mapping
        st.subheader('Transaction Locations with Geo Coordinates')
        st.write(geo_df[['TransactionEntryNo', 'TransactionDateTime', 'VehicleRegistrationNo', 'DriverFullName', 'Amount', 'Location']])
        
        # Plot the locations on a map
        st.subheader('Transaction Locations Map')
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        world.plot(ax=ax, color='lightgrey')
        geo_df.plot(ax=ax, color='red', markersize=5, alpha=0.7)
        plt.title('Transaction Locations')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error loading file: {e}")
