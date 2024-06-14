import streamlit as st
import requests

def get_shopping_list(customer_id):
    try:
        response = requests.get(f"http://localhost:8000/shopping_list/{customer_id}")
        if response.status_code == 200:
            return response.json()  # Assuming the API returns a JSON response
        else:
            return f"Failed to retrieve shopping list, status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {e}"

# Streamlit interface
st.title("Customer Shopping Assistant")

# Session state to track the conversation
if 'chat_started' not in st.session_state:
    st.session_state['chat_started'] = False
    
if 'customer_id' not in st.session_state:
    st.session_state['customer_id'] = ''

# Input for customer ID
if not st.session_state.chat_started:
    customer_id = st.text_input("Enter your customer ID to start:")
    if st.button("Start Conversation"):
        if customer_id:
            st.session_state.customer_id = customer_id
            st.session_state.chat_started = True
            st.write(f"Hello {customer_id}, do you want to know what I made for you for shopping today?")
        else:
            st.error("Please enter a valid customer ID.")

# Handle user responses
if st.session_state.chat_started:
    response = st.text_input("Type 'yes' to see your shopping list or 'no' to exit.")
    if response.lower() == 'yes':
        shopping_list = get_shopping_list(st.session_state.customer_id)
        st.write("Here is your shopping list:")
        st.write(shopping_list)
    elif response.lower() == 'no':
        st.write("Thank you! Have a great day.")
        st.session_state.chat_started = False
