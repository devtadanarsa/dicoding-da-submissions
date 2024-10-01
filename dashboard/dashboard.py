import pandas as pd
import os
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import data_transformer as dt
import geopandas as gpd
from shapely.geometry import Point

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

data_all = pd.read_csv(os.path.join(BASE_DIR, 'main_data.csv'))
datetime_columns = ['order_delivered_customer_date', 'order_purchase_timestamp']
for column in datetime_columns:
    data_all[column] = pd.to_datetime(data_all[column])
    
min_date = data_all["order_purchase_timestamp"].min()
max_date = data_all["order_purchase_timestamp"].max()

with st.sidebar:
    st.image(os.path.join(BASE_DIR, 'logo.png'))
    
    min_year = min_date.year
    max_year = max_date.year

    start_col1, start_col2 = st.columns(2)
    with start_col1:
        start_month = st.selectbox('Start Month', list(range(1, 13)), index=min_date.month - 1)
    with start_col2:
        start_year = st.selectbox('Start Year', list(range(min_year, max_year + 1)), index=0)

    end_col1, end_col2 = st.columns(2)
    with end_col1:
        end_month = st.selectbox('End Month', list(range(1, 13)), index=max_date.month - 1)
    with end_col2:
        end_year = st.selectbox('End Year', list(range(min_year, max_year + 1)), index=max_year - min_year)
    
start_date = pd.Timestamp(start_year, start_month, 1)
end_date = pd.Timestamp(end_year, end_month, 1) + pd.offsets.MonthEnd(0)
    

filtered_data = data_all[(data_all['order_purchase_timestamp'] >= start_date) & (data_all['order_purchase_timestamp'] <= end_date)]

monthly_orders = dt.create_monthly_orders(filtered_data)
quartals_orders = dt.create_quartal_orders(filtered_data)
sum_product_category = dt.create_sum_products(filtered_data)
reviews_sum = dt.create_sum_reviews(filtered_data)
spending_distributions = dt.spending_filtered(filtered_data)
customer_geolocations = dt.customer_geolocations(filtered_data)
seller_geolocations = dt.seller_geolocations(filtered_data)
sum_customer_city, sum_seller_city, cust_city_colors, seller_city_colors = dt.customer_seller_city(filtered_data)


# DASHBOARD SECTION !!

st.title('Brazilian Ecommerce Dashboard :flag-br:')

