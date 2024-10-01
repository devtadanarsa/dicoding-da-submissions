import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_monthly_orders(data_all):
    monthly_orders = (
        data_all.resample('ME', on='order_purchase_timestamp')
        .agg(order_count=('order_id', 'nunique'), revenue=('payment_value', 'sum'))
    )

    monthly_orders.index = monthly_orders.index.strftime("%b %Y")
    return monthly_orders

def create_quartal_orders(data_all):
    monthly_orders = create_monthly_orders(data_all)
    
    monthly_orders.index = pd.to_datetime(monthly_orders.index)
    quartals_orders = monthly_orders.resample('QE').sum()
    quartals_orders.index = quartals_orders.index.to_period('Q').strftime('Q%q %Y')
    
def create_sum_products(data_all):
    sum_product_category = pd.DataFrame(data_all.groupby(by='product_category_name')
        .product_id.nunique()
        .sort_values(ascending=False)
        .reset_index()).rename(columns={'product_id': 'quantity'})
    
    return sum_product_category

def create_sum_reviews(data_all):
    reviews_sum = pd.DataFrame(data_all.groupby(by='review_score')
        .order_id.nunique()
        .sort_values(ascending=False)
        .reset_index()).rename(columns={'order_id': 'quantity'})    
    
    return reviews_sum

def spending_filtered(data_all):
    spending_distributions = data_all.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", 
        "payment_value": "sum"
    })

    spending_filtered = spending_distributions[spending_distributions['payment_value'] <= spending_distributions['payment_value'].quantile(0.95)]
    
    return spending_filtered

def customer_geolocations(data_all):
    geolocations = pd.read_csv(os.path.join(BASE_DIR, '..', 'data', 'geolocation.csv'))
    geolocations = geolocations[geolocations['geolocation_zip_code_prefix'].isin(data_all['customer_zip_code_prefix'])]
    
    return geolocations

def seller_geolocations(data_all):
    geolocations = pd.read_csv(os.path.join(BASE_DIR, '..', 'data', 'geolocation.csv'))
    geolocations = geolocations[geolocations['geolocation_zip_code_prefix'].isin(data_all['seller_zip_code_prefix'])]
    
    return geolocations

def customer_seller_city(data_all):
    sum_customer_city = pd.DataFrame(data_all.groupby(by='customer_city').customer_id.nunique().sort_values(ascending=False).reset_index()).rename(columns={'customer_id': 'quantity'})
    sum_seller_city = pd.DataFrame(data_all.groupby(by='seller_city').seller_id.nunique().sort_values(ascending=False).reset_index()).rename(columns={'seller_id': 'quantity'})

    max_cust_city_qty = sum_customer_city['quantity'].max()
    max_seller_city_qty = sum_seller_city['quantity'].max()

    cust_city_colors = ['lightgray' if qty != max_cust_city_qty else 'orange' for qty in sum_customer_city['quantity']]
    seller_city_colors = ['lightgray' if qty != max_seller_city_qty else 'green' for qty in sum_seller_city['quantity']]
    
    return sum_customer_city, sum_seller_city, cust_city_colors, seller_city_colors