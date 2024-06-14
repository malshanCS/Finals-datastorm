# app/models.py

from pydantic import BaseModel, Field
from typing import Dict, List

class CustomerSalesDetail(BaseModel):
    level_1: str
    total_sales_quantity_breakdown: str

class CustomerSalesResponse(BaseModel):
    customer_code: str
    sales_data: List[CustomerSalesDetail]



class MaxSalesWeekDetail(BaseModel):
    month: int
    week_of_month: int
    total_sales: float

class MaxSalesWeekResponse(BaseModel):
    customer_code: str
    max_sales_weeks: List[MaxSalesWeekDetail]



class CustomerItemCategoryDetail(BaseModel):
    level_1: str
    total_sales_quantity_breakdown: str

class CustomerItemCategoryResponse(BaseModel):
    customer_code: str
    item_category: List[CustomerItemCategoryDetail]



class CustomerItemNameDetail(BaseModel):
    level_1: str
    total_sales_quantity_breakdown: str

class CustomerItemNameResponse(BaseModel):
    customer_code: str
    item_name: List[CustomerItemNameDetail]


class SalesDataRequest(BaseModel):
    sales_data: Dict
    key: str = Field(default='item_name', description="Key to access the list of items in the sales data.")

class Product(BaseModel):
    level_1: str
    total_sales_quantity_breakdown: float
