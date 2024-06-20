import aiohttp

async def claim(self, code):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://discord.com/api/v8/entitlements/gift-codes/{code}/redeem", headers={"Authorization": self.config["tokens"]["claim"]}) as response:
            if response.status == 200:
                self.logging.info(f"Successfully claimed nitro code: {code}")
                if self.config["notify"]["success"]:
                    await send_webhook(self, session, f"Successfully claimed nitro code: discord.gift/{code}")
            else:
                self.logging.info(f"Invalid nitro code: {code}")
                if self.config["notify"]["failed"]:
                    
                    await send_webhook(self, session, f"Invalid nitro code: discord.gift/{code}")

async def send_webhook(self, session, message):
    await session.post(self.config["notify"]["webhook"], json={"content": message})