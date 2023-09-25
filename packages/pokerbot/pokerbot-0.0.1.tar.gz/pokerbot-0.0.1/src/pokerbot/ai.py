# imports
from pokerbot import AI

from pokerbot.tools import tools
from pokerbot.states import PokerbotState
from pokerbot.systems import (
    PokerbotSystem,
)

# variables
state = PokerbotState()
prompts = []
description = PokerbotSystem().content


# create bot
bot = AI(
    name=state.name, description=description, tools=tools, prompts=prompts, state=state
)
