import re
import json
import os
import hashlib
import smtplib
import platform
import sqlite3
import math
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.font_definitions import theme_font_styles
from kivymd.icon_definitions import md_icons
from kivymd.uix.card import MDCard
from email.mime.text import MIMEText
from twilio.rest import Client
from kivymd.uix.dialog import MDDialog
from kivy.uix.textinput import TextInput
from kivymd.uix.progressbar import MDProgressBar
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivy.utils import get_color_from_hex
from kivy.properties import ListProperty
from kivy.uix.dropdown import DropDown
from kivymd.uix.textfield import MDTextField
from plyer import camera
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.logger import Logger
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.slider import MDSlider
from kivy.uix.spinner import Spinner
from kivymd.uix.list import OneLineListItem
import cv2
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.popup import Popup
from plyer import filechooser
from kivymd.uix.pickers import MDTimePicker
from datetime import datetime
from kivy.graphics.texture import Texture
from plyer import gps
from kivy.utils import platform  # To check the platform
import requests
from geopy.geocoders import Nominatim
from kivy_garden.mapview import MapView
#from kivy_garden.mapview import MapMarkerPopup
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivymd.uix.toolbar import MDTopAppBar
from kivy.clock import mainthread
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from twilio.rest import Client
import threading
import webbrowser
import time

Window.size = (350, 600)


def show_message(message):
    dialog = MDDialog(text=message)
    dialog.open()

