from django.shortcuts import render
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from dotenv import load_dotenv
import requests
load_dotenv()

game_name=''
# Create your views here.
@csrf_exempt
def get_gpt_recommendation(request):
    client = OpenAI(
        api_key=os.environ.get(
            "OPENAI_API_KEY"
        ),  # This is the default and can be omitted
    )
    if request.method == "POST":
        data = json.loads(request.body)
        user_input = data.get("input", "")

        if not user_input:
            return JsonResponse({"error": "No input provided"}, status=400)

        try:
            # Call OpenAI API using the new structure for completions
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # You can choose the appropriate model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": f"Suggest a video game based on what this user here wants: {user_input}. And try to make the game you reccomend usually be critically aclaimed or famous at least unless whatever the user said negates that and when in doubt chose the higher rated game and format it like this exactly and don't say anything else:\n game-name: whatever you recommend",
                    },
                ],
                max_tokens=100,
            )

            # Extract the recommendation
            recommendation = response.choices[0].message.content
            game_name = recommendation.split("game-name:")[-1].strip()
            print(f"This is what we are feeding to rawg: {game_name}")
            # Log what GPT replied with (for debugging)
            # print(f"This is what GPT replied with: {recommendation}")

            return JsonResponse({"recommendation": recommendation})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# Function 2: Fetch game details from RAWG
@csrf_exempt
def fetch_game_details(request):
    if request.method == "POST":
        game_name = "The Witcher 3: Wild Hunt"  # Example game name
        try:
            # Fetch details from RAWG API
            rawg_api_key = os.environ.get("RAWG_API_KEY")
            url = f"https://api.rawg.io/api/games?search={game_name}&key={rawg_api_key}&search_exact=True&exclude_additions=True&page_size=1&exclude_collection=True"
            response = requests.get(url)

            if response.status_code == 200:
                game_data = response.json()

                # Extract relevant details
                if game_data.get("results"):
                    game = game_data["results"][
                        0
                    ]  # Assuming only one result is returned

                    game_details = {
                        "name": game.get("name", "N/A"),
                        "description": game.get(
                            "description_raw", "No description available"
                        ),
                        "rating": game.get("rating", "N/A"),
                        "image": game.get("background_image", ""),
                        "stores": [
                            store["store"]["name"] for store in game.get("stores", [])
                        ],
                    }

                    return JsonResponse({"game_data": game_details})
                else:
                    return JsonResponse(
                        {"error": "No game found with that name"}, status=404
                    )
            else:
                return JsonResponse(
                    {"error": "Failed to fetch game details"},
                    status=response.status_code,
                )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
