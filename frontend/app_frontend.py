import streamlit as st
import requests
# Function to fetch promotional ads
def fetch_promotions(customer_code):
    url = f"http://localhost:8000/promotion_generation/{customer_code}"  # Adjust the URL based on your actual API
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return "No promotions available"

# Function to fetch product recommendations
def fetch_recommendations(customer_code):
    url = f"http://localhost:8000/recommendation_generation/{customer_code}"  # Adjust accordingly
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return "No recommendations available"
    
def get_shopping_list(customer_id):
    try:
        response = requests.get(f"http://localhost:8000/shopping_list/{customer_id}")
        if response.status_code == 200:
            return response.json()  # Assuming the API returns a JSON response
        else:
            return f"Failed to retrieve shopping list, status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {e}"

# Setup the sidebar
st.sidebar.title("Customer Input")
customer_code = st.sidebar.text_input("Enter Customer Code")
submit_button = st.sidebar.button("Submit")

if submit_button:
    promotions = fetch_promotions(customer_code)
    st.sidebar.write("Promotional Ads")

    favourite_product_type = promotions["response_01"]["Favourite product type"]
    Least_Favourite_product_type = promotions["response_01"]["Least Favourite product type"]
    Highest_volume_product_type = promotions["response_02"]["Highest volume product type"]
    Lowest_volume_product_type = promotions["response_02"]["Lowest volume product type"]

    st.sidebar.info(favourite_product_type)
    st.sidebar.info(Least_Favourite_product_type)
    st.sidebar.success(Highest_volume_product_type)
    st.sidebar.success(Lowest_volume_product_type)

    # Main body setup
    st.markdown("<h1 style='text-align: center; font-size: 60px'>Shopping Assistant</h1>",unsafe_allow_html=True)


    
    recommendations = fetch_recommendations(customer_code)

    st.header("Youe Usual Picks")
    usual_picks=recommendations["response_01"]

    for key,value in usual_picks.items():
        row = str(key)+":"+str(value)
        st.info(row)

    # You may also like section
    st.header("You May Also Like")
    you_may_like = recommendations["response_02"]
    for key,value in you_may_like.items():
        row = str(key)+":"+str(value)
        st.success(row)

    st.header("Here is your recommended shopping list:")
    shopping_list = get_shopping_list(customer_code)

    shopping_list=shopping_list["response"]["product"]
    for value in shopping_list:
        row = str(value)
        st.info(row)
    # For your pickup section
    # st.header("For Your Pickup")
    # pickup_items = ["Item A", "Item B", "Item C"]  # Static or dynamic data
    # for item in pickup_items:
    #     st.write(f"- {item}")
# Session state to track the conversation
# if 'chat_started' not in st.session_state:
#     st.session_state['chat_started'] = False
# if 'customer_id' not in st.session_state:
#     st.session_state['customer_id'] = ''


    # Initialize chatbot interaction
    st.header("Ask Our Shopping Assistant")
    user_input = st.text_input("Hello, would you like to know what I made for your shopping today? Type 'yes' or 'no'")
    if user_input.lower() == 'yes':
        shopping_list = get_shopping_list(customer_code)
        st.write("Here is your shopping list:")
        st.write(shopping_list)
    elif user_input.lower() == 'no':
        st.write("No problem! Feel free to ask me anything else or use the recommendations above.")
