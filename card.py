# card.py
from rank import Rank
from suit import Suit

class Card:

    ## Constructor that creates each card
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    ## Method that returns true or false if the card is a burn card by itself (2s, jokers, one-eyed jacks, king of hearts)
    def is_burn(self) -> bool:
        """Returns True if this card is a burn card by itself."""
        if self.rank == Rank.TWO:
            return True
        if self.rank == Rank.JOKER:
            return True
        if self.rank == Rank.JACK and self.suit in (Suit.HEARTS, Suit.SPADES):
            return True  # One-eyed jacks
        if self.rank == Rank.KING and self.suit == Suit.HEARTS:
            return True
        return False

    ## returns a string representation of the card, e.g. "6♣" or "Joker"
    def __repr__(self):
        if self.rank == Rank.JOKER:
            return "Joker"
        return f"{self.rank.display}{self.suit.value}"

    ## 
    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other):
        return self.rank.order < other.rank.order

    def __hash__(self):
        return hash((self.rank, self.suit))


