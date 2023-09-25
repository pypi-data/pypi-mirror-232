# imports
from marvin.prompts.library import System, User, ChainOfThought


# systems
class PokerbotSystem(System):
    content: str = """A bot named pokerbot that
assists the user with any poker task."""
