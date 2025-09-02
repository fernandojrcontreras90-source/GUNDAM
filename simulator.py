
import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Gundam TCG Simulator", layout="wide")

# ------------------------
# Helper functions
# ------------------------
def parse_deck_text(deck_text):
    """
    Parse deck text with lines like:
      Card Name x4
      Or: Card Name
    Returns list of card names (strings), duplicates expanded.
    """
    deck = []
    for line in deck_text.splitlines():
        ln = line.strip()
        if not ln:
            continue
        qty = 1
        name = ln
        # support formats "Name x4" or "4x Name" or "Name (4)"
        if " x" in ln.lower() or "x" in ln.lower() or "(" in ln and ")" in ln:
            # try "Name x4"
            if " x" in ln.lower() or ln.lower().rstrip().endswith(')') == False:
                # attempt to split by ' x' or ' x'
                parts = ln.rsplit("x", 1)
                if len(parts) == 2 and parts[1].strip().isdigit():
                    name = parts[0].strip()
                    qty = int(parts[1].strip())
            # try "(4)"
            if qty == 1 and "(" in ln and ")" in ln:
                try:
                    start = ln.rfind("(")
                    end = ln.rfind(")")
                    maybe = ln[start+1:end]
                    if maybe.isdigit():
                        qty = int(maybe)
                        name = ln[:start].strip()
                except:
                    pass
            # try "4x Name"
            if qty == 1:
                parts = ln.split("x", 1)
                if parts[0].strip().isdigit():
                    qty = int(parts[0].strip())
                    name = parts[1].strip()
        # fallback
        name = name.strip()
        for _ in range(qty):
            deck.append(name)
    return deck

def simulate_game_simple(deck1, deck2):
    """
    Simple simulation:
    - each player 'draws' 5 random cards from their deck (or full deck if smaller)
    - compute a simple strength metric: sum of card name lengths + random small modifier
    - winner based on higher strength
    Returns: winner (1,2 or 0 for draw), drawn_hand1, drawn_hand2
    """
    hand1 = random.sample(deck1, min(5, len(deck1)))
    hand2 = random.sample(deck2, min(5, len(deck2)))
    score1 = sum(len(c) for c in hand1) + random.randint(0,3)
    score2 = sum(len(c) for c in hand2) + random.randint(0,3)
    if score1 > score2:
        return 1, hand1, hand2
    elif score2 > score1:
        return 2, hand1, hand2
    else:
        return 0, hand1, hand2

# ------------------------
# Streamlit UI
# ------------------------
st.title("🤖 Gundam TCG Simulator — Ready-to-Go")

st.markdown("""
Paste your decklists into the boxes below.
- **Player 1**: your deck (one card per line; use `Card Name xQty` for multiples)
- **Opponents**: up to 10 separate boxes (each opponent deck in its own box)
""")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Player 1 (Your Deck)")
    p1_text = st.text_area("Paste Player 1 Deck", height=250, placeholder="Unit-Zaku x4\nUnit-Gundam x4\nUnit-Tallgeese x2")
    p1_deck = parse_deck_text(p1_text) if p1_text.strip() else []

with col_right:
    st.subheader("Opponents (Up to 10)")
    opponent_texts = []
    for i in range(1,11):
        txt = st.text_area(f"Opponent Deck {i}", height=120, key=f"opp_{i}")
        opponent_texts.append(txt)
    # build queue from non-empty boxes
    opponents = []
    for i, txt in enumerate(opponent_texts, start=1):
        if txt and txt.strip():
            opponents.append({
                "name": f"Opponent {i}",
                "deck": parse_deck_text(txt)
            })

st.sidebar.header("Simulation Settings")
sims = st.sidebar.slider("Simulations per opponent", 10, 2000, 200)
show_sample = st.sidebar.checkbox("Show one sample game log (first opponent only)", value=False)

