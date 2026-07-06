import streamlit as st
import random
import time

# Set up clean webpage layout
st.set_page_config(layout="wide")
st.title("🃏 Streamlit Blackjack Casino")
st.write("Test your luck against an automated AI dealer. Standard casino rules apply: Dealer hits on soft 17.")

# --- 1. GAME ENGINE STATE MANAGEMENT ---
if 'chips' not in st.session_state:
    st.session_state.chips = 1000
if 'game_stage' not in st.session_state:
    st.session_state.game_stage = 'betting'  # Options: 'betting', 'playing', 'dealer_turn', 'game_over'
if 'player_hand' not in st.session_state:
    st.session_state.player_hand = []
if 'dealer_hand' not in st.session_state:
    st.session_state.dealer_hand = []
if 'deck' not in st.session_state:
    st.session_state.deck = []
if 'current_bet' not in st.session_state:
    st.session_state.current_bet = 100
if 'result_message' not in st.session_state:
    st.session_state.result_message = ""

def get_hand_value(hand):
    value = 0
    aces = 0
    for card in hand:
        rank = card[:-1]
        if rank in ['J', 'Q', 'K']:
            value += 10
        elif rank == 'A':
            value += 11
            aces += 1
        else:
            value += int(rank)
    
    # Dynamically optimize Ace values from 11 down to 1 if the hand busts
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1
    return value

def generate_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    new_deck = [f"{rank}{suit}" for rank in ranks for suit in suits]
    random.shuffle(new_deck)
    return new_deck

def deal_card(target_hand):
    if len(st.session_state.deck) < 5:
        st.session_state.deck = generate_deck()
    card = st.session_state.deck.pop(0)
    target_hand.append(card)

# --- 2. SIDEBAR CASINO CHIPS BANK ---
st.sidebar.header("💰 Player Account")
st.sidebar.metric(label="Your Total Chips", value=f"${st.session_state.chips:,}")

if st.sidebar.button("Reset Bankroll ($1,000)"):
    st.session_state.chips = 1000
    st.session_state.game_stage = 'betting'
    st.rerun()

# --- 3. MAIN GAME INTERFACE ---

# STAGE A: BETTING PLACEMENT
if st.session_state.game_stage == 'betting':
    st.subheader("Place Your Bet to Deal the Cards")
    max_bet = max(10, st.session_state.chips)
    chosen_bet = st.slider("Select Bet Amount ($)", min_value=10, max_value=int(max_bet), value=min(100, int(max_bet)), step=10)
    
    if st.button("Deal Hand", type="primary"):
        if chosen_bet > st.session_state.chips:
            st.error("You don't have enough chips for that bet!")
        else:
            st.session_state.current_bet = chosen_bet
            st.session_state.deck = generate_deck()
            st.session_state.player_hand = []
            st.session_state.dealer_hand = []
            
            # Initial 2-card deal allocation
            deal_card(st.session_state.player_hand)
            deal_card(st.session_state.dealer_hand)
            deal_card(st.session_state.player_hand)
            deal_card(st.session_state.dealer_hand)
            
            # Auto-check for Natural Player Blackjack
            if get_hand_value(st.session_state.player_hand) == 21:
                st.session_state.game_stage = 'game_over'
                st.session_state.chips += int(st.session_state.current_bet * 1.5)
                st.session_state.result_message = f"🎉 Natural Blackjack! You won ${int(st.session_state.current_bet * 1.5)}!"
            else:
                st.session_state.game_stage = 'playing'
            st.rerun()

