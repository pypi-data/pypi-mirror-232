import requests

async def name_by_id(
    id:int
):

    url = f"https://users.roblox.com/v1/users/{id}"


    response = requests.get(url)
        
    if response.status_code == 200:
        user_data = response.json()
        return user_data
    else:
        print(f"Ошибка при выполнении запроса. Код состояния: {response.status_code}")
        return None