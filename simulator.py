import streamlit as st
import json
import random
from deck_utils import load_deck, validate_deck

def run_simulation(deck1, deck2, num_games=100):
    """Simulate matches and report win rates. Replace with your actual simulation logic."""
    p1_wins = sum(random.choice([True, False]) for _ in range(num_games))
    p2_wins = num_games - p1_wins
    draws = 0
    return {
        "p1_winrate": p1_wins / num_games * 100,
        "p2_winrate": p2_wins / num_games * 100,
        "draws": draws / num_games * 100
    }

def get_cardnames_from_deck(deck_str):
    """Convert deck list string to a list of card names."""
    deck = []
    for line in deck_str.splitlines():
        if not line.strip():
            continue
        try:
            count, card = line.split(" ", 1)
            count = int(count)
            deck.extend([card.strip()] * count)
        except Exception:
            continue
    return deck

def ai_card_add_suggestions(deck, opp_deck, all_cards, rules, num_trials=20, top_n=3):
    """
    Suggest top N cards to add that maximize win rate.
    For each candidate card not at max copies, swap it in for a random card,
    run a few quick simulations, and report the win rate improvement.
    """
    orig_deck = deck.copy()
    orig_deck_counts = {card: orig_deck.count(card) for card in set(orig_deck)}
    candidate_cards = [
        c['name'] for c in all_cards.values()
        if orig_deck_counts.get(c['name'], 0) < 4 and c['name'] not in rules.get("banned_cards", [])
    ]
    suggestions = []

    # Baseline win rate
    base_result = run_simulation(orig_deck, opp_deck, num_games=num_trials)
    base_rate = base_result["p1_winrate"]

    for candidate in candidate_cards:
        test_deck = orig_deck.copy()
        replaceable = [c for c in test_deck if c != candidate]
        if not replaceable:
            continue
        out_card = random.choice(replaceable)
        test_deck.remove(out_card)
        test_deck.append(candidate)
        res = run_simulation(test_deck, opp_deck, num_games=num_trials)
        suggestions.append((candidate, res["p1_winrate"] - base_rate))

    # Sort by improvement, descending
    suggestions.sort(key=lambda x: x[1], reverse=True)
    return suggestions[:top_n]

# -------- Streamlit UI --------
st.title("Gundam TCG Simulator — Unified Edition")

with open("rules.json") as f:
    rules = json.load(f)
with open("cards.json") as f:
    all_cards = json.load(f)

deck1_str = st.text_area("Player 1 Deck", height=200)
deck2_str = st.text_area("Player 2 Deck", height=200)
num_games = st.slider("Number of Simulations", 10, 500, 100, step=10)

if st.button("Run Simulation!"):
    deck1_list = get_cardnames_from_deck(deck1_str)
    deck2_list = get_cardnames_from_deck(deck2_str)
    if not (validate_deck(deck1_list) and validate_deck(deck2_list)):
        st.error("Both decks must have exactly 50 cards.")
    else:
        res = run_simulation(deck1_list, deck2_list, num_games)
        st.success("Simulation Complete!")
        st.write(f"Player 1 Win Rate: **{res['p1_winrate']:.1f}%**")
        st.write(f"Player 2 Win Rate: **{res['p2_winrate']:.1f}%**")
        st.write(f"Draws: **{res['draws']:.1f}%**")

        # AI Suggestions
        with st.spinner("Analyzing best cards to add..."):
            top_suggest = ai_card_add_suggestions(
                deck1_list,
                deck2_list,
                all_cards,
                rules,
                num_trials=20,
                top_n=3
            )
            st.subheader("AI Suggestions: Cards to Add for Higher Win Rate")
            if not top_suggest:
                st.info("No suggestions available (maybe all cards already in deck or only banned cards left).")
            else:
                for cand, gain in top_suggest:
                    st.write(f"- **{cand}** (Estimated win rate gain: {gain:+.1f}%)")
