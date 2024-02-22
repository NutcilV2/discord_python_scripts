import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta

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

def insert_event_data(connection, data):
    cursor = connection.cursor()
    query = """
    INSERT INTO events (Date, Card_Date, Title, Title_Link, Event_Text, Event_Text_Link, Is_Virtual, Price, Tags)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    for event in data:
        cursor.execute(query, (
            event['Date'],
            event.get('Card Date', ''),
            event['Title'],
            event.get('Title Link', ''),
            event.get('Event Text', ''),
            event.get('Event Text Link', ''),
            event.get('Is Virtual', False),
            event.get('Price', 'N/A'),
            event.get('Tags', '')
        ))
    connection.commit()
    cursor.close()

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
        event_info = {'Date': date.strftime('%Y-%m-%d')}

        # Extract event date
        date_element = card.find('div', class_='event_card_date')
        if date_element:
            event_info['Card Date'] = date_element.get_text(strip=True)

        # Extract event title and link
        title_element = card.find('h3', class_='em-card_title')
        if title_element and title_element.a:
            event_info['Title'] = title_element.get_text(strip=True)
            event_info['Title Link'] = title_element.a['href']

        # Extract event text and its link (if available)
        text_element = card.find('p', class_='em-card_event-text')
        if text_element and text_element.a:
            event_info['Event Text'] = text_element.get_text(strip=True)
            event_info['Event Text Link'] = text_element.a['href']
        elif text_element:  # For virtual event detection without a specific link
            event_info['Event Text'] = text_element.get_text(strip=True)

        # Determine if the event is a virtual event
        event_info['Is Virtual'] = 'Virtual Event' in card.get_text()

        # Extract price tag (if available)
        price_element = card.find('span', class_='em-price-tag em-price')
        event_info['Price'] = price_element.get_text(strip=True) if price_element else 'N/A'

        # Extract list of tags
        tags_container = card.find('div', class_='em-list_tags')
        tags = []
        if tags_container:
            span_tags = tags_container.find_all('span', class_='em-card_tag')
            tags.extend([tag.get_text(strip=True) for tag in span_tags])

            a_tags = tags_container.find_all('a', class_='em-card_tag')
            tags.extend([tag.get_text(strip=True) for tag in a_tags])

        event_info['Tags'] = ', '.join(tags)

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
host_name = "local_host"
db_name = "discord_db"
user_name = "discord"
user_password = "Nzk0OTYzODE5MjU2MjE3Njgx.GBs4_i.hizsWPaA_RyysaEhcTaDRmOWJyXwrtBRtYpfPY"

# Connect to the database
connection = create_db_connection(host_name, db_name, user_name, user_password)

# Check if connection was successful
if connection is not None:
    # Iterate over each day, scrape events, and insert into database
    current_date = start_date
    while current_date <= end_date:
        daily_events = scrape_events_for_date(current_date)
        if daily_events:
            insert_event_data(connection, daily_events)
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
