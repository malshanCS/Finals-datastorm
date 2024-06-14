def create_classification_prompt(customer_code, max_sales_weeks):
    intro = f"Based on the buying behavior for customer {customer_code}, determine the most suitable promotional period."
    data_summary = "\n".join([
        f"Month {week['month']} Week {week['week_of_month']} had sales totaling {week['total_sales']}."
        for week in max_sales_weeks
    ])
    question = "\nClassify this customer into one of the following categories: Begin-Month Promotion, Mid-Month Promotion, End-Month Promotion. What is the best category?"
    
    return f"{intro}\n{data_summary}\n{question}"


def fav_and_least_fav_product_type_promotional_text_template():
    template = """You are an Expert in writing promotional text and offer texts personalized for a given user. 
    you are given some information about the customer and you have to write a promotional text for a product of the favourite product type and a product of the least favourite product type to boost their sales.
    Refer to the offer_context for most common product of each type. Also you can create similar product for a given type. ALWAYS PROVIDE A PRODUCT NAME IN THE PROMOTIONAL TEXT. 
    Here are the information all time favourite product categories of the customer:
    {customer_info}: 
    input format for customer_info= "{{Favourite product type: {{product_type}}, Least Favourite product type: {{product_type}},}}"
    }}"

    Influence by below sample offers for different product categories to create example promotional text based on the product types, be creative and use more words:
    {offer_context}

    based on above information provide the promotional text for the favourite product type and least favourite product type.

    Final JSON output format= 
    "{{Favourite product type: GENERATED PROMOTIONAL TEXT FOR FAVOURITE PRODUCT TYPE,
    Least Favourite product type: GENERATED PROMOTIONAL TEXT FOR LEAST FAVOURITE PRODUCT TYPE,}}"

    No need opening or ending paragraph, provide the JSON file ONLY.

    """    

    return template


def highest_and_lowest_volume_product_type_promotional_text_template():

    template = """You are an Expert in writing promotional text and offer texts personalized for a given user. 
    You are given some information about the customer's transaction history and you have to write a promotional text for a product of the highest volume sales product type and a product of the lowest volume sales product type to boost their sales.
    Refer to the offer_context for the most common product of each type. You can also create similar products for a given type. ALWAYS PROVIDE A PRODUCT NAME IN THE PROMOTIONAL TEXT. 
    Here is the information about the customer's transaction history: EXTREMELY IMPORTANT TO GENERATE PROMOTIONAL TEXT EMPHASIZING THE BULK BEHAVIOR OF THE CUSTOMER
    {customer_info}: 
    input format for customer_info= "{{Highest volume product type: {{product_type}}, Lowest volume product type: {{product_type}},}}"
    }}"

    Influence by the below sample offers for different product categories to create example promotional text based on the product types, be creative and use more words:
    {offer_context}

    Based on the above information, provide the promotional text for the highest volume product type and the lowest volume product type.

    Final JSON output format= 
    "{{Highest volume product type: GENERATED PROMOTIONAL TEXT FOR HIGHEST VOLUME PRODUCT TYPE,
    Lowest volume product type: GENERATED PROMOTIONAL TEXT FOR LOWEST VOLUME PRODUCT TYPE,}}"

    No need for an opening or ending paragraph, provide the JSON file ONLY.
    """

    return template