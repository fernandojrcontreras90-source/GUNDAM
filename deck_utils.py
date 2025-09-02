import random

def load_deck(deck_str, rules):
    """Convert pasted deck into list and remove banned cards"""
    deck = []
    for line in deck_str.splitlines():
        if not line.strip():
            continue
        try:
            count, card = line.split(" ", 1)
            count = int(count)
            if card.strip() not in rules["banned_cards"]:
                deck.extend([card.strip()] * count)
        except:
            continue
    return deck

def validate_deck(deck):
    """Basic deck validation: must have 50 cards"""
    return len(deck) == 50
