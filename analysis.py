import random

def analyze_deck(deck):
    feedback = {}
    for card, qty in deck.items():
        # Assign random "bad card %" suggestion placeholder
        change = random.randint(-10, 20)
        feedback[card] = change
    return feedback
