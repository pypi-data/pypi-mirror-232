import aiohttp

async def name_by_id(
    id:int
):

    url = f"https://users.roblox.com/v1/users/{id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            if response.status == 200:

                data = await response.json()
                return data
            else:
                
                return f"Status: {response.status}"

