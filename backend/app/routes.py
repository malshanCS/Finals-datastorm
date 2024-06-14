# app/routes.py
import json
from fastapi import APIRouter, HTTPException
import pandas as pd
import os
from .config import *
from .data_processing import *
from .models import *
from .client import fetch_data
from .services.classification import create_classification_prompt, create_shopping_list_prompt
from .services.lmModel import generate_gpt3
from langchain.prompts import ChatPromptTemplate

from .services.classification import create_classification_prompt
# from .services.lmModel import classify_with_gpt3
from .services.prompts import fav_and_least_fav_product_type_promotional_text_template, highest_and_lowest_volume_product_type_promotional_text_template
from .services.lmModel import simple_rag, simple_rag_query
import datetime

from .services.lmModel import simple_rag, simple_rag_query
from .services.prompts import *

router = APIRouter()

@router.get("/max_sales_week/{customer_code}")
async def get_data(customer_code: str):
    if not os.path.exists(MAX_SALES_WEEKS_PATH):
        create_full_df()
        create_maximum_sale_week_in_each_month()

    max_sales_weeks = pd.read_csv(MAX_SALES_WEEKS_PATH)
    customer_data = max_sales_weeks[max_sales_weeks['customer_code'] == customer_code]

    if customer_data.empty:
        raise HTTPException(status_code=404, detail="No data found for given customer code")
    
    # Convert the DataFrame to a list of Pydantic models
    max_weeks = [MaxSalesWeekDetail(**row) for index, row in customer_data.iterrows()]

    # return customer_data.to_dict(orient='records')
    return MaxSalesWeekResponse(customer_code=customer_code, max_sales_weeks=max_weeks)


@router.get("/sales/{customer_code}", response_model=CustomerSalesResponse)
async def get_sales_data(customer_code: str):

    if not os.path.exists(TOTAL_SALES_Q_BY_DEPT_ITEM_CAT_PATH):
        agg_df = create_agg_df_department_item_category()
        get_total_sales_quantity_breakdown_by_department_item_category(agg_df)

    breakdown_df = pd.read_csv(TOTAL_SALES_Q_BY_DEPT_ITEM_CAT_PATH)
    breakdown_df.fillna('N/A', inplace=True)
    customer_data = breakdown_df[breakdown_df['customer_code'] == customer_code]
    
    if customer_data.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Convert the DataFrame to a list of Pydantic models
    sales_data = [CustomerSalesDetail(**row) for index, row in customer_data.iterrows()]
    
    return CustomerSalesResponse(customer_code=customer_code, sales_data=sales_data)

@router.get("/item_category/{customer_code}", response_model=CustomerItemCategoryResponse)
async def get_sales_data(customer_code: str):

    if not os.path.exists(TOTAL_SALES_Q_BY_ITEM_CAT_PATH):
        agg_df = create_agg_df_item_category()
        get_total_sales_quantity_breakdown_by_item_category(agg_df)

    breakdown_df = pd.read_csv(TOTAL_SALES_Q_BY_ITEM_CAT_PATH)
    breakdown_df.fillna('N/A', inplace=True)
    customer_data = breakdown_df[breakdown_df['customer_code'] == customer_code]
    
    if customer_data.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Convert the DataFrame to a list of Pydantic models
    item_category = [CustomerItemCategoryDetail(**row) for index, row in customer_data.iterrows()]
    
    return CustomerItemCategoryResponse(customer_code=customer_code, item_category=item_category)

@router.get("/item_name/{customer_code}", response_model=CustomerItemNameResponse)
async def get_sales_data(customer_code: str):

    if not os.path.exists(TOTAL_SALES_Q_BY_ITEM_NAME_PATH):
        agg_df = create_agg_df_item_name()
        get_total_sales_quantity_breakdown_by_item_name(agg_df)

    breakdown_df = pd.read_csv(TOTAL_SALES_Q_BY_ITEM_NAME_PATH)
    breakdown_df.fillna('N/A', inplace=True)
    customer_data = breakdown_df[breakdown_df['customer_code'] == customer_code]
    
    if customer_data.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Convert the DataFrame to a list of Pydantic models
    item_name = [CustomerItemNameDetail(**row) for index, row in customer_data.iterrows()]
    
    return CustomerItemNameResponse(customer_code=customer_code, item_name=item_name)

@router.get("/top_products/{customer_code}", response_model=List[Product])
async def top_products(customer_code: str):
    url = f"{BASE_URL}/item_name/{customer_code}"
    try:
        response_data = await fetch_data(url)

        # Ensuring the data contains the expected key
        if 'item_name' not in response_data.json():
            raise HTTPException(status_code=404, detail="Item data not found in the response")
        # print(response_data)
        top_products_list = get_top_products(response_data.json(), key='item_name')
        return top_products_list
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top_products_category/{customer_code}", response_model=List[Product])
async def top_products_category(customer_code: str):
    url = f"{BASE_URL}/item_category/{customer_code}"
    try:
        response_data = await fetch_data(url)

        # Ensuring the data contains the expected key
        if 'item_category' not in response_data.json():
            raise HTTPException(status_code=404, detail="Item data not found in the response")
        # print(response_data)
        top_category_list = get_top_category(response_data.json(), key='item_category')
        return top_category_list
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top_department/{customer_code}", response_model=List[Product])
async def top_departments(customer_code: str):
    url = f"{BASE_URL}/sales/{customer_code}"
    try:
        response_data = await fetch_data(url)

        # Ensuring the data contains the expected key
        if 'sales_data' not in response_data.json():
            raise HTTPException(status_code=404, detail="Item data not found in the response")
        # print(response_data)
        top_department_list = get_top_department(response_data.json(), key='sales_data')
        return top_department_list
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/classify_promotion/{customer_code}")
async def classify_promotion(customer_code: str):
    print("request received")
    url = f"{BASE_URL}/max_sales_week/{customer_code}"
    

    response = await fetch_data(url)
    print("data fetched")
    print(response)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Customer data not found")
    
    prompt = create_classification_prompt(customer_code, response.json()['max_sales_weeks'])
    print("classifiction prompt")
    print(prompt)
    classification = await generate_gpt3(prompt)
    
    return {"customer_code": customer_code, "response": response}


