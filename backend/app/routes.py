# app/routes.py

from fastapi import APIRouter, HTTPException
import pandas as pd
import os
from .config import *
from .data_processing import *
from .models import *
from .client import fetch_data
from app.services.classification import create_classification_prompt, create_shopping_list_prompt
from app.services.lmModel import generate_gpt3

from app.services.classification import create_classification_prompt
from app.services.lmModel import classify_with_gpt3
from app.services.prompts import fav_and_least_fav_product_type_promotional_text_template, highest_and_lowest_volume_product_type_promotional_text_template
from app.services.lmModel import simple_rag, simple_rag_query
import datetime

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