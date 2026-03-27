from card import Suit, Rank, Card
from enum import Enum


class Deck:
    def __init__(self, jokers: int = 2):
        self.cards = []
        for suit in Suit:
            if suit == Suit.NONE:
                continue
            for rank in Rank:
                if rank == Rank.JOKER:
                    continue
                self.cards.append(Card(rank, suit))
        for _ in range(jokers):
            self.cards.append(Card(Rank.JOKER, Suit.NONE))

    def shuffle(self):
        import random
        random.shuffle(self.cards)

    def deal(self, num_players: int) -> list[list[Card]]:
        self.shuffle()
        hands = [[] for _ in range(num_players)]
        for i, card in enumerate(self.cards):
            hands[i % num_players].append(card)
        return hands

    def __repr__(self):
        return f"Deck({len(self.cards)} cards)"