st.subheader('Orders and Revenues Growth')
growthTab1, growthTab2 = st.tabs(["Per Month", "Per Quartal"])
# Monthly Orders Graph
with growthTab1:
    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.plot(monthly_orders.index, monthly_orders['order_count'], marker='o', linewidth=2, color='orange', label='Order Count')
    ax1.set_ylabel('Order Count', color='orange')
    ax1.tick_params(axis='y', labelcolor='orange')
    ax1.set_xticks(monthly_orders.index)
    ax1.set_xticklabels(monthly_orders.index, rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(monthly_orders.index, monthly_orders['revenue'], marker='o', linewidth=2, color='green', label='Revenue')
    ax2.set_ylabel('Revenue (R$)', color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    # plt.title("Growth per Month (Sep 2016 - Aug 2018)", fontsize=15)
    fig.tight_layout()
    st.pyplot(fig)

# Quartal Orders Graph
with growthTab2:
    monthly_orders.index = pd.to_datetime(monthly_orders.index)
    quartals_orders = monthly_orders.resample('QE').sum()
    quartals_orders.index = quartals_orders.index.to_period('Q').strftime('Q%q %Y')

    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.plot(quartals_orders.index, quartals_orders['order_count'], marker='o', linewidth=2, color='b', label='Order Count')
    ax1.set_ylabel('Order Count', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_xticks(quartals_orders.index)
    ax1.set_xticklabels(quartals_orders.index, rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(quartals_orders.index, quartals_orders['revenue'], marker='o', linewidth=2, color='g', label='Revenue')
    ax2.set_ylabel('Revenue (R$)', color='g')
    ax2.tick_params(axis='y', labelcolor='g')

    # plt.title("Growth per Quartal (2016 - 2018)", fontsize=15)
    fig.tight_layout()
    st.pyplot(fig)

# Product Category Performance Graph
st.subheader("Best & Worst Performing Product")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35,15))

colors = ["orange", "lightgray", "lightgray", "lightgray", "lightgray"]

sns.barplot(x="quantity", y="product_category_name", data=sum_product_category.head(5), palette=colors, ax=ax[0])
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_ylabel(None)
ax[0].set_title("Most Selling Products", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="quantity", y="product_category_name", data=sum_product_category.sort_values(by='quantity', ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].yaxis.tick_right()
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position('right')
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Review Score Graph
st.subheader("Review Score Distribution")
reviews_colors = ['lightgray' if qty != reviews_sum['quantity'].max() else 'orange' for qty in reviews_sum['quantity']]

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x=reviews_sum['review_score'], height=reviews_sum['quantity'], color=reviews_colors)
ax.set_xlabel('Review Score', fontsize=12)
ax.set_ylabel('Quantity', fontsize=12)
ax.set_xticks(reviews_sum['review_score'])
ax.set_xticklabels(reviews_sum['review_score'], fontsize=10)
ax.tick_params(axis='y', labelsize=10)

ax.grid(axis='y', linestyle='--', alpha=0.7)
fig.tight_layout()
st.pyplot(fig)

# Spending Distribution Graph
st.subheader("Customer Spending Distribution")

fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(spending_distributions['payment_value'], bins=30, kde=True, color='orange')
plt.xlabel('Total Spending (R$)')
plt.ylabel('Frequency')

st.pyplot(fig)


## CUSTOMER GEOGRAPHIC SECTION
st.subheader("Customers and Sellers Geographic Location")
geographyTab1, geographyTab2, geographyTab3 = st.tabs(["Customers Geolocation", "Sellers Geolocation", "Popular City"])
# Customer Geographic Location
with geographyTab1:
    geometry = [Point(xy) for xy in zip(customer_geolocations['geolocation_lng'], customer_geolocations['geolocation_lat'])]
    gdf = gpd.GeoDataFrame(customer_geolocations, geometry=geometry)
    gdf.set_crs(epsg=4326, inplace=True)

    world = gpd.read_file(os.path.join(BASE_DIR, '..', 'data', 'naturalearth_lowres', 'naturalearth_lowres.shp'))
    brazil = world[world.name == 'Brazil']

    fig, ax = plt.subplots(figsize=(12, 12))
    brazil.plot(ax=ax, color='lightgray', edgecolor='black')  # Plot Brazil map

    gdf.plot(ax=ax, color='orange', alpha=0.7, markersize=10)  # Plot points on top

    plt.xlim([-75, -30])
    plt.ylim([-35, 10])

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.title('Where the customers lived', fontsize=16)
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)

    st.pyplot(fig)

# Seller Geographic Location
with geographyTab2:
    geometry = [Point(xy) for xy in zip(seller_geolocations['geolocation_lng'], seller_geolocations['geolocation_lat'])]
    gdf = gpd.GeoDataFrame(seller_geolocations, geometry=geometry)
    gdf.set_crs(epsg=4326, inplace=True)

    fig, ax = plt.subplots(figsize=(12, 12))
    brazil.plot(ax=ax, color='lightgray', edgecolor='black')

    gdf.plot(ax=ax, color='green', alpha=0.7, markersize=10)

    plt.xlim([-75, -30])
    plt.ylim([-35, 10])

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.title('Where the sellers lived', fontsize=16)
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)

    st.pyplot(fig)

# Top Cities Graph
with geographyTab3:
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24,10))

    ax[0].bar(x=sum_customer_city['customer_city'].head(), height=sum_customer_city['quantity'].head(), color=cust_city_colors)
    ax[0].set_title("Five cities most customers lived", fontsize=30)
    ax[0].tick_params(axis='y', labelsize=25)
    ax[0].tick_params(axis='x', labelsize=20, rotation=45)
    
    ax[1].bar(x=sum_seller_city['seller_city'].head(), height=sum_seller_city['quantity'].head(), color=seller_city_colors)
    ax[1].set_title("Five cities most sellers lived", fontsize=30)
    ax[1].tick_params(axis='y', labelsize=25)
    ax[1].tick_params(axis='x', labelsize=20, rotation=45)
    

    st.pyplot(fig)

st.caption('Copyright (c) Devta Danarsa 2024')