@router.get("/shopping_list/{customer_code}")
async def generate_shopping_list(customer_code: str):
    top_product_url = f"{BASE_URL}/top_products/{customer_code}"
    top_products_category_url = f"{BASE_URL}/top_products_category/{customer_code}"
    top_departments_url = f"{BASE_URL}/top_department/{customer_code}"

    top_product = await fetch_data(top_product_url)
    top_products_category = await fetch_data(top_products_category_url)
    top_departments = await fetch_data(top_departments_url)


    if top_product.status_code != 200:
        raise HTTPException(status_code=404, detail="Customer data not found")
    
    prompt = create_shopping_list_prompt(customer_code, top_product.json(), top_departments.json(), top_products_category.json())

    print(prompt)

    response = await generate_gpt3(prompt)
    
    return {"customer_code": customer_code, "response": response}

@router.get("/promotion_generation/{customer_code}")
async def generate_promotion(customer_code: str):
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

    template_2 = """You are an Expert in writing promotional text and offer texts personalized for a given user. 
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

    template = ChatPromptTemplate.from_template(template)
    template_2 = ChatPromptTemplate.from_template(template_2)

    result = str(get_customer_info_fav_and_leastfav_info("../database/total_sales_quantity_breakdown_by_department_item_category_df.csv", customer_code))
    customer_info = str(get_customer_info_highV_and_lowV_info("../database/top3_department_item_category.csv", "../database/bottom3_department_item_category.csv", customer_code))

    # vector_store_path = await simple_rag(VECTOR_STORE_PATH, SOURCE_PATH)
    response_01 = await simple_rag_query(VECTOR_STORE_PATH, template, result)
    response_02 = await simple_rag_query(VECTOR_STORE_PATH, template_2, customer_info)

    
    return {"customer_code": customer_code, "response_01": json.loads(response_01), "response_02": json.loads(response_02)}


@router.get("/recommendation_generation/{customer_code}")
async def generate_recommendation(customer_code: str):
    template = """You are an Expert in recommending products personalized for a given user. 
    you are given some information about the product categories of frequently bought products and the percentages of transactions counts happend per each category
    out of all the transactions done by each customer.
    Here are the information of top 3 favourite product categories of the customer:
    {customer_info}: 
    input format for customer_info= "{{Favourite product categories: {{product_type1}},{{product_type2}},{{product_type3}}}}"

    give ATLEAST 5 products relevent to the above favourite product categories of the customer solely based on the following:
    {offer_context}


    Final JSON output format= 
    "{{ product name1:Product Discription1,
    product name2:Product Discription2, 
    product name3:Product Discription3,
    ...}}"

    Example Output=
    "Green Apple: Crisp and tart, green apples are perfect for snacking, baking, or adding a refreshing crunch to salads. Rich in fiber and vitamin C."

    No need opening or ending paragraph, provide the JSON file ONLY.

    """

    template_2 = """You are an Expert in recommending products personalized for a given user. You are provided with the information on
    products that a user bought with it's discription.Your task is to creatively generate some complementary products related to the products in the input
    and output them with a creatively generated product discription.

    here is the information on products bought by user:
    {customer_info}

    input format for product_info = "
    {{
    product name1:product discription1
    product name2:product discription2
    product name3:product discription3}}"

    generate some complementary products for the above provided products and generate product discriptions for those products influenced by the following:
    {offer_context}

    Final JSON output format= 
    "
    product name1:product discription1
    product name2:product discriptio2
    product name3:product discription3
    product name4:product discription4
    product name5:product discription5
    product name6:product discription6
    product name7:product discription7
    "
    the output should not contain any product that was already in the input

    No need opening or ending paragraph, provide the JSON file ONLY.

    """

    template = ChatPromptTemplate.from_template(template)
    template_2 = ChatPromptTemplate.from_template(template_2)

    result = str(get_product_category(customer_code, "/Users/vihidun/Desktop/Finals_Datastorm_5/Finals-datastorm/database/frequet_items.csv"))
    # customer_info = str(get_customer_info_highV_and_lowV_info("../database/top3_department_item_category.csv", "../database/bottom3_department_item_category.csv", customer_code))

    # vector_store_path = await simple_rag(VECTOR_STORE_PATH_RECOMMEND, SOURCE_PATH_RECOMMEND)
    response_01 = await simple_rag_query(VECTOR_STORE_PATH_RECOMMEND, template, result)
    response_02 = await simple_rag_query(VECTOR_STORE_PATH_RECOMMEND, template_2, str(response_01))
  
    
    return {"customer_code": customer_code, "response_01": json.loads(response_01),"response_02": json.loads(response_02)}


