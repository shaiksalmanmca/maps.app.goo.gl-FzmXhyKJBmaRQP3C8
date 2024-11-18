from flask import Flask, request, jsonify, render_template
import psycopg2
import os
from psycopg2 import sql

# Flask app setup
app = Flask(__name__)

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize database table if it doesn't exist
def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id SERIAL PRIMARY KEY,
                latitude DOUBLE PRECISION NOT NULL,
                longitude DOUBLE PRECISION NOT NULL,
                google_maps_link TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        app.logger.info("Database initialized successfully!")
    except Exception as e:
        app.logger.error(f"Error initializing database: {e}")


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

        # Validate input
        if lat is None or long is None or not isinstance(lat, (int, float)) or not isinstance(long, (int, float)):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

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

    except Exception as e:
        app.logger.error(f"Error saving location: {e}")
        return jsonify({"error": "Failed to save location"}), 500


@app.route('/fetch_locations', methods=['GET'])
def fetch_locations():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT * FROM locations')
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Format the results as a JSON response
        result = [
            {"id": row[0], "latitude": row[1], "longitude": row[2], "google_maps_link": row[3], "timestamp": row[4]}
            for row in rows
        ]
        return jsonify(result)

    except Exception as e:
        app.logger.error(f"Error fetching data: {e}")
        return jsonify({"error": "Failed to fetch data"}), 500


if __name__ == '__main__':
    # Initialize the database
    init_db()
    port = int(os.environ.get('PORT', 8080))  # Default to 8080 if not set
    app.run(host='0.0.0.0', port=port)  # Bind to 0.0.0.0 for external access
