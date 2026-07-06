import streamlit as st
import random
import time

# --- MAIN PAGE CONFIG ---
st.set_page_config(layout="wide")
st.title("🎰 Streamlit Multi-Game Casino Hub")

# --- GLOBAL BANKROLL MANAGEMENT ---
# This wallet stays alive no matter which game the user switches to!
if 'chips' not in st.session_state:
    st.session_state.chips = 1000

# --- SIDEBAR NAVIGATION ENGINE ---
st.sidebar.title("🎮 Casino Navigation")
chosen_game = st.sidebar.selectbox("Choose Your Table:", ["🃏 Blackjack", "🎡 Roulette Wheel", "🃏 Poker Room (Coming Soon)"])

st.sidebar.markdown("---")
st.sidebar.header("💰 Your Global Bankroll")
st.sidebar.metric(label="Total Balance", value=f"${st.session_state.chips:,}")

if st.sidebar.button("Emergency Cash Reset ($1,000)"):
    st.session_state.chips = 1000
    st.rerun()

# =====================================================================
# GAME 1: BLACKJACK ENGINE
# =====================================================================
if chosen_game == "🃏 Blackjack":
    st.header("Blackjack Table")
    st.write("Dealer must hit on soft 17. Natural Blackjack pays 3:2.")

    # Localized state isolation
    if 'bj_stage' not in st.session_state: st.session_state.bj_stage = 'betting'
    if 'player_hand' not in st.session_state: st.session_state.player_hand = []
    if 'dealer_hand' not in st.session_state: st.session_state.dealer_hand = []
    if 'deck' not in st.session_state: st.session_state.deck = []
    if 'bj_bet' not in st.session_state: st.session_state.bj_bet = 100
    if 'bj_msg' not in st.session_state: st.session_state.bj_msg = ""

    def get_hand_value(hand):
        value, aces = 0, 0
        for card in hand:
            rank = card[:-1]
            if rank in ['J', 'Q', 'K']: value += 10
            elif rank == 'A': value += 11; aces += 1
            else: value += int(rank)
        while value > 21 and aces > 0:
            value -= 10; aces -= 1
        return value

    def generate_deck():
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        new_deck = [f"{rank}{suit}" for rank in ranks for suit in suits]
        random.shuffle(new_deck)
        return new_deck

    def deal_card(target_hand):
        if len(st.session_state.deck) < 5: st.session_state.deck = generate_deck()
        target_hand.append(st.session_state.deck.pop(0))

    if st.session_state.bj_stage == 'betting':
        max_bet = max(10, st.session_state.chips)
        st.session_state.bj_bet = st.slider("Select Blackjack Bet ($)", 10, int(max_bet), min(100, int(max_bet)), 10)
        
        if st.button("Deal Hand", type="primary"):
            st.session_state.deck = generate_deck()
            st.session_state.player_hand, st.session_state.dealer_hand = [], []
            deal_card(st.session_state.player_hand); deal_card(st.session_state.dealer_hand)
            deal_card(st.session_state.player_hand); deal_card(st.session_state.dealer_hand)
            
            if get_hand_value(st.session_state.player_hand) == 21:
                st.session_state.bj_stage = 'game_over'
                st.session_state.chips += int(st.session_state.bj_bet * 1.5)
                st.session_state.bj_msg = f"🎉 Natural Blackjack! Won ${int(st.session_state.bj_bet * 1.5)}!"
            else:
                st.session_state.bj_stage = 'playing'
            st.rerun()

    else:
        col1, col2 = st.columns(2)
        p_score = get_hand_value(st.session_state.player_hand)
        d_score = get_hand_value(st.session_state.dealer_hand)
        
        with col1:
            st.markdown("### 🧑‍💼 Dealer")
            if st.session_state.bj_stage == 'playing':
                st.markdown(f"<h1>[ 🎴 ,  {st.session_state.dealer_hand[0]} ]</h1>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h1>{', '.join(st.session_state.dealer_hand)}</h1>", unsafe_allow_html=True)
                st.metric("Dealer Final Score", d_score)
        with col2:
            st.markdown("### 🫵 You")
            st.markdown(f"<h1>{', '.join(st.session_state.player_hand)}</h1>", unsafe_allow_html=True)
            st.metric("Your Score", p_score)

        st.markdown("---")

        if st.session_state.bj_stage == 'playing':
            b1, b2, _ = st.columns([1, 1, 4])
            if b1.button("🃏 Hit", use_container_width=True):
                deal_card(st.session_state.player_hand)
                if get_hand_value(st.session_state.player_hand) > 21:
                    st.session_state.bj_stage = 'game_over'
                    st.session_state.chips -= st.session_state.bj_bet
                    st.session_state.bj_msg = f"💥 Busted! Lost ${st.session_state.bj_bet}."
                st.rerun()
            if b2.button("🛑 Stand", use_container_width=True, type="primary"):
                st.session_state.bj_stage = 'dealer_turn'
                st.rerun()

        elif st.session_state.bj_stage == 'dealer_turn':
            if d_score < 17:
                time.sleep(0.8)
                deal_card(st.session_state.dealer_hand)
                st.rerun()
            else:
                if d_score > 21:
                    st.session_state.chips += st.session_state.bj_bet
                    st.session_state.bj_msg = f"🏁 Dealer Busted! You win ${st.session_state.bj_bet}!"
                elif p_score > d_score:
                    st.session_state.chips += st.session_state.bj_bet
                    st.session_state.bj_msg = f"🏆 You Beat the Dealer! Won ${st.session_state.bj_bet}!"
                elif p_score < d_score:
                    st.session_state.chips -= st.session_state.bj_bet
                    st.session_state.bj_msg = f"📉 Dealer wins. Lost ${st.session_state.bj_bet}."
                else:
                    st.session_state.bj_msg = "🤝 Push! It's a tie."
                st.session_state.bj_stage = 'game_over'
                st.rerun()

        elif st.session_state.bj_stage == 'game_over':
            if "Lost" in st.session_state.bj_msg or "Busted" in st.session_state.bj_msg: st.error(st.session_state.bj_msg)
            elif "win" in st.session_state.bj_msg or "Won" in st.session_state.bj_msg: st.success(st.session_state.bj_msg)
            else: st.info(st.session_state.bj_msg)
            
            if st.button("Deal Next Hand", type="primary"):
                st.session_state.bj_stage = 'betting'
                st.rerun()

