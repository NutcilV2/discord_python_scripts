import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import time
load_dotenv()

import mysql.connector
from mysql.connector import Error

from collections import Counter

def rank_words_by_commonality(words):
    # Use Counter to count the frequency of each word
    word_counts = Counter(words)

    # Sort the words based on their frequency, from most common to least common
    ranked_words = word_counts.most_common()

    return ranked_words

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




# ====== SQL CODE ==============

# Database connection parameters
host_name = "localhost"
db_name = "discord_db"
user_name = "discord"
user_password = os.getenv('DISCORD_TOKEN')

# Connect to the database
connection = create_db_connection(host_name, db_name, user_name, user_password)




cursor = connection.cursor()
query = "SELECT Event_Title FROM events"
cursor.execute(query, (formatted_date,))
titles = [row[0] for row in cursor.fetchall()]
cursor.close()

words = []
for item in titles:
    temp_words = items.split(" ")
    for word in temp_words:
        words.append(word)


ranked_words = rank_words_by_commonality(words)
for word, frequency in ranked_words:
    print(f'"{word}": {frequency}')
