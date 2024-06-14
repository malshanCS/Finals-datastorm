def create_classification_prompt(customer_code, max_sales_weeks):
    intro = f"Based on the buying behavior for customer {customer_code}, determine the most suitable promotional period."
    data_summary = "\n".join([
        f"Month {week['month']} Week {week['week_of_month']} had maximum sales totaling {week['total_sales']}."
        for week in max_sales_weeks
    ])
    question = "\nClassify this customer into one of the following categories: Begin-Month Promotion, Mid-Month Promotion, End-Month Promotion, or Timing Promotion (consistent all-month). What is the best category?"
    
    return f"{intro}\n{data_summary}\n{question}"


def create_shopping_list_prompt(customer_code, top_products, top_departments, top_categories):
    intro = f"You are an Expert in giving personalized shopping list for customer. You are given some information about top buying products, top buying product categories, top buying product departments. Create a personalized shopping list for customer {customer_code} who frequently buys the following items and categories:\n\n"

    # avaliable_product_list = str({'available_product':[
    #     'carrot', 'potatoes', 'pumpkin', 'cucumber', 'green_beans', 'beetroot', 'capsicum', 
    #     'tomatoes', 'banana', 'papaya', 'fuji apple', 'green apple', 'pineapple', 'orange', 
    #     'grapes', 'mango', 'cat food', 'dog treats', 'chicken and liver treats', 'dog leash', 
    #     'slicker brush', 'pet shampoo', 'dog collar', 'cat litter', 'shampoo', 'conditioner', 
    #     'body_wash', 'facial_cleanser', 'soap', 'perfume', 'lip_balm', 'sunscreen', 
    #     'milk carton', 'vanialla ice cream', 'chocolate ice cream', 'butter', 'cheese slices', 
    #     'cheese wedges', 'set yogurt', 'drinking yogurt', 'protein_bars', 'multivitamin_bottle', 
    #     'smoothie_mix_6_packs', 'green_tea_bags_25_pack', 'yoga_mat', 'baby_soap', 'baby_diapers', 
    #     'baby_cream', 'baby_shampoo', 'silicon pacifiers', 'single_rule_exercise_book_120p', 
    #     'a5_sprial_notebook_100p', 'single_rule_cr_book_120p', 'glue_stick', 'highlighter_6_pack', 
    #     'whiteboard_marker_blue', 'stapler_large', 'ballpoint_pens_blue_6_pc', 'pencils_hb_6_pc', 
    #     'drawing_book_small_20pg', 'chicken_breast_slices_500g', 'chicken_sausages_150g', 
    #     'pork_bacon_500g', 'chicken_meatballs_250g', 'beef_meatballs_200g', 'prawns', 
    #     'cuttlefish', 'tuna', 'seer_fish', 'sea crabs']
    # })

    # Add top products
    top_products_info = "Top Products:\n" + "\n".join([f"- {item['level_1']} ({item['total_sales_quantity_breakdown']} of purchases)" for item in top_products]) + "\n\n"

    # Add top product categories
    top_categories_info = "Top Product Categories:\n" + "\n".join([f"- {cat['level_1']} ({cat['total_sales_quantity_breakdown']} of category purchases)" for cat in top_categories]) + "\n\n"

    # Add top departments
    top_departments_info = "Top Departments:\n" + "\n".join([f"- {dept['level_1']} ({dept['total_sales_quantity_breakdown']} of department purchases)" for dept in top_departments]) + "\n\n"

    # Instruction for the model
    instructions = """Considering these preferences, generate a comprehensive shopping list that includes a variety of items from these top products, categories, and departments. 
    Do not generate additional prompts.
    GIVE PRODUCT LIST ONLY BASED ON available product list.
    do not generate any product not in the available product list

    Final JSON output format= {
    "product": [
        "Product 1 Label",
        "Product 2 Label", ...
    ]
    }

    No need opening or ending paragraph, provide the JSON file ONLY."""

    # Combine all parts to form the complete prompt
    prompt = intro + top_products_info + instructions
    return prompt
