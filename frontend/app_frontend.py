import streamlit as st
import requests

# Function to fetch promotional ads
def fetch_promotions(customer_code):
    url = f"http://localhost:8000/promotions/{customer_code}"  # Adjust the URL based on your actual API
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return "No promotions available"

# Function to fetch product recommendations
def fetch_recommendations(customer_code):
    url = f"http://localhost:8000/recommendations/{customer_code}"  # Adjust accordingly
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return "No recommendations available"

# Setup the sidebar
st.sidebar.title("Customer Input")
customer_code = st.sidebar.text_input("Enter Customer Code")
submit_button = st.sidebar.button("Submit")

if submit_button:
    promotions = fetch_promotions(customer_code)
    st.sidebar.write("Promotional Ads")
    st.sidebar.write(promotions)

# Main body setup
st.title("Shopping Assistant")

if customer_code:
    # You may also like section
    st.header("You May Also Like")
    recommendations = fetch_recommendations(customer_code)
    if isinstance(recommendations, list):
        for item in recommendations:
            st.write(f"- {item}")
    else:
        st.write(recommendations)

    # For your pickup section
    st.header("For Your Pickup")
    pickup_items = ["Item A", "Item B", "Item C"]  # Static or dynamic data
    for item in pickup_items:
        st.write(f"- {item}")

# Chatbot section
st.header("Ask Our Shopping Assistant")

user_input = st.text_input("Type your question here...")
if st.button("Send"):
    # Assuming you have a chatbot API endpoint ready
    chat_response = requests.post("http://localhost:8000/chatbot", json={"customer_code": customer_code, "message": user_input})
    if chat_response.status_code == 200:
        st.write("Assistant:", chat_response.json()['reply'])
    else:
        st.error("Failed to get response from the assistant.")
