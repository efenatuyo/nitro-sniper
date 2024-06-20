import re
from . import claim

class message:
    async def check_message(self, event):
        gift_match = re.search(self.nitro_sniper_obj.gift_pattern, event["d"]["content"])
        if gift_match and gift_match.group(2) not in self.nitro_sniper_obj.already_found_nitro_codes:
            self.nitro_sniper_obj.already_found_nitro_codes.append(gift_match.group(2))
            self.nitro_sniper_obj.logging.debug(f"Matched gift code: {gift_match.group(2)}")
            guild_id, channel_id, author_id = int(event["d"].get("guild_id", 1)), int(event["d"].get("channel_id", 1)), int(event["d"]["author"].get("id", 1))
            if guild_id and channel_id and author_id and guild_id not in self.nitro_sniper_obj.config["black_listed"]["guild_ids"] and channel_id not in self.nitro_sniper_obj.config["black_listed"]["channel_ids"] and author_id not in self.nitro_sniper_obj.config["black_listed"]["user_ids"]:
                await claim.claim(self.nitro_sniper_obj, gift_match.group(2))