# main.py
from game import Game
from ai import AI
from deck import Deck

## Methods for 
def get_player_names() -> tuple[list[str], list[str]]:
    """Ask user to set up players and which are AI controlled."""
    print("\n=== PRESIDENT ===")
    num_players = int(input("How many players? "))
    
    names = []
    ai_names = []
    
    for i in range(num_players):
        name = input(f"Enter name for player {i + 1} (or press Enter for 'Player {i+1}'): ").strip()
        if not name:
            name = f"Player {i + 1}"
        names.append(name)
        
        is_ai = input(f"Is {name} AI controlled? (y/n): ").strip().lower()
        if is_ai == 'y':
            ai_names.append(name)
    
    return names, ai_names


def display_pile(pile):
    if not pile:
        print("  Pile: (empty)")
    else:
        print(f"  Pile: {pile} ({len(pile)} card(s))")


def display_hand(player):
    sorted_cards = sorted(player.hand.cards)
    for i, card in enumerate(sorted_cards):
        print(f"    [{i}] {card}")


def human_turn(player, game) -> list | None:
    """Handle a human player's turn. Returns chosen cards or None to pass."""
    print(f"\n--- {player.name}'s turn ---")
    display_pile(game.pile)
    print(f"  Your hand:")
    display_hand(player)

    valid_plays = player.hand.get_valid_plays(game.pile)
    if not valid_plays:
        print("  No valid plays — you must pass.")
        input("  Press Enter to continue...")
        return None

    print("\n  Valid plays:")
    for i, play in enumerate(valid_plays):
        print(f"    [{i}] {play}")
    print(f"    [p] Pass")

    while True:
        choice = input("  Choose a play: ").strip().lower()
        if choice == 'p':
            return None
        try:
            idx = int(choice)
            if 0 <= idx < len(valid_plays):
                return valid_plays[idx]
            else:
                print("  Invalid choice, try again.")
        except ValueError:
            print("  Please enter a number or 'p' to pass.")


def ai_turn(player, game, ai_agents) -> list | None:
    """Handle an AI player's turn."""
    ai = ai_agents[player.name]
    active_count = len(game.active_players())
    cards = ai.choose_play_smart(game.pile, active_count)

    ## Prints the AI's turn and the cards they played
    if cards:
        print(f"\n--- {player.name}'s turn (AI) ---")
        display_pile(game.pile)
        print(f"  {player.name} plays: {cards}")
        input("  Press Enter to continue...")
    else:
        print(f"\n--- {player.name}'s turn (AI) ---")
        print(f"  {player.name} passes.")
        input("  Press Enter to continue...")

    return cards


def run_game():
    player_names, ai_names = get_player_names()
    game = Game(player_names)
    game.setup_round()

    # Build full deck card list for AI tracking
    deck = Deck()
    all_cards = deck.cards

    # Set up AI agents
    ai_agents = {}
    for player in game.players:
        if player.name in ai_names:
            ai_agents[player.name] = AI(player, all_cards)

    print("\n=== Round Start ===")
    for player in game.players:
        print(f"  {player.name}: {len(player.hand.cards)} cards")

    # Main game loop
    while not game.is_round_over():
        current = game.current_player()

        if current.name in ai_agents:
            cards = ai_turn(current, game, ai_agents)
        else:
            cards = human_turn(current, game)

        # Execute play or pass
        if cards:
            result = game.play(current, cards)
            print(f"\n  >> {result}")

            # Notify all AI agents of the play
            for ai in ai_agents.values():
                ai.observe_play(cards)
        else:
            result = game.pass_turn(current)
            print(f"\n  >> {result}")

    # Round over
    print("\n=== Round Over ===")
    print("Final standings:")
    standings = game.get_standings()
    for i, player in enumerate(standings):
        print(f"  {i + 1}. {player.name}")

    # Last remaining player is scum
    remaining = game.active_players()
    if remaining:
        print(f"  {len(game.players)}. {remaining[0].name} (last place)")

    play_again = input("\nPlay again? (y/n): ").strip().lower()
    if play_again == 'y':
        run_game()
    else:
        print("\nThanks for playing!")


if __name__ == "__main__":
    run_game()