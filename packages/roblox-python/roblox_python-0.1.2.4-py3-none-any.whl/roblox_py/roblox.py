import httpx

async def name_by_id(
    id:int
):

    url = f"https://users.roblox.com/v1/users/{id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
        if response.status_code == 200:
            user_data = response.json()
            return user_data
        else:
            print(f"Ошибка при выполнении запроса. Код состояния: {response.status_code}")
            return None