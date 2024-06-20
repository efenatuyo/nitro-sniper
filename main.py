import src
import json
import asyncio

async def main():
    nitro_sniper = src.nitro_sniper(json.loads(open("config.json", "r").read()))
    await asyncio.gather(*[src.gateaway.client(nitro_sniper, token).connect() for token in nitro_sniper.config["tokens"]["watchers"]])

asyncio.run(main())