def create_classification_prompt(customer_code, max_sales_weeks):
    intro = f"Based on the buying behavior for customer {customer_code}, determine the most suitable promotional period."
    data_summary = "\n".join([
        f"Month {week['month']} Week {week['week_of_month']} had sales totaling {week['total_sales']}."
        for week in max_sales_weeks
    ])
    question = "\nClassify this customer into one of the following categories: Begin-Month Promotion, Mid-Month Promotion, End-Month Promotion. What is the best category?"
    
    return f"{intro}\n{data_summary}\n{question}"

