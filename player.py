# player.py
from hand import Hand
from card import Card

class Player:
    def __init__(self, name: str, cards: list[Card]):
        self.name = name
        self.hand = Hand(cards)
        self.finished = False
        self.finish_position = None  # will matter when we add roles later

    def play_cards(self, cards: list[Card]):
        """Remove played cards from hand, mark finished if empty."""
        self.hand.remove_cards(cards)
        if len(self.hand.cards) == 0:
            self.finished = True

    def has_valid_play(self, pile: list[Card]) -> bool:
        """Returns True if the player has at least one valid play."""
        return len(self.hand.get_valid_plays(pile)) > 0

    def __repr__(self):
        return f"Player({self.name}, {len(self.hand.cards)} cards)"