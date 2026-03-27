# hand.py
from collections import defaultdict
from card import Card, Rank, Suit

class Hand:

    """Constructor takes a list of Card objects representing the player's hand."""

    def __init__(self, cards: list[Card]):
        self.cards = cards

    """Methods for managing the hand and determining valid plays based on the current pile."""
    def add_card(self, card: Card):
        self.cards.append(card)

    def remove_cards(self, cards_to_remove: list[Card]):
        for card in cards_to_remove:
            self.cards.remove(card)

    def group_by_rank(self) -> dict:
        """Groups cards by rank. e.g. {Rank.SIX: [6♣, 6♥], ...}"""
        groups = defaultdict(list)
        for card in self.cards:
            groups[card.rank].append(card)
        return dict(groups)

    def is_joker_type(self, card: Card) -> bool:
        """Returns True if card is a Joker-type burn (Joker, OEJ, King of Hearts)."""
        if card.rank == Rank.JOKER:
            return True
        if card.rank == Rank.JACK and card.suit in (Suit.HEARTS, Suit.SPADES):
            return True
        if card.rank == Rank.KING and card.suit == Suit.HEARTS:
            return True
        return False

    def twos_needed_to_burn(self, pile_size: int) -> int:
        """Returns how many 2s are needed to burn a pile of given size."""
        return max(1, pile_size - 1)

    def get_valid_plays(self, pile: list[Card]) -> list[list[Card]]:
        """
        Returns all valid plays given the current pile.
        Each play is a list of cards.
        If pile is empty, any group is valid.
        """
        valid_plays = []
        groups = self.group_by_rank()

        # Empty pile — anything goes
        if not pile:
            for rank, cards in groups.items():
                for count in range(1, len(cards) + 1):
                    valid_plays.append(cards[:count])
            return valid_plays

        pile_size = len(pile)
        top_card = pile[-1]  # last played card represents current rank
        top_order = top_card.rank.order
        pile_is_burn = top_card.is_burn()

        # Separate hand into joker-types, 2s, and normal cards
        joker_types = [c for c in self.cards if self.is_joker_type(c)]
        twos = [c for c in self.cards if c.rank == Rank.TWO]
        normal_groups = {
            rank: cards for rank, cards in groups.items()
            if rank not in (Rank.TWO, Rank.JOKER)
            and not any(self.is_joker_type(c) for c in cards)
        }

        # --- Normal plays (must match pile size, must be higher rank) ---
        # Cannot play normal cards on top of burn cards
        if not pile_is_burn:
            for rank, cards in normal_groups.items():
                if rank.order > top_order and len(cards) >= pile_size:
                    valid_plays.append(cards[:pile_size])

        # --- Same rank burn (must match pile size exactly) ---
        for rank, cards in normal_groups.items():
            if rank.order == top_order and len(cards) >= pile_size:
                valid_plays.append(cards[:pile_size])  # burn by matching

        # --- 2s burn ---
        needed = self.twos_needed_to_burn(pile_size)
        if len(twos) >= needed:
            valid_plays.append(twos[:needed])

        # --- Joker-type burn (always just 1 card) ---
        if joker_types:
            valid_plays.append([joker_types[0]])

        return valid_plays

    def __repr__(self):
        return f"Hand({sorted(self.cards)})"