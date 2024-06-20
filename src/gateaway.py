import websockets
import json
import time
import asyncio
import re

from . import nitro_types


class client:
    def __init__(self, nitro_sniper_obj, token):
        self.token = token
        self.websocket = None
        self.heartbeat_interval = None
        self.heartbeat_acknowledged = True
        self.nitro_sniper_obj = nitro_sniper_obj
        
    async def lazy_guild_loading(self, guild_id):
        request_payload = {
            'op': 14,
            'd': {
                'guild_id': guild_id,
                "presences": True,
                "typing": True,
                "voiceStates": True,
                "activities": True,
                "emojis": True,
                'roles': True,
                'guildMembers': True,
                'threads': True,
                'integrations': True,
                'webhooks': True,
                'invites': True,
            }
        }
        await self.websocket.send(json.dumps(request_payload))

    async def connect(self):
        async with websockets.connect("wss://gateway.discord.gg/?v=10&encoding=json", max_size=None) as websocket:
            self.websocket = websocket
            await self.identify()
            await self.listen()

    async def identify(self):
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": "linux",
                    "$browser": "disco",
                    "$device": "disco"
                }
            }
        }
        await self.websocket.send(json.dumps(payload))
        self.nitro_sniper_obj.logging.debug("Identified to the gateway")
    
    async def heartbeat(self, interval):
        while True:
            if not self.heartbeat_acknowledged:
                self.nitro_sniper_obj.logging.warning("Heartbeat not acknowledged, attempting to reconnect")
                await self.connect()
                return
            
            self.heartbeat_acknowledged = False
            heartbeat_payload = {
                "op": 1,
                "d": int(time.time() * 1000)
            }
            await self.websocket.send(json.dumps(heartbeat_payload))
            status_payload = {
                "op": 3,
                "d": {
                    "since": int(time.time() * 1000),
                    "activities": [],
                    "status": self.nitro_sniper_obj.config["tokens"]["watchers_status"], 
                    "afk": False
                }
            }
            await self.websocket.send(json.dumps(status_payload))
            await asyncio.sleep(interval / 1000)

    async def listen(self):
        async for message in self.websocket:
            try:
                event = json.loads(message)
                op = event['op']
            
                if op == 10:
                    self.heartbeat_interval = event['d']['heartbeat_interval']
                    asyncio.create_task(self.heartbeat(self.heartbeat_interval))
                    self.nitro_sniper_obj.logging.debug(f"Received HELLO, heartbeat interval: {self.heartbeat_interval} ms")
            
                elif op == 11:
                    self.heartbeat_acknowledged = True
                    self.nitro_sniper_obj.logging.debug("Received heartbeat ACK")

                elif op == 0:
                    event_type = event['t']
                    if event_type == 'GUILD_CREATE':
                        guild_id = event['d']['id']
                        await self.lazy_guild_loading(guild_id)
                        self.nitro_sniper_obj.logging.debug(f"Received GUILD_CREATE for guild ID: {guild_id}")
                    
                    elif event_type == "READY":
                        for guild in event['d']['guilds']:
                            await self.lazy_guild_loading(guild["id"])
                            self.nitro_sniper_obj.logging.debug(f"Received READY for guild ID: {guild['id']}")
                        
                    elif event_type == "MESSAGE_CREATE":
                        await asyncio.create_task(nitro_types.message.check_message(self, event))
            except Exception as e:
                self.nitro_sniper_obj.logging.error(f"- WEBSOCKET - {e}")