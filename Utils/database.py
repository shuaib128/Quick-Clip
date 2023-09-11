import sqlite3
import pickle

# Connect to the SQLite database (will create if not exists)
db_name = "quickClip_capture.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Create the intervals table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS intervals (
    id INTEGER PRIMARY KEY,
    video_file_path TEXT NOT NULL
)
""")
conn.commit()

# Store interval the data
def store_intervals(formatted_intervals):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Serialize the list
    serialized_data = pickle.dumps(formatted_intervals)

    # Store in the database
    cursor.execute("INSERT INTO intervals (data) VALUES (?)", (serialized_data,))
    conn.commit()

# Get the interval data from the DataBase
def get_intervals():
    cursor.execute("SELECT data FROM intervals ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    if row:
        # Deserialize the list
        return pickle.loads(row[0])
    else:
        return []