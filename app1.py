from flask import Flask, request, jsonify, render_template
import os
import requests

app = Flask(__name__)

# File to store location data
LOCATION_FILE = r"C:\Users\Salmaan\PycharmProjects\pythonProject2\location.txt"

# Google Maps Geocoding API Key
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your Google API key


@app.route("/")
def index():
    return render_template("index.html")  # Render the HTML frontend


@app.route("/save-location", methods=["POST"])
def save_location():
    data = request.get_json()
    lat = data.get("lat")
    long = data.get("long")
    accuracy = data.get("accuracy")

    # Generate links and embed
    google_maps_short_link = f"https://maps.app.goo.gl/?q={lat},{long}"
    google_maps_embed = (
        f'<iframe src="https://www.google.com/maps/embed/v1/view?key={GOOGLE_API_KEY}&center={lat},{long}&zoom=15" '
        'width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'
    )
    google_maps_standard_link = f"https://www.google.com/maps/@{lat},{long},15z"

    # Reverse geocode the address
    address = get_address_from_lat_long(lat, long)

    # Append location details to the file
    with open(LOCATION_FILE, "a") as file:
        file.write(
            f"Latitude: {lat}, Longitude: {long}, Accuracy: {accuracy} meters\n"
            f"Google Maps Short Link: {google_maps_short_link}\n"
            f"Google Maps Embed: {google_maps_embed}\n"
            f"Google Maps Standard Link: {google_maps_standard_link}\n"
            f"Address: {address}\n\n"
        )

    return jsonify({
        "message": "Location saved successfully!",
        "short_link": google_maps_short_link,
        "embed": google_maps_embed,
        "standard_link": google_maps_standard_link,
        "address": address,
    })


def get_address_from_lat_long(lat, long):
    """Reverse geocode latitude and longitude into a human-readable address using Google Maps API."""
    url = (
        f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{long}&key={GOOGLE_API_KEY}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("results")
        if results:
            return results[0]["formatted_address"]
    return "Unknown Address"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
