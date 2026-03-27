# game.py
from card import Card, Rank
from deck import Deck
from player import Player

class Game:
    def __init__(self, player_names: list[str], jokers: int = 2):
        self.jokers = jokers
        self.player_names = player_names
        self.players = []
        self.pile = []
        self.played_cards = []      # all cards played this round (for AI tracking)
        self.current_index = 0     # index of whose turn it is
        self.last_player = None    # last player to successfully play
        self.pass_count = 0        # how many consecutive passes
        self.finish_position = 0   # tracks finishing order

    # -------------------------
    # Setup
    # -------------------------

    def setup_round(self):
        """Deal cards and reset round state."""
        deck = Deck(jokers=self.jokers)
        hands = deck.deal(len(self.player_names))
        self.players = [
            Player(name, hand) for name, hand in zip(self.player_names, hands)
        ]
        self.pile = []
        self.played_cards = []
        self.current_index = 0
        self.last_player = None
        self.pass_count = 0
        self.finish_position = 0

    # -------------------------
    # Turn management
    # -------------------------

    def active_players(self) -> list[Player]:
        """Returns players still in the round."""
        return [p for p in self.players if not p.finished]

    def current_player(self) -> Player:
        """Returns the player whose turn it is."""
        active = self.active_players()
        return active[self.current_index % len(active)]

    def advance_turn(self):
        """Move to the next active player."""
        active = self.active_players()
        if len(active) == 0:
            return
        self.current_index = (self.current_index + 1) % len(active)

    # -------------------------
    # Pile logic
    # -------------------------

    def is_burn(self, cards: list[Card]) -> bool:
        """
        Check if the play results in a burn.
        Cases:
          1. Any joker-type card played (Joker, OEJ, KoH)
          2. Correct number of 2s for the pile size
          3. Same rank as top of pile (matching count)
        """
        if not self.pile:
            return False

        pile_size = len(self.pile)
        top_card = self.pile[-1]

        # Case 1 — joker type (always burns, single card)
        joker_types = [c for c in cards if self.players[0].hand.is_joker_type(c)]
        if joker_types:
            return True

        # Case 2 — 2s burn
        twos = [c for c in cards if c.rank == Rank.TWO]
        needed = max(1, pile_size - 1)
        if len(twos) >= needed:
            return True

        # Case 3 — same rank as top card
        if all(c.rank == top_card.rank for c in cards) and len(cards) == pile_size:
            return True

        return False

    def clear_pile(self):
        """Move pile to played_cards log and reset it."""
        self.played_cards.extend(self.pile)
        self.pile = []

    # -------------------------
    # Playing & passing
    # -------------------------

    def play(self, player: Player, cards: list[Card]) -> str:
        """
        Execute a play. Returns a string describing what happened.
        """
        # Validate
        valid_plays = player.hand.get_valid_plays(self.pile)
        if cards not in valid_plays:
            return f"Invalid play by {player.name}."

        # Add to pile
        self.pile.extend(cards)
        player.play_cards(cards)
        self.pass_count = 0

        # Check finish
        if player.finished:
            self.finish_position += 1
            player.finish_position = self.finish_position
            result = f"{player.name} played {cards} and finished in position {self.finish_position}!"
        else:
            result = f"{player.name} played {cards}."

        # Check burn
        if self.is_burn(cards):
            self.clear_pile()
            self.last_player = player
            result += " BURN! Pile cleared."
            # Don't advance — burner goes again
        else:
            self.last_player = player
            self.advance_turn()

        return result

    def pass_turn(self, player: Player) -> str:
        """Player passes their turn."""
        self.pass_count += 1
        active = self.active_players()

        # Everyone else passed — last player leads again
        if self.pass_count >= len(active) - 1:
            self.clear_pile()
            self.pass_count = 0
            # Set turn back to last player who played
            if self.last_player and not self.last_player.finished:
                self.current_index = active.index(self.last_player)
            return f"{player.name} passed. Everyone passed — pile cleared. {self.last_player.name} leads."

        self.advance_turn()
        return f"{player.name} passed."

    # -------------------------
    # Round state checks
    # -------------------------

    def is_round_over(self) -> bool:
        """Round ends when only one player hasn't finished."""
        return len(self.active_players()) <= 1

    def get_standings(self) -> list[Player]:
        """Returns players sorted by finish position."""
        finished = [p for p in self.players if p.finished]
        return sorted(finished, key=lambda p: p.finish_position)

    def __repr__(self):
        return (f"Game(players={self.players}, "
                f"pile={self.pile}, "
                f"turn={self.current_player().name})")