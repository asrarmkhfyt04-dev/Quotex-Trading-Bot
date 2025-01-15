# bot/app.py

import streamlit as st
import time
from bot.trade_executor import TradeExecutor
import sys
import os

# --- Page Configuration (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    page_title="Quotex Trader Pro",
    page_icon=":chart_with_upwards_trend:",
    layout="centered",
    initial_sidebar_state="auto",
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# --- Custom CSS for a more polished look ---
st.markdown("""
<style>
/* Main background */
.stApp {
    background-color: #f0f2f6; /* Soft background color */
}

/* Title styling */
.title {
    color: #262730;
    font-size: 2.5em;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}

/* Section headers */
.st-bb { /* Streamlit class for headers */
    background-color: #4A90E2;
    color: white;
    padding: 10px;
    border-radius: 5px;
}

/* Input fields */
.stTextInput, .stNumberInput, .stSelectbox {
    background-color: white;
}

/* Button styling */
.stButton>button {
    color: white;
    background-color: #008CBA;
    border-radius: 20px;
    padding: 10px 24px;
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #005f6b;
}

/* Info and error messages */
.st-b8, .st-b7, .st-bc {
    border-radius: 5px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

def main():
    """
    A Streamlit app for a Quotex Trading Bot.
    Features enhanced UI, error handling, and a more professional design.
    """

    st.markdown("<h1 class='title'>Quotex Trader Pro</h1>", unsafe_allow_html=True)

    # --- Credentials Section ---
    with st.expander("Login Credentials", expanded=True):
        username = st.text_input("Email / Username", value="", placeholder="demo@example.com")
        password = st.text_input("Password", value="", type="password")

    # --- Trade Settings Section ---
    with st.expander("Trade Settings", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.selectbox("Asset",
                                    options=["AUD/USD (OTC)", "EUR/USD (OTC)", "GBP/USD (OTC)", "Other"],
                                    index=0)
            if asset_name == "Other":
                asset_name = st.text_input("Enter the full asset name", value="")

        with col2:
            trade_amount = st.number_input("Trade Amount ($)", value=5.0, min_value=1.0, step=1.0)

        direction = st.radio("Trade Direction", options=["UP :arrow_up:", "DOWN :arrow_down:"])

    # --- Trade Execution Section ---
    if st.button("Execute Trade", key="execute_trade"):
        if not username or not password:
            st.error("Credentials required. Please provide your Quotex login details.")
            return

        with st.spinner("Executing trade... Please wait."):
            try:
                executor = TradeExecutor()

                # 2) Login (if necessary)
                # executor.login_to_quotex(username, password)

                st.info(f":mag: Selecting asset: {asset_name}")
                executor.select_asset(asset_name)

                st.info(f":moneybag: Setting trade amount: ${trade_amount}")
                executor.set_investment_amount(trade_amount)

                trade_direction = direction.split(" ")[0]
                st.info(f":rocket: Placing trade {trade_direction}")
                executor.place_trade(trade_direction)

                time.sleep(2)

                st.success(f"Trade executed successfully! :tada: \n\nAsset: {asset_name} | Amount: ${trade_amount} | Direction: {trade_direction}")

            except Exception as e:
                st.error(f"An error occurred: {e}")

    # --- Footer (Optional) ---
    st.markdown("---")
    st.markdown("""
        **Disclaimer:** Trading involves risk. Use this bot at your own discretion.
        \n\n© 2023 Your Name or Company
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()