from flask import Flask, request, jsonify, render_template
import psycopg2
import os
from psycopg2 import sql

# Flask app setup
app = Flask(__name__)

# Database URL (replace with your actual Render PostgreSQL URL)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://location_db_qqr2_user:NRBgluMV5poG7g6Mw8g7oAWVXRBlPSHq@dpg-cssvoqt2ng1s73apm09g-a.oregon-postgres.render.com/location_db_qqr2"
)

# Initialize database table if it doesn't exist
def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id SERIAL PRIMARY KEY,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                google_maps_link TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully!")
    except Exception as e:
        print("Error initializing database:", e)


@app.route('/')
def home():
    """Serve the frontend HTML."""
    return render_template('index.html')


@app.route('/save_location', methods=['POST'])
def save_location():
    """Save user location to the PostgreSQL database."""
    try:
        data = request.json
        lat = data.get("lat")
        long = data.get("long")

        if lat and long:
            # Construct the Google Maps link
            google_maps_url = f"https://www.google.com/maps/@{lat},{long},15z"

            # Save the location to the database
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(
                '''
                INSERT INTO locations (latitude, longitude, google_maps_link)
                VALUES (%s, %s, %s)
                ''',
                (lat, long, google_maps_url)
            )
            conn.commit()
            cur.close()
            conn.close()

            return jsonify({"message": "Location saved successfully!", "url": google_maps_url})

        return jsonify({"error": "Invalid data"}), 400

    except Exception as e:
        print("Error saving location:", e)
        return jsonify({"error": "Failed to save location"}), 500


@app.route('/fetch_locations', methods=['GET'])
def fetch_locations():
    """Fetch all saved locations from the database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT * FROM locations')
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Format the results as a JSON-friendly response
        result = [
            {"id": row[0], "latitude": row[1], "longitude": row[2], "google_maps_link": row[3], "timestamp": row[4]}
            for row in rows
        ]

        return jsonify(result)

    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({"error": "Failed to fetch data"}), 500


if __name__ == '__main__':
    # Initialize the database
    init_db()
    app.run(debug=True)
