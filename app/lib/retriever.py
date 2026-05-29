import httpx
import json
from geopy.geocoders import Nominatim

from app.lib.rag import openai_client, ollama_client
from config import OLLAMA_MODEL
import urllib.parse


def interests_to_osm_tags(interests: list[str], source) -> list[tuple[str, str]]:
    """Utilise le LLM pour convertir des intérêts libres en tags OSM valides."""

    prompt = f"""
    Tu es une API de conversion. Réponds UNIQUEMENT par un JSON valide, sans markdown.
    Convertis ces centres d'intérêt en tags OpenStreetMap (clé/valeur) pertinents.
    Format EXACT :
    {{
    "tags": [
        {{"key": "leisure", "value": "park"}},
        {{"key": "tourism", "value": "museum"}}
    ]
    }}

    Centres d'intérêt : {', '.join(interests)}

    Retourne entre 5 et 15 tags OSM réels et pertinents.
    Utilise uniquement des tags OSM qui existent vraiment (leisure, tourism, amenity, sport, natural, shop...).
    """
    raw = ""
    if source == "openai":
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=400
        )

        raw = response.choices[0].message.content
    elif source == "ollama":
        response = ollama_client.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            stream=False,
            format="json",
            options={
                "temperature": 0
            }
        )
        raw = response["response"]
    data = json.loads(raw)
    return [(t["key"], t["value"]) for t in data["tags"]]


def geocode_place(place: str) -> tuple[float, float] | None:
    geolocator = Nominatim(user_agent="dayplanner")
    location = geolocator.geocode(place)
    if location:
        return location.latitude, location.longitude
    return None


def build_overpass_query(lat: float, lon: float, tags: list[tuple], radius_m: int = 15000) -> str:
    union_parts = []
    for key, value in tags:
        union_parts.append(f'node["{key}"="{value}"](around:{radius_m},{lat},{lon});')
        union_parts.append(f'way["{key}"="{value}"](around:{radius_m},{lat},{lon});')
    union = "\n  ".join(union_parts)
    return f"""
    [out:json][timeout:25];
    (
      {union}
    );
    out center 30;
    """


def fetch_real_places(place: str, interests: list[str], source) -> list[dict]:
    coords = geocode_place(place)
    if not coords:
        return []

    lat, lon = coords

    try:
        tags = interests_to_osm_tags(interests, source)
    except Exception:
        tags = [("tourism", "attraction"), ("leisure", "park"), ("amenity", "theatre")]

    query = build_overpass_query(lat, lon, tags)
    encoded_query = urllib.parse.quote(query)
    url = f"https://overpass-api.de/api/interpreter?data={encoded_query}"
    try:

        response = httpx.get(url, timeout=30,
                             headers={
                                 "User-Agent": "DayPlanner/1.0",
                                 "Accept": "application/json"
                             })
        response.raise_for_status()
        elements = response.json().get("elements", [])

        places = []
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name")
            if not name:
                continue
            places.append({
                "name": name,
                "type": tags.get("tourism") or tags.get("leisure") or tags.get("amenity") or "lieu",
                "address": tags.get("addr:street", ""),
                "city": tags.get("addr:city", place),
                "website": tags.get("website", ""),
                "opening_hours": tags.get("opening_hours", ""),
            })

        return places[:25]

    except Exception:
        return []
