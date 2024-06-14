# app/routes.py

from fastapi import APIRouter, HTTPException
import pandas as pd
import os
from .config import *
from .data_processing import *
from .models import *

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