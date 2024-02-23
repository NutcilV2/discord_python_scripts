import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()

import mysql.connector
from mysql.connector import Error

def create_db_connection(host_name, db_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            database=db_name,
            user=user_name,
            password=user_password
        )
        print("MySQL Database connection successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def insert_event_data(connection, data, titles):
    cursor = connection.cursor()
    query = """
    INSERT INTO events (Event_Date, Event_Time, Event_Title, Event_Link, Event_Description, Event_Price, Event_Tags)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for event in data:
        if(event.get('Event_Time', '') not in titles):
            cursor.execute(query, (
                event.get('Event_Date', ''),
                event.get('Event_Time', ''),
                event.get('Event_Title', ''),
                event.get('Event_Link', ''),
                event.get('Event_Description', ''),
                event.get('Event_Price', 'N/A'),
                event.get('Event_Tags', '')
            ))
    connection.commit()
    cursor.close()

def get_events_for_date(connection, event_date):
    cursor = connection.cursor()
    query = "SELECT Event_Title FROM events WHERE Event_Date = %s"
    cursor.execute(query, (event_date,))
    titles = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return titles

def scrape_events_for_date(date):
    # Format the URL with the current date
    url = f'https://events.unf.edu/calendar/day/{date.year}/{date.month}/{date.day}?card_size=small&days=1&event_types%5B%5D=41614676488110&event_types%5B%5D=41614676476843&experience=&order=date'

    # Send a GET request to the website
    response = requests.get(url)

    # Check for successful response
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage for {date}: Status code {response.status_code}")
        return []

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all event cards by their class
    event_cards = soup.find_all('div', class_='em-card')

    # Prepare data list to store all event information for the current date
    event_data = []

    for card in event_cards:
        # Initialize a dictionary to store the info for each event
        event_info = {'Event_Date': date.strftime('%Y-%m-%d')}

        # Extract event date
        date_element = card.find('div', class_='event_card_date')
        if date_element:
            card_date = date_element.get_text(strip=True).split(", ")
            event_info['Event_Time'] = card_date[-1]

        # Extract event title and link
        title_element = card.find('h3', class_='em-card_title')
        if title_element and title_element.a:
            event_info['Event_Title'] = title_element.get_text(strip=True)
            event_info['Event_Link'] = title_element.a['href']

        # Extract event text and its link (if available)
        text_element = card.find('p', class_='em-card_event-text')
        if text_element and text_element.a:
            event_info['Event_Description'] = text_element.get_text(strip=True)
            #event_info['Event Text Link'] = text_element.a['href']
        elif text_element:  # For virtual event detection without a specific link
            event_info['Event_Description'] = text_element.get_text(strip=True)

        # Extract price tag (if available)
        price_element = card.find('span', class_='em-price-tag em-price')
        event_info['Event_Price'] = price_element.get_text(strip=True) if price_element else 'N/A'

        # Extract list of tags
        tags_container = card.find('div', class_='em-list_tags')
        tags = []
        if tags_container:
            span_tags = tags_container.find_all('span', class_='em-card_tag')
            tags.extend([tag.get_text(strip=True) for tag in span_tags])

            a_tags = tags_container.find_all('a', class_='em-card_tag')
            tags.extend([tag.get_text(strip=True) for tag in a_tags])

        event_info['Event_Tags'] = ', '.join(tags)

        # Add the event info to our list for the current date
        event_data.append(event_info)

    return event_data

# Start and end dates for March
start_date = datetime(2024, 2, 22)
end_date = datetime(2024, 3, 1)

current_date = start_date
all_event_data = []


# ====== SQL CODE ==============

# Database connection parameters
host_name = "localhost"
db_name = "discord_db"
user_name = "discord"
user_password = os.getenv('DISCORD_TOKEN')

# Connect to the database
connection = create_db_connection(host_name, db_name, user_name, user_password)

# Check if connection was successful
if connection is not None:
    # Iterate over each day, scrape events, and insert into database
    current_date = start_date
    while current_date <= end_date:
        daily_events = scrape_events_for_date(current_date)
        if daily_events:
            titles = get_events_for_date(connection, current_date)
            insert_event_data(connection, daily_events, titles)
        current_date += timedelta(days=1)

    # Close the database connection
    connection.close()
    print("MySQL connection is closed")
else:
    print("Failed to connect to the database")

# ====== SQL CODE ==============



### Iterate over each day in March
##while current_date <= end_date:
##    daily_events = scrape_events_for_date(current_date)
##    all_event_data.extend(daily_events)
##    current_date += timedelta(days=1)
##
### After collecting all events for March, write them to a CSV file
##with open('events.csv', 'w', newline='', encoding='utf-8') as csvfile:
##    fieldnames = ['Date', 'Card Date', 'Title', 'Title Link', 'Event Text', 'Event Text Link', 'Is Virtual', 'Price', 'Tags']
##    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
##    writer.writeheader()
##    for event in all_event_data:
##        writer.writerow(event)
