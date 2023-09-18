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
    data BLOB,
    video_file_path TEXT NOT NULL
)
""")

# Create 'cliped' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cliped (
    id INTEGER PRIMARY KEY,
    video_file_path TEXT NOT NULL
)
""")
conn.commit()

# Store interval the data
def store_video_data(formatted_intervals, video_path):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Serialize the list
    serialized_data = pickle.dumps(formatted_intervals)

    # Store in the database
    cursor.execute(
        "INSERT INTO intervals (data, video_file_path) VALUES (?, ?)",
        (serialized_data, video_path)
    )
    conn.commit()
    conn.close()

# Get the interval data from the DataBase
def get_last_video_data():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT " +
        "id, data, video_file_path " +
        "FROM intervals " +
        "ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()

    if row:
        record_id, serialized_data, video_path = row
        intervals = pickle.loads(serialized_data)
        return {
            "id": record_id,
            "intervals": intervals,
            "video_path": video_path
        }
    else:
        return {}
    

# Get all the video data
def get_all_video_data():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, data, video_file_path FROM intervals"
    )
    rows = cursor.fetchall()
    conn.close()

    video_data_list = []

    for row in rows:
        record_id, serialized_data, video_path = row
        intervals = pickle.loads(serialized_data)
        video_data_list.append({
            "id": record_id,
            "intervals": intervals,
            "video_path": video_path
        })

    return video_data_list

# Get video data by id
def get_video_data_by_id(record_id):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Prepare the SELECT query
    cursor.execute(
        "SELECT id, data, video_file_path FROM intervals WHERE id = ?", (record_id,)
    )
    
    # Fetch one row
    row = cursor.fetchone()
    conn.close()
    
    # If row exists, unpack the row and return it as a dictionary
    if row:
        id, serialized_data, video_file_path = row
        intervals = pickle.loads(serialized_data)
        return {
            "id": id,
            "intervals": intervals,
            "video_path": video_file_path
        }
    # If no row is found for the given ID
    else:
        return None
    

def delete_video_by_id(id):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM intervals WHERE id=?", (id,))
    conn.commit()
    conn.close()


"""Cliped video data"""
# Store interval the data
def store_cliped_video_data(video_path):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Store in the database
    cursor.execute(
        "INSERT INTO cliped (video_file_path) VALUES (?)",
        (video_path,)
    )
    conn.commit()
    conn.close()

# Get all cliped video data.
def get_all_cliped_video_data():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, video_file_path FROM cliped"
    )
    rows = cursor.fetchall()
    conn.close()

    video_data_list = []

    for row in rows:
        record_id, video_path = row
        video_data_list.append({
            "id": record_id,
            "video_path": video_path
        })

    return video_data_list

# Delete cliped video
def delete_cliped_video_by_id(id):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cliped WHERE id=?", (id,))
    conn.commit()
    conn.close()