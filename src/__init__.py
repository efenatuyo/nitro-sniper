import logging
from . import gateaway

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger('websockets').setLevel(logging.WARNING)

class nitro_sniper:
    already_found_nitro_codes = []
    
    gift_pattern = r'(discord\.gift|discord\.com\/gifts|discordapp\.com\/gifts)\/(\w{16,25})'
    logging = logging
    
    def __init__(self, config):
        self.config = config
        