if st.button("Run Simulations"):
    if not p1_deck:
        st.error("Please paste Player 1 deck (left side).")
    elif not opponents:
        st.error("Please paste at least one opponent deck (right side).")
    else:
        overall_results = {}
        # track card stats for Player1
        card_stats = {c: {"played":0, "wins":0, "losses":0} for c in p1_deck}
        for opp in opponents:
            wins_p1 = 0
            wins_p2 = 0
            for _ in range(sims):
                winner, hand1, hand2 = simulate_game_simple(p1_deck, opp["deck"])
                # count appearances
                for c in hand1:
                    card_stats.setdefault(c, {"played":0,"wins":0,"losses":0})
                    card_stats[c]["played"] += 1
                if winner == 1:
                    wins_p1 += 1
                    for c in hand1:
                        card_stats[c]["wins"] += 1
                elif winner == 2:
                    wins_p2 += 1
                    for c in hand1:
                        card_stats[c]["losses"] += 1
                # draws ignored in per-card stats
            overall_results[opp["name"]] = {"p1": wins_p1, "p2": wins_p2}

        # Display results summary chart
        st.subheader("Matchup Results")
        names = list(overall_results.keys())
        p1_wins = [overall_results[n]["p1"] for n in names]
        p2_wins = [overall_results[n]["p2"] for n in names]

        fig, ax = plt.subplots(figsize=(max(6, len(names)*0.6), 4))
        x = range(len(names))
        ax.bar([i-0.2 for i in x], p1_wins, width=0.4, label="Player 1 Wins")
        ax.bar([i+0.2 for i in x], p2_wins, width=0.4, label="Player 2 Wins")
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=30, ha='right')
        ax.set_ylabel("Wins")
        ax.legend()
        st.pyplot(fig)

        # Card Effectiveness Report (Player 1)
        st.subheader("📈 Card Effectiveness Report (Player 1)")
        # Build DataFrame with times played, wins, losses, win_rate_with_card, win_rate_without
        rows = []
        total_games = sum([v["p1"]+v["p2"] for v in overall_results.values()]) or 1
        total_p1_wins = sum([v["p1"] for v in overall_results.values()])
        global_win_rate = total_p1_wins / total_games

        for card, stats in card_stats.items():
            played = stats["played"]
            wins = stats["wins"]
            losses = stats["losses"]
            win_rate_with = wins / played if played>0 else 0
            # estimate win rate without card = (total wins - wins when card present)/(total games - played)
            without_games = total_games - played
            wins_without = total_p1_wins - wins
            win_rate_without = wins_without / without_games if without_games>0 else 0
            rows.append({
                "Card": card,
                "Times Played (in hands)": played,
                "Wins when in hand": wins,
                "Losses when in hand": losses,
                "Win Rate with card": round(win_rate_with*100,1),
                "Win Rate without card": round(win_rate_without*100,1),
                "Delta (with - without)": round((win_rate_with - win_rate_without)*100,1)
            })

        df = pd.DataFrame(rows).sort_values("Delta (with - without)", ascending=False)
        if df.empty:
            st.write("No card stats to show yet (try more simulations).")
        else:
            st.dataframe(df, use_container_width=True)

            # charts: top 10 positive delta and bottom 10 negative delta
            top = df.head(10).set_index("Card")["Delta (with - without)"]
            bottom = df.tail(10).set_index("Card")["Delta (with - without)"]

            fig2, ax2 = plt.subplots(figsize=(8,4))
            top.plot(kind="bar", ax=ax2, color="green")
            ax2.set_title("Top cards (positive impact % points)")
            ax2.set_ylabel("Delta % points")
            st.pyplot(fig2)

            fig3, ax3 = plt.subplots(figsize=(8,4))
            bottom.plot(kind="bar", ax=ax3, color="red")
            ax3.set_title("Bottom cards (negative impact % points)")
            ax3.set_ylabel("Delta % points")
            st.pyplot(fig3)

        # optional sample log
        if show_sample and opponents:
            st.subheader("Sample Game Log (first opponent)")
            winner, hand1, hand2 = simulate_game_simple(p1_deck, opponents[0]["deck"])
            st.write(f"Winner: {'Player 1' if winner==1 else 'Player 2' if winner==2 else 'Draw'}")
            st.write("Player1 hand:", hand1)
            st.write("Player2 hand:", hand2)

        st.success("Simulation batch complete.")
