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
import plotly.express as px

# Initialize Nominatim API
geolocator = Nominatim(user_agent="abcd")
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
    try:
        df = pd.read_csv(uploaded_file)
        # df = pd.read_csv(file_path)
        # Convert the 'TrackingCardNo' column to string format
        if 'TrackingCardNo' in df.columns:
            df['TrackingCardNo'] = df['TrackingCardNo'].apply(lambda x: str(int(x)) if pd.notnull(x) else '')
        st.success('File loaded successfully')
        
        # 2. Filter the data based on a given AccountNo
        account_no = st.text_input('Enter AccountNo to filter')
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
        

        # Plot the locations on a map using Plotly and Mapbox
        st.subheader('Transaction Locations Map')
        fig = px.scatter_mapbox(
            geo_df, 
            lat='Latitude', 
            lon='Longitude', 
            hover_name='Location', 
            hover_data={'TransactionEntryNo': True, 'TransactionDateTime': True, 'VehicleRegistrationNo': True, 'DriverFullName': True, 'Amount': True},
            color_discrete_sequence=['red'],
            zoom=5,
            height=600
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error loading file: {e}")