# =====================================================================
# GAME 2: ROULETTE ENGINE
# =====================================================================
elif chosen_game == "🎡 Roulette Wheel":
    st.header("European Roulette Table")
    st.write("Bet on Red, Black, Even, Odd, or target a specific single Lucky Number for a massive 35:1 payout!")

    # Set up color mappings for European roulette layout
    red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    
    if 'r_bet_type' not in st.session_state: st.session_state.r_bet_type = "Red"
    if 'r_target_num' not in st.session_state: st.session_state.r_target_num = 7
    if 'r_bet_amount' not in st.session_state: st.session_state.r_bet_amount = 100
    if 'r_status' not in st.session_state: st.session_state.r_status = "idle" # idle, spinning, done
    if 'r_result' not in st.session_state: st.session_state.r_result = None

    col_input, col_wheel = st.columns([2, 3])

    with col_input:
        st.subheader("Place Your Outer/Inner Bets")
        bet_choice = st.selectbox("Select Bet Strategy Type:", ["Red (Pays 1:1)", "Black (Pays 1:1)", "Even (Pays 1:1)", "Odd (Pays 1:1)", "Single Number (Pays 35:1)"])
        
        target_number = 0
        if "Single Number" in bet_choice:
            target_number = st.number_input("Pick a Lucky Number (0-36):", min_value=0, max_value=36, value=7, step=1)
            
        max_r_bet = max(10, st.session_state.chips)
        bet_amt = st.slider("Select Roulette Bet Amount ($)", 10, int(max_r_bet), min(100, int(max_r_bet)), 10)

        if st.button("🎰 Spin the Wheel!", type="primary", disabled=(st.session_state.r_status == "spinning")):
            if bet_amt > st.session_state.chips:
                st.error("Insufficent chips!")
            else:
                st.session_state.r_bet_amount = bet_amt
                st.session_state.r_status = "spinning"
                st.session_state.r_result = None
                st.rerun()

    with col_wheel:
        st.subheader("The Wheel Display")
        
        if st.session_state.r_status == "spinning":
            # Pseudo-animation cycle
            with st.spinner("🔮 The croupier releases the ball... Wheel spinning..."):
                time.sleep(1.5) # Simulating spin momentum duration
            
            # Draw random outcome land vector
            landed = random.randint(0, 36)
            st.session_state.r_result = landed
            st.session_state.r_status = "done"
            st.rerun()
            
        if st.session_state.r_status == "done":
            num = st.session_state.r_result
            color = "🟢 GREEN" if num == 0 else ("🔴 RED" if num in red_numbers else "⚫ BLACK")
            is_even = (num != 0) and (num % 2 == 0)
            
            st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{num}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 24px;'>The ball landed on: <b>{color}</b></p>", unsafe_allow_html=True)
            
            # Process bet win matrices
            won = False
            payout = 0
            
            if "Red" in bet_choice and num in red_numbers: won = True; payout = st.session_state.r_bet_amount
            elif "Black" in bet_choice and num not in red_numbers and num != 0: won = True; payout = st.session_state.r_bet_amount
            elif "Even" in bet_choice and is_even: won = True; payout = st.session_state.r_bet_amount
            elif "Odd" in bet_choice and not is_even and num != 0: won = True; payout = st.session_state.r_bet_amount
            elif "Single Number" in bet_choice and num == target_number: won = True; payout = st.session_state.r_bet_amount * 35
            
            st.markdown("---")
            if won:
                st.session_state.chips += payout
                st.success(f"🎉 Winner! You won ${payout:,}!")
            else:
                st.session_state.chips -= st.session_state.r_bet_amount
                st.error(f"📉 House Wins! You lost your ${st.session_state.r_bet_amount} bet.")
                
            if st.button("Clear Table & Re-bet"):
                st.session_state.r_status = "idle"
                st.rerun()
        else:
            st.info("Place a bet and spin to see results!")

# =====================================================================
# GAME 3: POKER MODULE RESERVATION SLOT
# =====================================================================
elif chosen_game == "🃏 Poker Room (Coming Soon)":
    st.header("The Casino Poker Room")
    st.info("Development structural logic is reserved for this block. Next, we can build a traditional 5-Card Video Poker draw engine or a Casino Three-Card Hold'em framework here!")