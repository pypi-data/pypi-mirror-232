import requests

async def name_by_id(
    id:int
):

    response = requests.get(f"https://users.roblox.com/v1/users/{id}")

    return response.json()

