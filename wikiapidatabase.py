import requests
import sqlite3

# Function to delete existing data from the table
'''def delete_existing_data():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM my_table')
    conn.commit()
    conn.close()'''


# Function to fetch detailed information about a specific topic from Wikipedia
def fetch_wikipedia_data(topic):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return (topic, data['title'], data['extract'])
    else:
        return (topic, "No topic found", "No information available")

# Define the main subjects and their subtopics
subjects_with_subtopics = {
    'Physics': ['Classical Mechanics', 'Quantum Mechanics', 'Thermodynamics', 'Electromagnetism'],
    'Chemistry': ['Organic Chemistry', 'Inorganic Chemistry', 'Analytical Chemistry', 'Physical Chemistry'],
    'Biology': ['Genetics', 'Evolution', 'Microbiology', 'Ecology'],
    'Mathematics': ['Algebra', 'Calculus', 'Geometry', 'Statistics']
}

# Connect to SQLite database (will create it if it doesn't exist)
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute(''' CREATE TABLE IF NOT EXISTS my_table (
                   subject TEXT,
                   topic TEXT,
                   info TEXT
                )''')

# Delete existing data from the table
#delete_existing_data()

# Fetch data for each subject and its subtopics and insert into the database
for subject, subtopics in subjects_with_subtopics.items():
    for subtopic in subtopics:
        topic, title, info = fetch_wikipedia_data(subtopic)
        cursor.execute('INSERT INTO my_table (subject, topic, info) VALUES (?, ?, ?)', (subject, title, info))



# Commit changes to the database
conn.commit()

# Close the database connection
conn.close()
print("\nData fetched and inserted successfully!")
