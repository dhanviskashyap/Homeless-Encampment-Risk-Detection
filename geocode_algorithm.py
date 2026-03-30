import requests
import pandas as pd
import math

ENCAMPMENT_DATA_PATH = "encampments.csv"
RADIUS_KM = 1.0
THRESHOLDS = (0, 2, 5)  

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def geocode_address(address, api_key):
    """Use Google Geocoding API to get lat/lon for an address."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if data["status"] != "OK" or not data["results"]:
        raise ValueError(f"Geocoding failed: {data.get('status')}")
    loc = data["results"][0]["geometry"]["location"]
    return loc["lat"], loc["lng"]

def load_encampments(csv_path):
    """Load encampment data (only active)."""
    df = pd.read_csv(csv_path)
    if "status" in df.columns:
        df = df[df["status"].str.lower() == "active"]
    return df[["latitude", "longitude"]].to_dict(orient="records")

def count_nearby_encampments(lat, lon, encampments, radius_km=1.0):
    return sum(
        1
        for e in encampments
        if haversine_distance(lat, lon, e["latitude"], e["longitude"]) <= radius_km
    )

def risk_scale(count, thresholds):
    low_th, med_th, high_th = thresholds
    if count <= low_th:
        return "Low"
    elif count <= med_th:
        return "Medium"
    else:
        return "High"

def assess_risk(address):
    lat, lon = geocode_address(address, GOOGLE_API_KEY)
    encampments = load_encampments(ENCAMPMENT_DATA_PATH)
    count = count_nearby_encampments(lat, lon, encampments, RADIUS_KM)
    risk = risk_scale(count, THRESHOLDS)

    print(f"📍 Address: {address}")
    print(f" Coordinates: ({lat:.5f}, {lon:.5f})")
    print(f"Encampments within {RADIUS_KM} km: {count}")
    print(f"Risk Level: {risk}")

    return {"address": address, "lat": lat, "lon": lon, "count": count, "risk": risk}


if __name__ == "__main__":
    business_address = input("Enter business address: ")
    result = assess_risk(business_address)
