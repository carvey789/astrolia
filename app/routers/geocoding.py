from fastapi import APIRouter
import httpx
from typing import List, Optional

router = APIRouter(prefix="/geocoding", tags=["Geocoding"])

# Using free Nominatim OpenStreetMap API (no API key required)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


@router.get("/search")
async def search_cities(query: str, limit: int = 10) -> List[dict]:
    """
    Search for cities/places by name.
    Returns list of places with name, country, lat, lon.
    """
    if len(query) < 2:
        return []

    async with httpx.AsyncClient() as client:
        response = await client.get(
            NOMINATIM_URL,
            params={
                "q": query,
                "format": "json",
                "limit": limit,
                "addressdetails": 1,
                "featuretype": "city",
            },
            headers={"User-Agent": "HoroscopeApp/1.0"}
        )

        if response.status_code != 200:
            return []

        results = response.json()

        places = []
        for item in results:
            address = item.get("address", {})
            city = address.get("city") or address.get("town") or address.get("village") or item.get("name", "")
            state = address.get("state", "")
            country = address.get("country", "")

            # Build display name
            parts = [p for p in [city, state, country] if p]
            display_name = ", ".join(parts) if parts else item.get("display_name", "")

            places.append({
                "display_name": display_name,
                "city": city,
                "state": state,
                "country": country,
                "latitude": float(item.get("lat", 0)),
                "longitude": float(item.get("lon", 0)),
            })

        return places
