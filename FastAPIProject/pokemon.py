from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/pokemon/{name}")
def get_pokemon(name: str):
    response = requests.get(
        f"https://pokeapi.co/api/v2/pokemon/{name}"
    )

    if response.status_code == 200:
        data = response.json()
        return {
            "name": data["name"],
            "height": data["height"],
            "weight": data["weight"]
        }

    return {"error": "Pokemon not found"}