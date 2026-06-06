from database import get_connection
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test route
@app.get("/")
def home():
    return {"message": "Backend is running"}

# Recommendation API
@app.get("/recommend")
def recommend(mood: str, latitude: float, longitude: float):
    
    try:
      conn = get_connection()
      cursor = conn.cursor()

      cursor.execute(
        """
        INSERT INTO searches
        (mood, latitude, longitude)
        VALUES (%s, %s, %s)
        """,
        (mood, latitude, longitude)
      )

      conn.commit()

      cursor.close()
      conn.close()

    except Exception as e:
     print("Database Error:", e)
    # Map mood to place type
    mood_to_amenity = {
        "happy": "cafe",
        "sad": "park",
        "hungry": "restaurant",
        "tired": "cafe",
        "bored": "cinema"
    }

    amenity = mood_to_amenity.get(mood.lower(), "restaurant")

    # Overpass query
    query = f"""
    [out:json];
    node
      ["amenity"="{amenity}"]
      (around:1500,{latitude},{longitude});
    out;
    """

    try:
        response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": query},
        headers={
           "User-Agent": "MoodRecommendationApp/1.0"
        },
        timeout=20
        )

        print("Status Code:", response.status_code)
        print("Response:", response.text[:500])

        # If API failed
        if response.status_code != 200:
            return [
                {
                    "name": "API error",
                    "rating": 0,
                    "distance": "N/A",
                    "open": False
                }
            ]

        # If empty response
        if not response.text.strip():
            return [
                {
                    "name": "No places found nearby",
                    "rating": 0,
                    "distance": "N/A",
                    "open": False
                }
            ]

        data = response.json()

        places = []

        for element in data.get("elements", [])[:5]:
            name = element.get("tags", {}).get("name", "Unknown Place")

            places.append({
                "name": name,
                "rating": 4.0,
                "distance": "Nearby",
                "open": True
            })

        # If no places found
        if not places:
            return [
                {
                    "name": "No nearby places found",
                    "rating": 0,
                    "distance": "N/A",
                    "open": False
                }
            ]

        return places

    except requests.exceptions.Timeout:
        return [
            {
                "name": "Request timed out",
                "rating": 0,
                "distance": "N/A",
                "open": False
            }
        ]

    except Exception as e:
        print("Error:", e)

        return [
            {
                "name": "Failed to fetch data",
                "rating": 0,
                "distance": "N/A",
                "open": False
            }
        ]
@app.get("/history")
def history():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM searches ORDER BY searched_at DESC"
    )

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results