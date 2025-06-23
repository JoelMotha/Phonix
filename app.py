import streamlit as st
import urllib.parse
import pandas as pd

# Example definitions (you should replace with actual logic or imports)
# -------------------------------------------------------------
# Ensure these are defined before the UI loads
# df = pd.read_csv("your_data.csv")  # Make sure df has 'brand', 'model', 'price', and 'reasons_<type>' columns
# types = ['casual', 'photography', 'gaming', 'business', 'student']

def get_recommendations(user_type, budget, top_n=5, preferred_brand=None):
    filtered = df.copy()

    # Filter by budget
    filtered = filtered[filtered['price'] <= budget]

    # Filter by brand if specified
    if preferred_brand and preferred_brand != "Any":
        filtered = filtered[filtered['brand'] == preferred_brand]

    # Sort by some logic - here assumed cheapest first for demo
    filtered = filtered.sort_values(by='price', ascending=False).head(top_n)
    return filtered

# Safe default session values
default_type = st.session_state.get('chat_type', 'casual')
default_budget = st.session_state.get('chat_budget', 30000)

# --- Chatbot-Based Suggestions ---
if st.session_state.get('from_chatbot'):
    st.subheader("🤖 Top 10 Phones Based on Your Description")
    chat_recs = get_recommendations(default_type, default_budget, top_n=10)

    for idx, row in chat_recs.iterrows():
        search_query = urllib.parse.quote(f"{row['brand']} {row['model']} smartphone")
        amazon_url = f"https://www.amazon.in/s?k={search_query}"
        flipkart_url = f"https://www.flipkart.com/search?q={search_query}"
        st.markdown(f"- **{row['brand']} {row['model']}** - ₹{row['price']}")
        st.markdown(f"  🔗 [Amazon]({amazon_url}) | [Flipkart]({flipkart_url})")

    st.info("👉 Based on these results, adjust your preferences below to get your top 5 personalized recommendations.")

# --- Main UI ---
st.subheader("🎯 Customize Your Preference")

user_type = st.selectbox(
    "Select Type of User",
    types,
    index=types.index(default_type)
)

brand_list = ["Any"] + sorted(df['brand'].dropna().unique().tolist())
preferred_brand = st.selectbox("Select Preferred Brand (optional)", brand_list)

budget = st.slider(
    "Select Your Budget (INR)",
    5000, 150000,
    default_budget,
    step=1000
)

# --- Final Top 5 Recommendations ---
st.subheader("📋 Top 5 Recommendations")

final_recs = get_recommendations(user_type, budget, top_n=5, preferred_brand=preferred_brand)

for idx, row in final_recs.iterrows():
    search_query = urllib.parse.quote(f"{row['brand']} {row['model']} smartphone")
    amazon_url = f"https://www.amazon.in/s?k={search_query}"
    flipkart_url = f"https://www.flipkart.com/search?q={search_query}"

    st.markdown(f"### {row['brand']} {row['model']}")
    st.markdown(f"💰 **Price**: ₹{row['price']}")
    
    reason_col = f'reasons_{user_type}'
    if reason_col in row and pd.notna(row[reason_col]):
        st.markdown(f"📌 {row[reason_col]}")
    else:
        st.markdown("*No specific recommendation explanation available.*")
    
    st.markdown(f"🔗 [Buy on Amazon]({amazon_url}) | [Buy on Flipkart]({flipkart_url})")
    st.markdown("---")
