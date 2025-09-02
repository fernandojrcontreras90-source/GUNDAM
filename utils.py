import json

def load_rules(path):
    with open(path, "r") as f:
        return json.load(f)

def load_cards(path):
    with open(path, "r") as f:
        return json.load(f)

def parse_deck(deck_text):
    deck = {}
    for line in deck_text.strip().splitlines():
        parts = line.strip().split(" ", 1)
        if len(parts) == 2:
            qty, card = parts
            try:
                qty = int(qty)
                deck[card] = qty
            except:
                continue
    return deck
