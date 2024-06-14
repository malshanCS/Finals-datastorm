# app/data_processing.py

import pandas as pd
from .config import *

def create_full_df():
    trx_table = pd.read_csv(TRX_TABLE_PATH)
    item_info = pd.read_csv(ITEM_INFO_PATH)
    
    trx_table["transaction_time"] = pd.to_datetime(trx_table["transaction_time"])
    trx_table = trx_table.assign(
        year=trx_table["transaction_time"].dt.year,
        month=trx_table["transaction_time"].dt.month,
        day=trx_table["transaction_time"].dt.day,
        hour=trx_table["transaction_time"].dt.hour,
        minute=trx_table["transaction_time"].dt.minute
    )

    full_df = pd.merge(trx_table, item_info, on="item code", how="left")
    full_df["department_item_category"] = full_df["department"] + "-" + full_df["item_category"]
    full_df.to_csv(FULL_DF_PATH, index=False)

def create_maximum_sale_week_in_each_month():
    full_df = pd.read_csv(FULL_DF_PATH)
    full_df['transaction_time'] = pd.to_datetime(full_df['transaction_time'])
    full_df['week_of_month'] = (full_df['transaction_time'].dt.day - 1) // 7 + 1

    total_sales_by_week = full_df.groupby(['customer_code', 'month', 'week_of_month'])['sales_quantity'].sum().reset_index(name='total_sales')
    max_sales_weeks = total_sales_by_week.loc[total_sales_by_week.groupby(['customer_code', 'month'])['total_sales'].idxmax()]
    max_sales_weeks.to_csv(MAX_SALES_WEEKS_PATH, index=False)


def create_agg_df_department_item_category():
    full_df = pd.read_csv(FULL_DF_PATH)
    return full_df.groupby(['customer_code', 'department_item_category']).agg(
        total_sales_quantity=('sales_quantity', 'sum'),
        transaction_count=('transaction_time', 'count')
    ).reset_index()

def create_agg_df_item_category():
    full_df = pd.read_csv(FULL_DF_PATH)
    return full_df.groupby(['customer_code', 'item_category']).agg(
        total_sales_quantity=('sales_quantity', 'sum'),
        transaction_count=('transaction_time', 'count')
    ).reset_index()

def create_agg_df_item_name():
    full_df = pd.read_csv(FULL_DF_PATH)
    return full_df.groupby(['customer_code', 'item_name']).agg(
        total_sales_quantity=('sales_quantity', 'sum'),
        transaction_count=('transaction_time', 'count')
    ).reset_index()


def get_total_sales_quantity_breakdown_by_department_item_category(agg_df):
    agg_df['total_sales_percentage'] = agg_df.groupby('customer_code')['total_sales_quantity'].transform(lambda x: x / x.sum() * 100)
    agg_df['total_sales_quantity_breakdown'] = agg_df.apply(
        lambda row: {row['department_item_category']: f"{row['total_sales_percentage']:.2f}%"},
        axis=1
    )
    result_df = agg_df.groupby('customer_code')['total_sales_quantity_breakdown'].apply(
        lambda x: {k: v for d in x for k, v in d.items()}
    ).reset_index()

    result_df.to_csv(TOTAL_SALES_Q_BY_DEPT_ITEM_CAT_PATH, index=False)
    # return result_df

def load_full_df():
    return pd.read_csv(FULL_DF_PATH)

def get_total_sales_quantity_breakdown_by_item_category(agg_df):
    # Calculate the percentage of total_sales_quantity for each department_item_category relative to the total for each customer
    agg_df['total_sales_percentage'] = agg_df.groupby('customer_code')['total_sales_quantity'].transform(lambda x: x / x.sum() * 100)

    # Create the total_sales_quantity_breakdown column as a dictionary
    agg_df['total_sales_quantity_breakdown'] = agg_df.apply(lambda row: {row['item_category']: f"{row['total_sales_percentage']:.2f}%"} , axis=1)

    # Aggregate the dictionaries for each customer
    result_df = agg_df.groupby('customer_code')['total_sales_quantity_breakdown'].apply(
        lambda x: {k: v for d in x for k, v in d.items()}
    ).reset_index()

    result_df.to_csv(TOTAL_SALES_Q_BY_ITEM_CAT_PATH,index=False)

def get_total_sales_quantity_breakdown_by_item_name(agg_df):
    # Calculate the percentage of total_sales_quantity for each department_item_category relative to the total for each customer
    agg_df['total_sales_percentage'] = agg_df.groupby('customer_code')['total_sales_quantity'].transform(lambda x: x / x.sum() * 100)

    # Create the total_sales_quantity_breakdown column as a dictionary
    agg_df['total_sales_quantity_breakdown'] = agg_df.apply(lambda row: {row['item_name']: f"{row['total_sales_percentage']:.2f}%"} , axis=1)

    # Aggregate the dictionaries for each customer
    result_df = agg_df.groupby('customer_code')['total_sales_quantity_breakdown'].apply(
        lambda x: {k: v for d in x for k, v in d.items()}
    ).reset_index()


    result_df.to_csv(TOTAL_SALES_Q_BY_ITEM_NAME_PATH,index=False)

def get_top_products(sales_data, key='item_name'):
    try:
        # print(sales_data)
        # Extract items and filter out 'N/A'
        filtered_items = [
            item for item in sales_data[key]
            if item['total_sales_quantity_breakdown'] != 'N/A'
        ]
        # print(filtered_items)
        # Convert percentage strings to floats and sort by this value
        for item in filtered_items:
            item['total_sales_quantity_breakdown'] = float(item['total_sales_quantity_breakdown'].rstrip('%'))

        # Sort items based on sales percentage in descending order
        top_items = sorted(
            filtered_items, 
            key=lambda x: x['total_sales_quantity_breakdown'], 
            reverse=True
        )

        # Return top 5 items
        return top_items[:5]
    except KeyError as e:
        raise ValueError(f"Key error in sales data processing: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Value error in sales data processing: {str(e)}")

def get_top_category(sales_data, key='item_name'):
    try:
        # print(sales_data)
        # Extract items and filter out 'N/A'
        filtered_items = [
            item for item in sales_data[key]
            if item['total_sales_quantity_breakdown'] != 'N/A'
        ]
        # print(filtered_items)
        # Convert percentage strings to floats and sort by this value
        for item in filtered_items:
            item['total_sales_quantity_breakdown'] = float(item['total_sales_quantity_breakdown'].rstrip('%'))

        # Sort items based on sales percentage in descending order
        top_items = sorted(
            filtered_items, 
            key=lambda x: x['total_sales_quantity_breakdown'], 
            reverse=True
        )

        # Return top 5 items
        return top_items[:3]
    except KeyError as e:
        raise ValueError(f"Key error in sales data processing: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Value error in sales data processing: {str(e)}")

def get_top_department(sales_data, key='sales_data'):
    try:
        # print(sales_data)
        # Extract items and filter out 'N/A'
        filtered_items = [
            item for item in sales_data[key]
            if item['total_sales_quantity_breakdown'] != 'N/A'
        ]
        # print(filtered_items)
        # Convert percentage strings to floats and sort by this value
        for item in filtered_items:
            item['total_sales_quantity_breakdown'] = float(item['total_sales_quantity_breakdown'].rstrip('%'))

        # Sort items based on sales percentage in descending order
        top_items = sorted(
            filtered_items, 
            key=lambda x: x['total_sales_quantity_breakdown'], 
            reverse=True
        )

        # Return top 5 items
        return top_items[:3]
    except KeyError as e:
        raise ValueError(f"Key error in sales data processing: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Value error in sales data processing: {str(e)}")
