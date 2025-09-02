import streamlit as st
from deck_utils import load_deck, validate_deck
from simulation import run_simulation, analyze_deck
import json

# Load rules
with open("rules.json") as f:
    rules = json.load(f)

st.title("🤖 Gundam TCG Simulator")
st.write("Test decks, simulate matches, and get AI suggestions!")

# Player Deck Inputs
st.header("Player Decks")
deck_p1 = st.text_area("Paste Player 1 Deck", height=200)
deck_p2 = st.text_area("Paste Player 2 Deck", height=200)

# Simulation settings
st.header("Simulation Settings")
num_matches = st.slider("Number of Simulations", 10, 1000, 100, step=10)

if st.button("Run Simulation"):
    p1_deck = load_deck(deck_p1, rules)
    p2_deck = load_deck(deck_p2, rules)

    if not validate_deck(p1_deck) or not validate_deck(p2_deck):
        st.error("⚠️ Invalid deck! Check bans or format rules.")
    else:
        results = run_simulation(p1_deck, p2_deck, num_matches)
        st.success(f"✅ Simulation Complete over {num_matches} matches!")

        st.subheader("Results")
        st.write(f"**Player 1 Wins:** {results['p1_wins']} ({results['p1_winrate']}%)")
        st.write(f"**Player 2 Wins:** {results['p2_wins']} ({results['p2_winrate']}%)")

        # AI Deck Suggestions
        st.subheader("📊 AI Suggestions")
        bad, good = analyze_deck(results, p1_deck)

        st.write("**🚫 Cards Hurting Win Rate**")
        for card, pct in bad.items():
            st.write(f"- {card} (reduces win rate by {pct:.1f}%)")

        st.write("**✅ Cards Helping Win Rate**")
        for card, pct in good.items():
            st.write(f"- {card} (boosts win rate by {pct:.1f}%)")
