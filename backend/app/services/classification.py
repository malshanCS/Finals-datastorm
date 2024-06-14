def create_classification_prompt(customer_code, max_sales_weeks):
    intro = f"Based on the buying behavior for customer {customer_code}, determine the most suitable promotional period."
    data_summary = "\n".join([
        f"Month {week['month']} Week {week['week_of_month']} had maximum sales totaling {week['total_sales']}."
        for week in max_sales_weeks
    ])
    question = "\nClassify this customer into one of the following categories: Begin-Month Promotion, Mid-Month Promotion, End-Month Promotion, or Timing Promotion (consistent all-month). What is the best category?"
    
    return f"{intro}\n{data_summary}\n{question}"


def create_shopping_list_prompt(customer_code, top_products, top_departments, top_categories):
    intro = f"Create a personalized shopping list for customer {customer_code} who frequently buys the following items and categories:\n\n"

    # Add top products
    top_products_info = "Top Products:\n" + "\n".join([f"- {item['level_1']} ({item['total_sales_quantity_breakdown']} of purchases)" for item in top_products]) + "\n\n"

    # Add top product categories
    top_categories_info = "Top Product Categories:\n" + "\n".join([f"- {cat['level_1']} ({cat['total_sales_quantity_breakdown']} of category purchases)" for cat in top_categories]) + "\n\n"

    # Add top departments
    top_departments_info = "Top Departments:\n" + "\n".join([f"- {dept['level_1']} ({dept['total_sales_quantity_breakdown']} of department purchases)" for dept in top_departments]) + "\n\n"

    # Instruction for the model
    instructions = "Considering these preferences, generate a comprehensive shopping list that includes a variety of items from these top products, categories, and departments."

    # Combine all parts to form the complete prompt
    prompt = intro + top_products_info + top_categories_info + top_departments_info + instructions
    return prompt