# STAGE B: ACTIVE PLAYER GAMEPLAY MODE
elif st.session_state.game_stage == 'playing':
    col1, col2 = st.columns(2)
    player_score = get_hand_value(st.session_state.player_hand)
    
    with col1:
        st.markdown("### 🧑‍💼 Dealer's Hand")
        visible_card = st.session_state.dealer_hand[0]
        st.markdown(f"<h1>[ 🎴 ,  {visible_card} ]</h1>", unsafe_allow_html=True)
        st.caption("Dealer Value: Hidden")
            
    with col2:
        st.markdown("### 🫵 Your Hand")
        st.markdown(f"<h1>{', '.join(st.session_state.player_hand)}</h1>", unsafe_allow_html=True)
        st.metric(label="Your Current Score", value=player_score)
        st.caption(f"Active Bet Value: ${st.session_state.current_bet}")

    st.markdown("---")
    btn_col1, btn_col2, _ = st.columns([1, 1, 4])
    
    with btn_col1:
        if st.button("🃏 Hit", use_container_width=True):
            deal_card(st.session_state.player_hand)
            if get_hand_value(st.session_state.player_hand) > 21:
                st.session_state.game_stage = 'game_over'
                st.session_state.chips -= st.session_state.current_bet
                st.session_state.result_message = f"💥 You Busted! Lost ${st.session_state.current_bet}."
            st.rerun()
            
    with btn_col2:
        if st.button("🛑 Stand", use_container_width=True, type="primary"):
            st.session_state.game_stage = 'dealer_turn'
            st.rerun()

# STAGE C: DEALER'S STEP-BY-STEP REVEAL TURN
elif st.session_state.game_stage == 'dealer_turn':
    col1, col2 = st.columns(2)
    player_score = get_hand_value(st.session_state.player_hand)
    dealer_score = get_hand_value(st.session_state.dealer_hand)
    
    with col1:
        st.markdown("### 🧑‍💼 Dealer's Hand")
        st.markdown(f"<h1>{', '.join(st.session_state.dealer_hand)}</h1>", unsafe_allow_html=True)
        st.metric(label="Dealer Score", value=dealer_score)
            
    with col2:
        st.markdown("### 🫵 Your Hand")
        st.markdown(f"<h1>{', '.join(st.session_state.player_hand)}</h1>", unsafe_allow_html=True)
        st.metric(label="Your Final Score", value=player_score)
        st.caption(f"Active Bet Value: ${st.session_state.current_bet}")

    # Sequential card deal loop animation mechanic
    if dealer_score < 17:
        time.sleep(1.0)  # Dramatic 1-second delay before drawing next card
        deal_card(st.session_state.dealer_hand)
        st.rerun()
    else:
        # Evaluate final outcome vectors once dealer hits minimum house requirement limit
        if dealer_score > 21:
            st.session_state.chips += st.session_state.current_bet
            st.session_state.result_message = f"🏁 Dealer Busted! You win ${st.session_state.current_bet}!"
        elif player_score > dealer_score:
            st.session_state.chips += st.session_state.current_bet
            st.session_state.result_message = f"🏆 You Beat the Dealer! Won ${st.session_state.current_bet}!"
        elif player_score < dealer_score:
            st.session_state.chips -= st.session_state.current_bet
            st.session_state.result_message = f"📉 Dealer wins. Lost ${st.session_state.current_bet}."
        else:
            st.session_state.result_message = "🤝 Push! It's a tie, your chips are returned."
            
        st.session_state.game_stage = 'game_over'
        st.rerun()

# STAGE D: RESOLVED ROUND SUMMARY
elif st.session_state.game_stage == 'game_over':
    col1, col2 = st.columns(2)
    player_score = get_hand_value(st.session_state.player_hand)
    dealer_score = get_hand_value(st.session_state.dealer_hand)
    
    with col1:
        st.markdown("### 🧑‍💼 Dealer's Hand")
        st.markdown(f"<h1>{', '.join(st.session_state.dealer_hand)}</h1>", unsafe_allow_html=True)
        st.metric(label="Final Dealer Score", value=dealer_score)
            
    with col2:
        st.markdown("### 🫵 Your Hand")
        st.markdown(f"<h1>{', '.join(st.session_state.player_hand)}</h1>", unsafe_allow_html=True)
        st.metric(label="Your Final Score", value=player_score)

    st.markdown("---")
    
    if "Busted" in st.session_state.result_message or "Lost" in st.session_state.result_message:
        st.error(st.session_state.result_message)
    elif "win" in st.session_state.result_message or "Beat" in st.session_state.result_message or "Blackjack" in st.session_state.result_message:
        st.success(st.session_state.result_message)
    else:
        st.info(st.session_state.result_message)
        
    if st.session_state.chips <= 0:
        st.warning("🚨 You are completely out of chips! Use the sidebar button to get emergency funding.")
    else:
        if st.button("Deal Next Hand", type="primary"):
            st.session_state.game_stage = 'betting'
            st.rerun()