class AccidentMarker(MapMarkerPopup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set properties specific to the accident marker
        self.color = (1, 0, 0, 1)  # Red color for accident marker

class HospitalMarker(MapMarkerPopup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set properties specific to the hospital marker
        self.color = (0, 1, 0, 1)  # Green color for hospital marker


class CustomSpinnerDropDown(DropDown):
    pass

class PhoneValidationScreen(Screen):
    pass

class LoginPage(MDApp):
    icon_color = ListProperty([0.8, 0.8, 0.8, 1])  # Default gray

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = self.load_credentials() or {}  # Initialize user_data

    def build(self):
        print("App is starting")

        # Load the screen manager and kv files

        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(Builder.load_file("pre-splash.kv"))
        self.screen_manager.add_widget(Builder.load_file("signup.kv"))
        self.screen_manager.add_widget(Builder.load_file("home.kv"))
        self.screen_manager.add_widget(Builder.load_file("adduser.kv"))
        self.screen_manager.add_widget(Builder.load_file("account-details.kv"))
        self.screen_manager.add_widget(Builder.load_file("report.kv"))
        self.screen_manager.add_widget(Builder.load_file("news.kv"))
        self.screen_manager.add_widget(Builder.load_file("quickGuide.kv"))
        self.screen_manager.add_widget(Builder.load_file("track_location.kv"))
        self.screen_manager.add_widget(Builder.load_file("near_hospitals.kv"))
        self.screen_manager.add_widget(Builder.load_file("bed_availability.kv"))
        self.screen_manager.add_widget(Builder.load_file("near_police_stations.kv"))
        self.screen_manager.add_widget(Builder.load_file("police_availability.kv"))
        self.screen_manager.add_widget(Builder.load_file("inform_family.kv"))
        self.screen_manager.add_widget(Builder.load_file("self_picking.kv"))
        self.screen_manager.add_widget(Builder.load_file("last-step.kv"))

        # Start updating the progress bar after the app starts
        Clock.schedule_interval(self.update_progress_bar, 0.2)

        self.capture = None  # This will hold the OpenCV camera capture object
        # Initialize the SQLite3 database

        Logger.setLevel('DEBUG')  # Set logging to DEBUG level
        self.setup_database()

        self.fetch_latest_news()
        # Ensure the accident count is updated when entering the home screen
        home_screen = self.screen_manager.get_screen('home')
        home_screen.bind(on_enter=self.get_accident_count)


        # Create the accident type dropdown menu
        self.accident_menu_items = [
            {"viewclass": "OneLineListItem", "text": "Vehicle Accident",
             "on_release": lambda x="Vehicle Accident": self.set_accident_type(x)},
            {"viewclass": "OneLineListItem", "text": "Bike Accident",
             "on_release": lambda x="Bike Accident": self.set_accident_type(x)},
            {"viewclass": "OneLineListItem", "text": "Pedestrian Accident",
             "on_release": lambda x="Pedestrian Accident": self.set_accident_type(x)},
            {"viewclass": "OneLineListItem", "text": "Other",
             "on_release": lambda x="Other": self.set_accident_type(x)},
        ]

        self.menu_accident = MDDropdownMenu(
            caller=self.screen_manager.get_screen('report').ids.accident_field,
            items=self.accident_menu_items,
            width_mult=4
        )

        # Create the persons status dropdown menu
        self.persons_status_items = [
            {"viewclass": "OneLineListItem", "text": "Normal",
             "on_release": lambda x="Normal": self.set_persons_status(x)},
            {"viewclass": "OneLineListItem", "text": "Medium",
             "on_release": lambda x="Medium": self.set_persons_status(x)},
            {"viewclass": "OneLineListItem", "text": "Serious",
             "on_release": lambda x="Serious": self.set_persons_status(x)},
            {"viewclass": "OneLineListItem", "text": "Very Serious",
             "on_release": lambda x="Very Serious": self.set_persons_status(x)},
        ]

        self.menu_person_status = MDDropdownMenu(
            caller=self.screen_manager.get_screen('report').ids.persons_status_field,
            items=self.persons_status_items,
            width_mult=4
        )

        if platform == 'android' or platform == 'ios':
            lat, lon = self.get_gps_location()
        else:
            lat, lon = self.get_ip_location()

        if lat and lon:
            print(f"Latitude: {lat}, Longitude: {lon}")
            address = self.get_address(lat, lon)
            print(f"Address: {address}")
        else:
            print("Could not retrieve location.")


        return self.screen_manager

    # -------------------set current time ------------------------------------
    def set_current_time(self):
        # Get current time
        current_time = datetime.now().strftime("%I:%M %p")  # Format: Hour:Minute AM/PM
        print(f"Current time: {current_time}")

        # Set the current time in the TextField
        time_screen = self.root.get_screen('track_location')  # Assuming your screen is 'track_location'
        time_screen.ids.time_fieldT.text = current_time  # Set the current time to the MDTextField
        time_screen.ids.time_fieldM.text = current_time
    # -------------------set current time ------------------------------------



    # -------------------News disply ________________________________________

    @mainthread
    def display_news(self, articles):
        # Fetch the Carousel by its id
        news_screen = self.screen_manager.get_screen('news')
        news_carousel = news_screen.ids.news_carousel

        # Clear any previous content
        news_carousel.clear_widgets()

        # Loop through the articles and create cards for each one
        for article in articles:
            title = article.get('title', "No Title")
            description = article.get('description', "No Description")
            url = article.get('url', "#")

            # Create a card layout for each news article
            card = MDCard(orientation='vertical', size_hint=(0.95, 1),
                          padding=15, spacing=30, pos_hint={"center_x": 0.5, "center_y": 0.4})

            # Add title
            title_label = MDLabel(text=title, theme_text_color="Primary", font_style="H6", halign="center")
            card.add_widget(title_label)

            # Add space between title and description
            space = Widget(size_hint_y=None, height=dp(10))  # Add space of 10dp (or any desired size)
            card.add_widget(space)

            # Add description
            description_label = MDLabel(text=description, theme_text_color="Secondary", size_hint_y=None, halign="center",  height=dp(60))
            card.add_widget(description_label)

            # Add button to open the article URL
            open_button = MDRaisedButton(
                text="Read More",
                pos_hint={"center_x": 0.5},
                on_release=self.create_open_news_callback(url)  # Use a helper function
            )
            card.add_widget(open_button)

            # Add the card to the carousel
            news_carousel.add_widget(card)

    def create_open_news_callback(self, url):
        # Helper function to return a lambda that correctly binds the URL
        return lambda *args: self.open_news(url)
    def open_news(self, url):
        # Function to open the article URL (you can use web browser or other means)
        import webbrowser
        if url != "#":
            webbrowser.open(url)

    def fetch_latest_news(self):
        api_key = '3bd2454fba4b4198856b6265d5d0faf3'
        query = 'road accidents Malaysia'  # Search for road accidents related to Malaysia
        url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={api_key}"

        try:
            response = requests.get(url)
            data = response.json()

            if data['status'] == 'ok':
                articles = data.get('articles', [])
                print(f"Fetched {len(articles)} articles")
                self.display_news(articles)  # Display the articles in cards
            else:
                print(f"Error fetching news: {data.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"Error fetching news: {e}")


    def switch_to_news_screen(self):
        # Call this method to switch to the news screen after fetching the news
        self.screen_manager.current = 'news'

    # ------------------  News display  --------------------------------------------

    # ----------------------------for database part--------------------------
    def setup_database(self):
        # Connect to SQLite database
        db_path = os.path.abspath('accidents.db')
        print(f"Database path: {db_path}")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        # Create table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accident_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                accident_type TEXT,
                injury_count INTEGER,
                person_status TEXT,
                person_photo BLOB,
                accident_location TEXT,
                latitude REAL,
                longitude REAL,
                time TEXT
            )
        ''')
        self.conn.commit()

    def store_data(self, accident_type, injury_count, persons_status, photo_path, accident_location, latitude, longitude, time_taken):
        try:
            print(
                f"Inserting data: {accident_type}, {injury_count},{persons_status}, {photo_path}, {accident_location}, {latitude}, {longitude}, {time_taken}")
            # Read photo as binary data
            with open(photo_path, 'rb') as file:
                photo_data = file.read()

            # Insert the collected data into the SQLite database
            self.cursor.execute('''
                INSERT INTO accident_reports (
                    accident_type, injury_count, person_status, person_photo, accident_location, latitude, longitude, time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (accident_type, injury_count, persons_status, photo_data, accident_location, latitude, longitude, time_taken))

            self.conn.commit()
            print("Data stored successfully.")
            # Debug: Check if rows are inserted
            self.cursor.execute('SELECT COUNT(*) FROM accident_reports')
            row_count = self.cursor.fetchone()[0]
            print(f"Total records in database: {row_count}")
        except Exception as e:
            print(f"Error storing data: {e}")

    # --------------update the accident count value in home page-------------

    def get_accident_count(self, *args):
        # Connect to the SQLite database
        db_path = os.path.abspath('accidents.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # Execute the query to get the count of records
        self.cursor.execute("SELECT COUNT(*) FROM accident_reports")
        accident_count = self.cursor.fetchone()[0]

        # Close the connection
        #self.conn.close()

        # Update the label in the UI
        self.update_accident_count_label(accident_count)

    @mainthread
    def update_accident_count_label(self, count):
        # Find the MDLabel by ID and update the text
        self.root.get_screen('home').ids.accident_count_label.text = str(count)

    # -------------update the accident count value in home page--------------



    def submit_report(self):
        # Collect data from UI elements

        print("Submit report called")  # Debug: Ensure this function is called
        accident_type = self.screen_manager.get_screen('report').ids.accident_field.text
        injury_count = int(self.selected_count) if hasattr(self, 'selected_count') else 0
        persons_status=self.screen_manager.get_screen('report').ids.persons_status_field.text
        photo_path = 'captured_photo_opencv.jpg'  # Assuming the captured photo is saved here
        accident_location = self.screen_manager.get_screen('track_location').ids.accident_location_field1.text
        latitude = float(self.screen_manager.get_screen('track_location').ids.latitude_field1.text)
        longitude = float(self.screen_manager.get_screen('track_location').ids.longitude_field1.text)
        time_taken = self.screen_manager.get_screen('track_location').ids.time_fieldT.text

        # Store data in the database
        self.store_data(accident_type, injury_count, persons_status, photo_path, accident_location, latitude, longitude, time_taken)

        # Fetch the 5 nearest hospitals
        nearest_hospitals = self.fetch_nearest_hospitals(latitude, longitude)

        # Pass the data to the map screen to display
        Clock.schedule_once(lambda dt: self.display_nearest_hospitals(nearest_hospitals), 2)
        print(f"Nearest Hospitals: {nearest_hospitals}")
        """
        # Fetch the 5 nearest police stations
        nearest_police_stations=self.fetch_nearest_police_stations(latitude,longitude)

        # Pass the data to the map screen to display
        Clock.schedule_once(lambda dt: self.display_nearest_police_stations(nearest_police_stations), 5)
        print(f"Nearest Police Stations: {nearest_police_stations}")
        """

    def get_lat_long(self):
        latitude = float(self.screen_manager.get_screen('track_location').ids.latitude_field1.text)
        longitude = float(self.screen_manager.get_screen('track_location').ids.longitude_field1.text)

        # Fetch the 5 nearest police stations
        nearest_police_stations = self.fetch_nearest_police_stations(latitude, longitude)

        # Pass the data to the map screen to display
        Clock.schedule_once(lambda dt: self.display_nearest_police_stations(nearest_police_stations), 2)
        print(f"Nearest Police Stations: {nearest_police_stations}")
    


    # Connect to the hospital_availability.db database (it will create the file if it doesn't exist)
    conn = sqlite3.connect('hospital_availability.db')
    cursor = conn.cursor()

    # Create the table for hospital availability
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bed_availability (
        name TEXT PRIMARY KEY,          -- Name of the hospital
        total_beds INTEGER,              -- Total number of beds
        used_beds INTEGER,               -- Number of beds currently in use
        availability TEXT                -- Availability status (e.g., 'Available', 'Full', etc.)
    )
    ''')
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    def fetch_nearest_hospitals(self, accident_lat, accident_lon):
        try:
            # Connect to the hospital database
            hospital_conn = sqlite3.connect('hospital_database.db')
            hospital_cursor = hospital_conn.cursor()

            # Get all hospitals' data (name, address, latitude, longitude)
            hospital_cursor.execute('SELECT name, address, latitude, longitude FROM hospitals')
            hospitals = hospital_cursor.fetchall()

            # List to store hospitals with their distances
            hospitals_with_distance = []

            # Calculate distance from the accident location to each hospital
            for hospital in hospitals:
                hospital_name, hospital_address, hospital_lat, hospital_lon = hospital
                distance = self.calculate_distance(accident_lat, accident_lon, hospital_lat, hospital_lon)
                hospitals_with_distance.append((hospital_name, hospital_address, hospital_lat, hospital_lon, distance))

            # Sort hospitals by distance
            hospitals_with_distance.sort(key=lambda x: x[4])

            # Get the 5 nearest hospitals
            nearest_hospitals = hospitals_with_distance[:5]

            # Close the hospital database connection
            hospital_conn.close()

            return nearest_hospitals

        except Exception as e:
            print(f"Error fetching nearest hospitals: {e}")
            return []

    def display_nearest_hospitals(self, hospitals):
        # Access the ListView from the 'near_hospitals' screen
        map_screen = self.screen_manager.get_screen('near_hospitals')
        hospital_list = map_screen.ids.hospital_list  # Reference the hospital list via its ID

        # Clear previous items to avoid duplication
        hospital_list.clear_widgets()

        # Add each hospital to the list
        for hospital in hospitals:
            name, address, lat, lon, distance = hospital
            hospital_item = OneLineListItem(
                text=f"{name} - {distance:.2f} km",
                on_release=lambda item: (
                    print(f"Hospital Name: '{item.text.split(' - ')[0]}'"),  # Debug print
                    self.open_hospital_availability(item.text.split(' - ')[0])  # Get only the name
                )[1]  # Use a tuple to execute both statements
            )
            hospital_list.add_widget(hospital_item)

        # Switch to the near_hospitals screen
        self.switch_to_screen('near_hospitals')


    def open_hospital_availability(self, hospital_name):
        hospital_name = hospital_name.strip()
        print(f"Hospital Name: {hospital_name}, Type: {type(hospital_name)}")
        name=hospital_name

        # Assuming you have a database connection setup
        try:
            conn = sqlite3.connect('hospital_availability.db')
            cursor = conn.cursor()

            # Fetch availability data for the selected hospital
            cursor.execute('''SELECT total_beds, used_beds, availability 
                              FROM bed_availability 
                              WHERE name = ?''', (hospital_name,))
            data = cursor.fetchone()
            conn.close()
            if data:
                total_beds, used_beds, availability = data
                # Process the retrieved data (for example, displaying it in a label)
                self.display_hospital_data(hospital_name, total_beds, used_beds, availability)

            else:
                print("No data found for the selected hospital.")
                # Show a message to the user that no data was found
                #self.show_no_data_message(hospital_name)

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

        return name

    def display_hospital_data(self, hospital_name, total_beds, used_beds, availability):
        # Assuming you have a screen or layout where you display this information

        info_screen = self.screen_manager.get_screen('bed_availability')  # Make sure you have the correct screen name
        info_screen.ids.hospital_name.text = hospital_name
        info_screen.ids.total_beds.text = f"Total Beds: {total_beds}"
        info_screen.ids.available_beds.text = f"Available Beds: {total_beds-used_beds}"
        info_screen.ids.icu_availability.text = f"ICU Availability: {'Available' if availability else 'Not Available'}"

        #self.inform_to_hospital(hospital_name)
        # Switch to the info screen to show the details
        self.switch_to_screen('bed_availability')

    def inform_to_hospital(self):
        # Twilio credentials
        account_sid = 'AC0b4f8d11643236f1b586f5cbefaaf0e1'
        auth_token = 'd9f9562373ef34622d2fd8e27a45dd04'
        client = Client(account_sid, auth_token)

        hospital_name = self.screen_manager.get_screen('bed_availability').ids.hospital_name.text
        hospital_name = hospital_name.strip()

        if not hospital_name:
            print("No hospital selected.")
            return
        # Retrieve the contact number from the hospital_availability.db based on the hospital's name or other identifier
        #hospital_name = hospital_name  # Replace with the selected hospital's name or ID
        connection = sqlite3.connect("hospital_availability.db")
        cursor = connection.cursor()
        cursor.execute("SELECT contact_no FROM bed_availability WHERE name = ?", (hospital_name,))
        result = cursor.fetchone()
        contact_number = result[0] if result else None
        connection.close()

        if not contact_number:
            print("No contact number found for the hospital.")
            return

        # Retrieve accident details from accidents.db
        connection = sqlite3.connect("accidents.db")
        cursor = connection.cursor()
        cursor.execute(
            "SELECT accident_type, injury_count, person_status, accident_location, time, latitude, longitude FROM accident_reports ORDER BY id DESC LIMIT 1")
        accident_details = cursor.fetchone()
        connection.close()

        if not accident_details:
            print("No accident data available.")
            return

        # Format the message
        accident_type, injury_count, person_status, location, time, lat, lon = accident_details
        message_body = (
            f"Accident Notification:\n"
            f"Type: {accident_type}\n"
            f"Injuries: {injury_count}\n"
            f"Status: {person_status}\n"
            f"Location: {location} at {time}\n"
            f"Coordinates: ({lat}, {lon})"
        )

        # Send SMS
        message = client.messages.create(
            body=message_body,
            from_='+15597937204',
            to=contact_number
        )

        print(f"Message sent to {contact_number}. Message SID: {message.sid}")



    def on_stop(self):
        # Close the SQLite database connection on exit
        self.conn.close()

    def fetch_data(self):
        # Fetch all data from the `accident_reports` table
        self.cursor.execute("SELECT * FROM accident_reports")
        rows = self.cursor.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("No data found.")


        # ----------------------------for mapping part--------------------------------------
    def calculate_distance(self,lat1, lon1, lat2, lon2):
        # Convert latitude and longitude from degrees to radians
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        radius_of_earth = 6371  # Radius of the Earth in kilometers
        distance = radius_of_earth * c

        return distance





    # ----------------------------for police station mapping part--------------------------------------
    def calculate_distance_police(self,lat1, lon1, lat2, lon2):
        # Convert latitude and longitude from degrees to radians
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        radius_of_earth = 6371  # Radius of the Earth in kilometers
        distance = radius_of_earth * c

        return distance




    conn = sqlite3.connect('police_stations.db')
    cursor = conn.cursor()

    # Create the table for hospital availability
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS police_station_list (
            name TEXT PRIMARY KEY,          -- Name of the hospital
            address INTEGER,              -- Total number of beds
            latitude REAL,               -- Number of beds currently in use
            longitude REAL,                -- Availability status (e.g., 'Available', 'Full', etc.)
            contact_no TEXT DEFAULT '60196764038'
            )
        ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    def fetch_nearest_police_stations(self, accident_lat, accident_lon):
        print("Fetching nearest police stations...")
        try:
            # Connect to the police stations database
            police_conn = sqlite3.connect('police_stations.db')
            police_cursor = police_conn.cursor()

            # Get all police stations' data (name, address, latitude, longitude)
            police_cursor.execute('SELECT name, address, latitude, longitude FROM police_station_list')
            stations = police_cursor.fetchall()
            print(stations)
            # List to store police stations with their distances
            stations_with_distance = []

            # Calculate distance from the accident location to each police station
            for station in stations:
                station_name, station_address, station_lat, station_lon = station
                distance = self.calculate_distance_police(accident_lat, accident_lon, station_lat, station_lon)
                stations_with_distance.append((station_name, station_address, station_lat, station_lon, distance))

            # Sort police stations by distance
            stations_with_distance.sort(key=lambda x: x[4])

            # Get the 5 nearest police stations
            nearest_stations = stations_with_distance[:5]

            # Close the police station database connection
            police_conn.close()
            print("Police stations fetched successfully.")
            print(nearest_stations)
            return nearest_stations

        except Exception as e:
            print(f"Error fetching nearest police stations: {e}")
            return []

    def display_nearest_police_stations(self, stations):
        # Access the ListView from the 'near_police_stations' screen
        map_screen = self.screen_manager.get_screen('near_police_stations')
        station_list = map_screen.ids.station_list  # Reference the police station list via its ID

        # Clear previous items to avoid duplication
        station_list.clear_widgets()

        # Add each police station to the list
        for station in stations:
            name, address, lat, lon, distance = station
            station_item = OneLineListItem(
                text=f"{name} - {distance:.2f} km",
                on_release=lambda item: (
                    print(f"Police Station Name: '{item.text.split(' - ')[0]}'"),  # Debug print
                    self.open_station_availability(item.text.split(' - ')[0])  # Send notification
                )[1]
            )
            station_list.add_widget(station_item)

        # Switch to the near_police_stations screen
        self.switch_to_screen('near_police_stations')
    
    def open_station_availability(self, station_name):
        station_name = station_name.strip()
        print(f"Station Name: {station_name}, Type: {type(station_name)}")
        name=station_name

        # Assuming you have a database connection setup
        try:
            conn = sqlite3.connect('police_stations.db')
            cursor = conn.cursor()

            # Fetch availability data for the selected hospital
            cursor.execute('''SELECT name, latitude, longitude,contact_no 
                              FROM police_station_list
                              WHERE name = ?''', (station_name,))
            data = cursor.fetchone()
            conn.close()
            if data:
                name, latitude, longitude,contact_no = data
                # Process the retrieved data (for example, displaying it in a label)
                self.display_station_data(station_name, latitude, longitude,contact_no)

            else:
                print("No data found for the selected station.")
                # Show a message to the user that no data was found
                #self.show_no_data_message(hospital_name)

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

        return name

    def display_station_data(self, station_name, latitude, longitude,contact_no):
        # Assuming you have a screen or layout where you display this information

        info_screen = self.screen_manager.get_screen('police_availability')  # Make sure you have the correct screen name
        info_screen.ids.station_name.text = station_name
        info_screen.ids.lat.text = f"Latitude: {latitude}"
        info_screen.ids.long.text = f"Longitude: {longitude}"
        info_screen.ids.contact_no.text = f"Contact Details: {contact_no}"

        #self.inform_to_hospital(hospital_name)
        # Switch to the info screen to show the details
        self.switch_to_screen('police_availability')

    
    
    
    
    
    def inform_to_police_station(self):
        # Twilio credentials
        account_sid = 'AC0b4f8d11643236f1b586f5cbefaaf0e1'
        auth_token = 'd9f9562373ef34622d2fd8e27a45dd04'
        client = Client(account_sid, auth_token)

        station_name = self.screen_manager.get_screen('police_availability').ids.station_name.text
        station_name = station_name.strip()

        if not station_name:
            print("No Station selected.")
            return

        connection = sqlite3.connect("police_stations.db")
        cursor = connection.cursor()
        cursor.execute("SELECT contact_no FROM police_station_list WHERE name = ?", (station_name,))
        result = cursor.fetchone()
        contact_number = result[0] if result else None
        connection.close()

        if not contact_number:
            print("No contact number found for the police station.")
            return

        # Retrieve accident details from accidents.db
        connection = sqlite3.connect("accidents.db")
        cursor = connection.cursor()
        cursor.execute(
            "SELECT accident_type, injury_count, person_status, accident_location, time, latitude, longitude FROM accident_reports ORDER BY id DESC LIMIT 1")
        accident_details = cursor.fetchone()
        connection.close()

        if not accident_details:
            print("No accident data available.")
            return

        # Format the message
        accident_type, injury_count, person_status, location, time, lat, lon = accident_details
        message_body = (
            f"Accident Notification:\n"
            f"Type: {accident_type}\n"
            f"Injuries: {injury_count}\n"
            f"Status: {person_status}\n"
            f"Location: {location} at {time}\n"
            f"Coordinates: ({lat}, {lon})"
        )

        # Send SMS
        message = client.messages.create(
            body=message_body,
            from_='+15597937204',
            to=contact_number
        )

        print(f"Message sent to {contact_number}. Message SID: {message.sid}")


    """
    def get_location(self):
        try:
            latitude = float(self.screen_manager.get_screen('track_location').ids.latitude_field1.text) or \
                           float(self.screen_manager.get_screen('track_location').ids.latitude_field.text)

            longitude = float(self.screen_manager.get_screen('track_location').ids.longitude_field1.text) or \
                            float(self.screen_manager.get_screen('track_location').ids.longitude_field.text)

            self.screen_manager.get_screen('inform_family').ids.latitude_field.text=latitude
            self.screen_manager.get_screen('inform_family').ids.longitude_field.text = longitude

            #return latitude,longitude
        except ValueError:
            print("Invalid location input.")
    """

    def get_location(self):
        # Retrieve text values from the fields
        lat_text1 = self.screen_manager.get_screen('track_location').ids.latitude_field1.text
        lat_text2 = self.screen_manager.get_screen('track_location').ids.latitude_field.text
        lon_text1 = self.screen_manager.get_screen('track_location').ids.longitude_field1.text
        lon_text2 = self.screen_manager.get_screen('track_location').ids.longitude_field.text

        try:
            # Try converting to float only if the text is not empty
            latitude = lat_text1 if lat_text1 else lat_text2
            longitude = lon_text1 if lon_text1 else lon_text2
            self.screen_manager.get_screen('inform_family').ids.latitude_field.text = latitude
            self.screen_manager.get_screen('inform_family').ids.longitude_field.text = longitude
            return latitude,longitude

        except ValueError:
            print("Invalid location input.")
            return None

    def call_parents(self):
        #latitude,longitude=self.get_location()
        phone_number = self.screen_manager.get_screen('inform_family').ids.number_field.text
        account_sid = 'AC0b4f8d11643236f1b586f5cbefaaf0e1'
        auth_token = 'd9f9562373ef34622d2fd8e27a45dd04'
        client = Client(account_sid, auth_token)

        connection = sqlite3.connect("accidents.db")
        cursor = connection.cursor()
        cursor.execute(
            "SELECT accident_type, injury_count, person_status, accident_location, time, latitude, longitude FROM accident_reports ORDER BY id DESC LIMIT 1")
        accident_details = cursor.fetchone()
        connection.close()

        if not accident_details:
            print("No accident data available.")
            return

        accident_type, injury_count, person_status, location, time, lat, lon = accident_details
        message_body = (
            f"Accident Notification:\n"
            f"Type: {accident_type}\n"
            f"Injuries: {injury_count}\n"
            f"Status: {person_status}\n"
            f"Location: {location} at {time}\n"
            f"Coordinates: ({lat}, {lon})"
        )

        # Send SMS
        message = client.messages.create(
            body=message_body,
            from_='+15597937204',
            to=phone_number
        )

        print(f"Message sent to {phone_number}. Message SID: {message.sid}")


    """ worked 
    def load_map(self):
        # Get accident coordinates from the screen input
        acc_lat = float(self.screen_manager.get_screen('track_location').ids.latitude_field1.text)
        acc_long = float(self.screen_manager.get_screen('track_location').ids.longitude_field1.text)

        # Get the MapView widget
        map_screen = self.screen_manager.get_screen('self_picking')
        map_view = map_screen.ids.map_view  # Ensure there's an ID for MapView in `map_screen.kv`

        # Center the map on the accident location
        map_view.center_on(acc_lat, acc_long)

        # Add an accident marker
        accident_marker = AccidentMarker(lat=acc_lat, lon=acc_long)
        accident_marker.add_widget(Label(text="Accident Location", color=(0, 1, 0, 1)))  # Green label for visibility
        map_view.add_marker(accident_marker)

        # Fetch nearest hospitals
        nearest_hospitals = self.fetch_nearest_hospitals(acc_lat, acc_long)

        # Add markers for each hospital
        for hospital in nearest_hospitals:
            name, address, lat, lon, distance = hospital
            hospital_marker = HospitalMarker(lat=lat, lon=lon)
            hospital_marker.add_widget(
                Label(text=f"{name} ({distance:.2f} km)", color=(1, 0, 0, 1)))  # Red label for visibility
            map_view.add_marker(hospital_marker)

        self.switch_to_screen('self_picking')
    """

    def load_map(self):
        # Get accident coordinates from the screen input
        acc_lat = float(self.screen_manager.get_screen('track_location').ids.latitude_field1.text)
        acc_long = float(self.screen_manager.get_screen('track_location').ids.longitude_field1.text)

        # Get the MapView widget
        map_screen = self.screen_manager.get_screen('self_picking')
        map_view = map_screen.ids.map_view  # Ensure there's an ID for MapView in `map_screen.kv`

        # Center the map on the accident location
        map_view.center_on(acc_lat, acc_long)

        # Add an accident marker
        accident_marker = AccidentMarker(lat=acc_lat, lon=acc_long)
        accident_marker.add_widget(Label(text="Accident Location", color=(0, 1, 0, 1)))  # Green label for visibility
        map_view.add_marker(accident_marker)

        # Fetch nearest hospitals
        nearest_hospitals = self.fetch_nearest_hospitals(acc_lat, acc_long)

        # Add markers for each hospital
        for hospital in nearest_hospitals:
            name, address, lat, lon, distance = hospital
            hospital_marker = HospitalMarker(lat=lat, lon=lon)
            hospital_marker.add_widget(
                Label(text=f"{name} ({distance:.2f} km)", color=(1, 0, 0, 1)))  # Red label for visibility
            hospital_marker.bind(
                on_release=lambda marker, name=name, lat=lat, lon=lon: self.show_route_to_hospital(acc_lat, acc_long,
                                                                                                   lat, lon))
            map_view.add_marker(hospital_marker)

        self.switch_to_screen('self_picking')

    def show_route_to_hospital(self, acc_lat, acc_long, hospital_lat, hospital_lon):
        # Create a URL for Google Maps with the accident and hospital coordinates
        url = f"https://www.google.com/maps/dir/?api=1&origin={acc_lat},{acc_long}&destination={hospital_lat},{hospital_lon}"
        # Open the URL in a web browser
        webbrowser.open(url)


    def validate_phone_number(self, phone_number):
        # Regex pattern for a "+" sign followed by 11 digits
        pattern = r'^\+?\d{11}$'
        if re.match(pattern, phone_number):
            show_message("Valid Number")
        else:
            print("Invalid. Format should be + followed by 11 digits")



    # set lat,long taken from ip address for testing purposes part's text fields
    def on_get_ip_location(self):
        # Retrieve the IP location
        lat, lon = self.get_ip_location()
        if lat is not None and lon is not None:
            # Update the text fields with the retrieved latitude and longitude
            self.screen_manager.get_screen('track_location').ids.latitude_field1.text = str(lat)
            self.screen_manager.get_screen('track_location').ids.longitude_field1.text = str(lon)

            # Get the address from the latitude and longitude
            address = self.get_address(lat, lon)
            if address:
                # Set the address in the accident location text field
                self.screen_manager.get_screen('track_location').ids.accident_location_field1.text = address
            else:
                show_message("Could not retrieve address.")
        else:
            show_message("Could not retrieve IP location.")

    def get_ip_location(self):
        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()
            location = data.get('loc')  # Format: "latitude,longitude"
            if location:
                lat, lon = map(float, location.split(','))
                return lat, lon
            else:
                print("Location data not available")
                return None, None
        except Exception as e:
            print(f"Error fetching location: {e}")
            return None, None

    # get lat, long from get_gps_location for mobile app part
    def on_get_location(self):
        # Retrieve the GPS location
        lat, lon = self.get_gps_location()
        if lat is not None and lon is not None:
            # Update the text fields with the retrieved latitude and longitude
            self.screen_manager.get_screen('track_location').ids.latitude_field.text = str(lat)
            self.screen_manager.get_screen('track_location').ids.longitude_field.text = str(lon)
            # Get the address from the latitude and longitude
            address = self.get_address(lat, lon)
            if address:
                # Set the address in the accident location text field
                self.screen_manager.get_screen('track_location').ids.accident_location_field.text = address
            else:
                show_message("Could not retrieve address.")
        else:
            show_message("Could not retrieve GPS location.")

    def get_gps_location(self):
        try:
            # Start GPS
            gps.configure(on_location=self.on_location, on_error=self.on_error)
            gps.start()
            Logger.info("GPS: Starting to get location...")
            return None, None  # Initially return None until the location is updated
        except Exception as e:
            Logger.error(f"Error starting GPS: {e}")
            return None, None

    def on_location(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        if lat is not None and lon is not None:
            Logger.info(f"GPS: Location updated - Latitude: {lat}, Longitude: {lon}")
            address = self.get_address(lat, lon)
            Logger.info(f"GPS: Address: {address}")
            return lat, lon
        else:
            Logger.warning("GPS: Location data not available")
            return None, None

    def on_error(self, **kwargs):
        Logger.error(f"GPS: Error occurred - {kwargs}")


    def get_address(self, lat, lon):
        try:
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.reverse(f"{lat}, {lon}", language='en')
            return location.address if location else None
        except Exception as e:
            print(f"Error fetching address: {e}")
            return None






    # --------------------For Camera purposes --------------------------------------------------------
    def start_camera(self):
        """
        Start the camera and schedule the update function.
        """
        # Open the camera
        self.capture = cv2.VideoCapture(1)  # Use index 0 or 1 depending on the camera

        # Schedule the update function to refresh the frames in the UI
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)  # 30 FPS

    def start_opencv_camera(self):
        """
        Start capturing a live camera feed using OpenCV (for Windows).
        """
        self.capture = cv2.VideoCapture(0)

        if not self.capture.isOpened():
            Logger.error("OpenCV: Cannot access the camera")
            return

        # Schedule the update function to display the camera feed
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)  # 30 frames per second

    def update_frame(self, dt):
        """
        Capture frames from the camera and display them in the Kivy Image widget.
        """
        ret, frame = self.capture.read()

        if ret:
            print(f"Frame captured: {frame.shape}")  # Log the frame size

            # Convert the image frame to Kivy texture
            buffer = cv2.flip(frame, 0).tobytes()  # Flip the frame to avoid upside-down display
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')

            # Update the Image widget with the new texture
            photo_holder = self.screen_manager.get_screen('report').ids.photo_holder
            photo_holder.texture = texture  # Assign the texture to the Image widget
        else:
            print("Failed to capture frame.")  # Add this log to catch camera issues
            Logger.error("OpenCV: Failed to capture frame")

    def capture_photo(self):
        """
        Capture and save a single frame when the user clicks the "Capture Photo" button.
        This function captures the photo, displays it in the app, and stops the camera.
        """
        if self.capture:
            ret, frame = self.capture.read()
            if ret:
                # Save the captured frame as an image file
                image_path = 'captured_photo_opencv.jpg'
                cv2.imwrite(image_path, frame)
                Logger.info(f"Photo saved at {image_path}")

                # Update the Image widget with the captured photo
                buffer = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')

                # Assign the texture to the Image widget
                photo_holder = self.screen_manager.get_screen('report').ids.photo_holder
                photo_holder.texture = texture

                # Stop the camera feed after capturing the photo
                self.stop_camera()
            else:
                Logger.error("Failed to capture frame.")
        else:
            Logger.error("No camera feed available.")

    def update_photo(self, image_path):
        """
        Update the Image widget with the captured photo.
        """
        if image_path and os.path.exists(image_path):
            Logger.info(f"Camera: Image captured and saved to {image_path}")
            # Update the Image widget (photo_holder) with the new image
            self.screen_manager.get_screen('report').ids.photo_holder.source = image_path
        else:
            Logger.error("Camera: No image captured or image path does not exist")

    def stop_camera(self):
        """
        Stop the camera feed and release OpenCV resources without crashing the app.
        """
        if self.capture:
            # Release the camera and stop updating frames
            Clock.unschedule(self.update_frame)
            self.capture.release()
            self.capture = None
            Logger.info("OpenCV: Camera feed stopped.")

            # Optionally, you can clear the texture or show a default image
            photo_holder = self.screen_manager.get_screen('report').ids.photo_holder
            photo_holder.texture = None  # Or set it to a placeholder image
    # --------------------For Camera purposes --------------------------------------------------------


    # Create your custom spinner with dropdown
    def set_accident_type(self, text_item):
        """Set the accident type in the text field."""
        self.screen_manager.get_screen('report').ids.accident_field.text = text_item
        self.menu_accident.dismiss()

    def on_injured_count_selected(self, count):
        # Set the selected count when the user selects from the spinner
        self.selected_count = count
        print(f"Selected injury count: {self.selected_count}")

    def set_persons_status(self, text_item):
        """Set the accident type in the text field."""
        self.screen_manager.get_screen('report').ids.persons_status_field.text = text_item
        self.menu_person_status.dismiss()

    def submit_injured_count(self):
        if hasattr(self, 'selected_count'):
            print(f"Submitting injured count: {self.selected_count}")
        else:
            print("No injured count selected.")

    def switch_to_screen(self, screen_name):
        # Switch the screen
        self.root.current = screen_name

    def update_icon_colors(self):
        current_screen = self.screen_manager.current
        print(f"Current screen: {current_screen}")

        # Reset icon colors for all icons
        home_icon_color = get_color_from_hex('##969592')  # Light Grey for inactive
        if current_screen == 'home':
            home_icon_color = get_color_from_hex('#545452')  # Dark gray for active

        # Update the icon color using the ID
        self.root.get_screen('home').ids.home_icon.md_bg_color = home_icon_color

    def switch_to_screenHome(self, screen_name):
        print(f"Switching to {screen_name}")
        self.screen_manager.current = screen_name  # Make sure 'account-details' is a valid screen name
        self.update_icon_colors()

    def toggle_password_visibilitySignup(self):
        """Toggle the password visibility and the icon."""
        password_field = self.root.get_screen('login').ids.password_field
        icon_button = self.root.get_screen('login').ids.password_toggle

        # Check current state and toggle visibility
        if password_field.password:  # If the password is hidden
            password_field.password = False  # Show the password
            icon_button.icon = "eye"  # Change icon to 'eye' for visible password
        else:
            password_field.password = True  # Hide the password
            icon_button.icon = "eye-off"  # Change icon back to 'eye-off'

    def toggle_password_visibilityAdduser(self):
        """Toggle the password visibility and the icon."""
        password_field = self.root.get_screen('adduser').ids.password_field
        icon_button = self.root.get_screen('adduser').ids.password_toggle

        # Check current state and toggle visibility
        if password_field.password:  # If the password is hidden
            password_field.password = False  # Show the password
            icon_button.icon = "eye"  # Change icon to 'eye' for visible password
        else:
            password_field.password = True  # Hide the password
            icon_button.icon = "eye-off"  # Change icon back to 'eye-off'

    def validate_username(self, username):
        """Validate username when user types."""
        if len(username) < 3:
            self.root.get_screen('login').ids.username_field.error = True
            self.root.get_screen(
                'login').ids.username_field.helper_text = "Username must be at least 3 characters long."
        else:
            self.root.get_screen('login').ids.username_field.error = False
            self.root.get_screen('login').ids.username_field.helper_text = ""

    def validate_password(self, password):
        """Validate password with certain conditions."""
        password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(password_pattern, password):
            self.root.get_screen('login').ids.password_field.error = True
            self.root.get_screen('login').ids.password_field.helper_text = (
                "Password must at least 1 uppercase,lowercase,number, "
                "symbol and minimum of 8 characters."
            )
        else:
            self.root.get_screen('login').ids.password_field.error = False
            self.root.get_screen('login').ids.password_field.helper_text = ""

    def hash_password(self, password):
        """Hash the password using SHA-256 for security."""
        return hashlib.sha256(password.encode()).hexdigest()

    def save_credentials(self, username, password, full_name, email=None, contact_number=None):
        """Save the username, plain password, full name, and other details to a JSON file."""
        user_data = {
            "username": username,
            "full_name": full_name,  # Store the full name
            "plain_password": password,  # Store the plain password
            "hashed_password": self.hash_password(password),  # Still hash it if needed
            "email": email,
            "contact_number": contact_number
        }

        with open("user_data.json", "w") as file:
            json.dump(user_data, file)

        show_message("User credentials saved!")

    def load_credentials(self):
        """Load credentials from the JSON file."""
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r") as file:
                return json.load(file)
        #return None
        return {}
    #===================for account details window=============================

    def toggle_edit_mode(self):
        """Toggle text fields between editable and read-only mode."""
        account_screen = self.screen_manager.get_screen('account-details')
        is_readonly = account_screen.ids.username_field.readonly

        for field_id in ['username_field', 'full_name_field', 'email_field', 'password_field', 'contact_field']:
            account_screen.ids[field_id].readonly = not is_readonly

    def save_user_details(self):
        """Save the edited user details to user_data.json."""
        account_screen = self.screen_manager.get_screen('account-details')

        self.user_data['username'] = account_screen.ids.username_field.text
        self.user_data['full_name'] = account_screen.ids.full_name_field.text
        self.user_data['email'] = account_screen.ids.email_field.text
        self.user_data['plain_password'] = account_screen.ids.password_field.text
        self.user_data['contact_number'] = account_screen.ids.contact_field.text

        with open("user_data.json", "w") as file:
            json.dump(self.user_data, file)

        show_message("User details saved successfully!")

    # ===================for account details window=============================

    def validate_login(self):
        """Validate the login credentials against stored data."""
        username = self.root.get_screen('login').ids.username_field.text
        password = self.root.get_screen('login').ids.password_field.text

        if username == "" or password == "":
            show_message("Username/Password cannot be empty")
            return

        stored_data = self.load_credentials()

        if stored_data:
            # Use either plain or hashed password comparison
            if (username == stored_data["username"] and password == stored_data["plain_password"]) or \
                    (username == stored_data["username"] and self.hash_password(password) == stored_data[
                        "hashed_password"]):
                show_message("Login successful!")

                # Pass the full name to the home screen
                full_name = stored_data["full_name"]
                self.root.get_screen('home').ids.welcome_label.text = f"Welcome, {full_name}!"  # Update label text
                self.screen_manager.current = "home"
            else:
                show_message("Invalid username/password")
        else:
            self.save_credentials(username, password)
            show_message("No credentials found. New User Saved...")
            self.screen_manager.current = "home"

    def validate_email(self, email):
        """Validate email format to ensure it contains '@' and a valid domain suffix."""
        # Regular expression pattern to match email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return True
        return False

    def register_user(self):
        """Handle user registration with additional validations."""
        full_name = self.root.get_screen('adduser').ids.full_name_field.text
        email = self.root.get_screen('adduser').ids.email_field.text
        contact_number = self.root.get_screen('adduser').ids.contact_number_field.text
        new_username = self.root.get_screen('adduser').ids.new_username_field.text
        new_password = self.root.get_screen('adduser').ids.password_field.text

        # Ensure fields are not empty
        if not all([full_name, email, contact_number, new_username, new_password]):
            show_message("All fields must be filled out.")
            return

        # Validate email
        if not self.validate_email(email):
            self.root.get_screen('adduser').ids.email_field.error = True
            self.root.get_screen('adduser').ids.email_field.helper_text = "Invalid email address format."
            return

        # Validate contact number
        self.validate_contact_number(contact_number)  # Call validation function

        if self.root.get_screen('adduser').ids.contact_number_field.error:
            return

        # Validate username
        if len(new_username) < 3:
            show_message("Username must be at least 3 characters long.")
            return

        # Validate password
        password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(password_pattern, new_password):
            show_message(
                "Password must contain 1 uppercase, lowercase, number, symbol, and be at least 8 characters long.")
            return

        # Save new credentials with full name
        self.save_credentials(new_username, new_password, full_name, email, contact_number)
        show_message("Registration successful!...")

        # Populate the username field in the login screen
        self.root.get_screen('login').ids.username_field.text = new_username

        # Switch back to the login screen
        self.screen_manager.current = "login"

    def validate_contact_number(self, contact_number):
        """Validate contact number to ensure it contains only digits and is at least 10 digits long."""
        contact_number_field = self.root.get_screen('adduser').ids.contact_number_field
        if not contact_number.isdigit():
            contact_number_field.error = True
            contact_number_field.helper_text = "Contact number must contain only digits."
        elif len(contact_number) < 10:
            contact_number_field.error = True
            contact_number_field.helper_text = "Contact number must be at least 10 digits long."
        else:
            contact_number_field.error = False
            contact_number_field.helper_text = "Enter your contact number"

    def format_phone_number(self, contact_number):
        """Ensure phone number is in E.164 format (e.g., +60123456789)."""
        if not contact_number.startswith('+'):
            # Assuming the number is Malaysian; add the correct country code
            contact_number = '+60' + contact_number[1:]  # Assuming '60' is the Malaysian country code
        return contact_number

    def send_sms(self, to_phone_number, message):
        """Send an SMS message using Twilio."""
        # Twilio credentials
        account_sid = 'AC0b4f8d11643236f1b586f5cbefaaf0e1'
        auth_token = 'd9f9562373ef34622d2fd8e27a45dd04'
        client = Client(account_sid, auth_token)

        # Format the phone number to E.164
        to_phone_number = self.format_phone_number(to_phone_number)

        # Initialize Twilio client
        client = Client(account_sid, auth_token)

        try:
            message = client.messages.create(
                body=message,
                from_='+15597937204',
                to=to_phone_number
            )
            return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False

    def handle_forgot_password(self):
        """Handle the 'Forgot Password' request."""
        username = self.root.get_screen('login').ids.username_field.text

        stored_data = self.load_credentials()

        if stored_data and username == stored_data["username"]:
            phone_number = stored_data["contact_number"]  # Retrieve the contact number directly
            plain_password = stored_data["plain_password"]  # Retrieve the stored plain password

            message = f"Username: {username}\nPassword: {plain_password}"
            if self.send_sms(phone_number, message):
                show_message("Password sent via SMS")
            else:
                show_message("Failed to send SMS")
        else:
            show_message("Username not found")

    def logout(self):
        """Logout the user and switch to the signup screen."""
        print("Logging out and switching to signup page")
        self.screen_manager.current = "login"  # Switch to the signup page

    def on_start(self):
        #Clock.schedule_once(self.login, 4)
        # Call gps_setup after the app has started
        if platform == 'android' or platform == 'ios':
            self.gps_setup()  # Call the function to setup GPS
        else:
            print("GPS functionality is only available on mobile platforms.")

        """Load user data when the app starts."""
        if not self.user_data:  # If not already loaded, try loading it again
            self.user_data = self.load_credentials() or {}
        print("User data loaded:", self.user_data)


    def login(self, *args):
        print("Switching to login screen")
        self.screen_manager.current = "login"

    def close_app(self):
        self.stop()

    def update_progress_bar(self, dt):
        progress_bar = self.screen_manager.get_screen("pre-splash").ids.progress_bar
        if progress_bar.value >= 100:
            #Clock.schedule_once(lambda *args: setattr(self.screen_manager, 'current', 'login'), 1.5)  # Delay in seconds
            self.screen_manager.current = 'login'
            Clock.unschedule(self.update_progress_bar)
        else:
            progress_bar.value += 2

        """
        if progress_bar.value < 100:
            progress_bar.value += 2  # Increment progress bar value by 1
        else:
            # Stop updating when it reaches 100
            Clock.unschedule(self.update_progress_bar)
        """


if __name__ == "__main__":
    LoginPage().run()
