# ai.py
from card import Card, Rank, Suit
from hand import Hand
from player import Player

class AI:
    def __init__(self, player: Player, all_cards: list[Card]):
        self.player = player
        # Track all cards not yet seen (starts as full deck minus player's own hand)
        self.unseen_cards = [
            c for c in all_cards if c not in self.player.hand.cards
        ]

    # -------------------------
    # Card tracking
    # -------------------------

    def observe_play(self, cards: list[Card]):
        """Call this every time any player plays cards, to update unseen tracking."""
        for card in cards:
            if card in self.unseen_cards:
                self.unseen_cards.remove(card)

    def cards_remaining_of_rank(self, rank: Rank) -> int:
        """How many cards of a given rank are still unseen."""
        return sum(1 for c in self.unseen_cards if c.rank == rank)

    def opponent_likely_has(self, rank: Rank) -> bool:
        """Returns True if at least one unseen card of this rank exists."""
        return self.cards_remaining_of_rank(rank) > 0

    # -------------------------
    # Play evaluation
    # -------------------------

    def is_joker_type(self, card: Card) -> bool:
        if card.rank == Rank.JOKER:
            return True
        if card.rank == Rank.JACK and card.suit in (Suit.HEARTS, Suit.SPADES):
            return True
        if card.rank == Rank.KING and card.suit == Suit.HEARTS:
            return True
        return False

    def is_burn_play(self, cards: list[Card], pile: list[Card]) -> bool:
        """Check if this play would result in a burn."""
        if not pile:
            return False

        pile_size = len(pile)
        top_card = pile[-1]

        if any(self.is_joker_type(c) for c in cards):
            return True

        twos = [c for c in cards if c.rank == Rank.TWO]
        if len(twos) >= max(1, pile_size - 1):
            return True

        if all(c.rank == top_card.rank for c in cards) and len(cards) == pile_size:
            return True

        return False

    def score_play(self, cards: list[Card], pile: list[Card]) -> float:
        """
        Score a potential play. Lower score = more preferred (greedy saves big cards).
        Burn plays are scored separately and used only when needed.
        """
        if not cards:
            return float('inf')

        top_card = cards[0]  # all cards same rank so just check first
        rank_order = top_card.rank.order

        # Burns are high cost — save them unless necessary
        if self.is_joker_type(top_card):
            return 1000 + rank_order  # joker types most expensive

        if top_card.rank == Rank.TWO:
            return 900 + rank_order   # 2s also expensive

        if self.is_burn_play(cards, pile):
            return 800 + rank_order   # same-rank burn, slightly cheaper

        # Normal play — prefer lowest rank that beats the pile
        # Slight penalty if opponents likely have the same rank (they can burn us)
        danger_penalty = 0
        if self.opponent_likely_has(top_card.rank):
            danger_penalty = 10  # opponents might burn this back

        return rank_order + danger_penalty

    # -------------------------
    # Decision making
    # -------------------------

    def choose_play(self, pile: list[Card]) -> list[Card] | None:
        """
        Returns the best play given the current pile, or None to pass.
        Greedy strategy:
          - Play the lowest valid non-burn card if possible
          - Only burn if no normal play exists
          - Pass if nothing is playable
        """
        valid_plays = self.player.hand.get_valid_plays(pile)

        if not valid_plays:
            return None  # must pass

        # Separate into normal plays and burn plays
        normal_plays = [
            p for p in valid_plays if not self.is_burn_play(p, pile)
        ]
        burn_plays = [
            p for p in valid_plays if self.is_burn_play(p, pile)
        ]

        # Prefer normal plays — score and pick lowest cost
        if normal_plays:
            return min(normal_plays, key=lambda p: self.score_play(p, pile))

        # No normal play available — use cheapest burn
        if burn_plays:
            return min(burn_plays, key=lambda p: self.score_play(p, pile))

        return None  # pass

    # -------------------------
    # End game awareness
    # -------------------------

    def should_burn_to_clear(self, pile: list[Card], active_count: int) -> bool:
        """
        Returns True if burning now is strategically smart.
        e.g. player has few cards left and wants control of the pile.
        """
        cards_left = len(self.player.hand.cards)
        # If we have 3 or fewer cards and there are 2+ opponents, burning to lead is valuable
        return cards_left <= 3 and active_count >= 2

    def choose_play_smart(self, pile: list[Card], active_count: int) -> list[Card] | None:
        """
        Enhanced version of choose_play that factors in end game awareness.
        Use this instead of choose_play once the game is wired up.
        """
        valid_plays = self.player.hand.get_valid_plays(pile)

        if not valid_plays:
            return None

        normal_plays = [
            p for p in valid_plays if not self.is_burn_play(p, pile)
        ]
        burn_plays = [
            p for p in valid_plays if self.is_burn_play(p, pile)
        ]

        # End game — consider burning early to take control
        if self.should_burn_to_clear(pile, active_count) and burn_plays:
            return min(burn_plays, key=lambda p: self.score_play(p, pile))

        if normal_plays:
            return min(normal_plays, key=lambda p: self.score_play(p, pile))

        if burn_plays:
            return min(burn_plays, key=lambda p: self.score_play(p, pile))

        return None

    def __repr__(self):
        return f"AI({self.player.name}, unseen={len(self.unseen_cards)} cards)"