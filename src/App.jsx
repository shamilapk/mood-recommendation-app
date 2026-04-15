import { useState } from "react";

function App() {
  const [mood, setMood] = useState("");
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [minRating, setMinRating] = useState(0);
  const [maxDistance, setMaxDistance] = useState(10);
  const [openNow, setOpenNow] = useState(false);

  // LOCATION STATES

  const [latitude, setLatitude] = useState(null);
  const [longitude, setLongitude] = useState(null);
  const [locationError, setLocationError] = useState("");

  // GET LOCATION FUNCTION

  const getLocation = () => {
    if (!navigator.geolocation) {
      setLocationError("Geolocation is not supported");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLatitude(position.coords.latitude);
        setLongitude(position.coords.longitude);
        setLocationError("");
      },

      () => {
        setLocationError("Permission denied");
      },
    );
  };

  const handleSearch = async () => {
    setError("");
    setLoading(true);
    setPlaces([]);

    if (!mood) {
      setError("Please enter a mood");
      setLoading(false);
      return;
    }

    if (!latitude || !longitude) {
      setError("Please get your location first");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/recommend?mood=${mood}&latitude=${latitude}&longitude=${longitude}`,
      );

      const data = await response.json();

      setPlaces(data);
    } catch (error) {
      setError("Failed to fetch data");
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Mood-Based Recommendation App</h1>
      <button onClick={getLocation}>Get My Location</button>
      <br />
      <br />
      {latitude && (
        <p>
          Latitude: {latitude}
          <br />
          Longitude: {longitude}
        </p>
      )}
      {locationError && <p>{locationError}</p>}
      <input
        type="text"
        placeholder="Enter your mood"
        value={mood}
        onChange={(e) => setMood(e.target.value)}
      />
      <br />
      <br />

      <br />
      <button onClick={handleSearch}>Find Places</button>
      <h2>Recommended Places</h2>
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      <ul>
        {places.map((place, index) => (
          <li key={index}>
            <strong>{place.name}</strong>
            <br />
            Rating: {place.rating}
            <br />
            Distance: {place.distance} km
            <br />
            Open: {place.open ? "Yes" : "No"}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
