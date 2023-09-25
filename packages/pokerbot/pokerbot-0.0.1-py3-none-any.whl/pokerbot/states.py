# imports
from pydantic import BaseModel


# states
class PokerbotState(BaseModel):
    """State of pokerbot.ai"""

    # info about bot
    name: str = "pokerbot"
    creator: str = "dkdc.dev"
    version: str = "infinity"

    # links to open
    self_source_code: str = "https://github.com/dkdc-dev/pokerbot"
