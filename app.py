from flask import Flask, request, render_template, jsonify
import psycopg2
import os

app = Flask(__name__)

# Initialize Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")

def initialize_db():
    """Set up the database schema."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        # SQL query to create the table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id SERIAL PRIMARY KEY,
                latitude VARCHAR(50),
                longitude VARCHAR(50),
                google_maps_url TEXT
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print("Error initializing database:", e)

initialize_db()

# Serve the HTML Page
@app.route('/')
def home():
    return render_template('index.html')

# Save Location to Database
@app.route('/save_location', methods=['POST'])
def save_location():
    data = request.json
    lat = data.get("lat")
    long = data.get("long")

    if lat and long:
        google_maps_url = f"https://www.google.com/maps/@{lat},{long},15z"
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO locations (latitude, longitude, google_maps_url)
                VALUES (%s, %s, %s)
            ''', (lat, long, google_maps_url))
            conn.commit()
            cur.close()
            conn.close()

            return jsonify({"message": "Location saved successfully!", "url": google_maps_url})
        except Exception as e:
            print("Error saving to database:", e)
            return jsonify({"error": "Failed to save location"}), 500

    return jsonify({"error": "Invalid data"}), 400

if __name__ == '__main__':
    app.run(debug=True)
