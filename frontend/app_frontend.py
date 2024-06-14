import streamlit as st
import requests

json_01 = """{
  "customer_code": "customer_code_310",
  "response_01": {
    "Banana": "Sweet and creamy, bananas are perfect for snacking, baking, or adding to smoothies. Rich in potassium and vitamin B6.",
    "Beetroot": "Rich in color and flavor, beetroot is perfect for salads, roasting, and juicing. Packed with vitamins, minerals, and antioxidants.",
    "Potatoes": "Versatile and hearty, potatoes are great for baking, mashing, frying, and boiling. A staple rich in carbohydrates and vitamins.",
    "Carrot": "Crisp and sweet, carrots are perfect for snacking, salads, soups, and roasting. Rich in beta-carotene, fiber, and vitamins.",
    "Capsicum": "Vibrant and crunchy, capsicum is great for salads, stir-fries, and grilling. High in vitamins A and C, and antioxidants."
  },
  "response_02": {
    "Pumpkin": "Sweet and nutritious, pumpkin is ideal for soups, roasting, and baking. High in vitamins A and C, and fiber.",
    "Cucumber": "Refreshing and hydrating, cucumber is perfect for salads, snacking, and pickling. Low in calories and rich in vitamins.",
    "Green Beans": "Tender and nutritious, green beans are ideal for steaming, stir-fries, and casseroles. High in fiber, vitamins, and minerals.",
    "Single Rule Exercise Book 120p": "Durable and practical, this 120-page single rule exercise book is perfect for note-taking, homework, and journaling.",
    "Ballpoint Pens Blue 6 Pc": "Smooth and reliable, these blue ballpoint pens come in a pack of 6, ideal for everyday writing and note-taking.",
    "Single Rule CR Book 120p": "Sturdy and functional, this 120-page single rule CR book is perfect for classwork, assignments, and notes.",
    "Glue Stick": "Easy to use and mess-free, this glue stick is perfect for arts, crafts, and school projects. Strong adhesive for a secure bond."
  }
}"""

json_01 = """{
  "customer_code": "customer_code_310",
  "response_01": {
    "Favourite product type": "Celebrate your favorites! Get 20% off on the Stationery Bliss Set and enjoy the products you love even more.",
    "Least Favourite product type": "Give the Baby Essentials Pack Another Try! Enjoy a special 25% discount on your next purchase. We're sure you'll love it this time!"
  },
  "response_02": {
    "Highest volume product type": "As a valued customer who consistently purchases homeware and stationery items in bulk, we want to offer you an exclusive discount of 25% on your next bulk purchase. Stock up on your favorite homeware and stationery products like 'Cozy Home Decor Set' and 'Elegant Stationery Set' at a discounted price!",
    "Lowest volume product type": "We've noticed that you haven't been purchasing animal products and seafood frequently. How about giving it another try with a special 25% discount on your next purchase? Try out our premium 'Ocean's Bounty Seafood Platter' or 'Farm Fresh Organic Eggs' and rediscover the delicious flavors!"
  }
}"""
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
    # st.header("For Your Pickup")
    # pickup_items = ["Item A", "Item B", "Item C"]  # Static or dynamic data
    # for item in pickup_items:
    #     st.write(f"- {item}")

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
