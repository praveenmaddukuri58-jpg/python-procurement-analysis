# ============================================
# PROCUREMENT SPEND ANALYSIS
# Author: [Your Name]
# ============================================

import pandas as pd

# ============================================
# LOAD DATA
# ============================================

df = pd.read_csv('sample_data.csv')
df['order_date'] = pd.to_datetime(df['order_date'])
df['month'] = df['order_date'].dt.to_period('M')
df['quarter'] = df['order_date'].dt.to_period('Q')

print("=" * 55)
print("   PROCUREMENT SPEND ANALYSIS — FULL REPORT")
print("=" * 55)
print(f"\nDataset loaded: {len(df)} purchase orders")
print(f"Date range:     {df['order_date'].min().date()} to {df['order_date'].max().date()}")
print(f"Total spend:    ${df['total_amount'].sum():,.2f}")


# ============================================
# SECTION 1: SUPPLIER SPEND ANALYSIS
# Business Question: Which suppliers are we most dependent on?
# ============================================

print("\n" + "=" * 55)
print("SECTION 1: SUPPLIER SPEND ANALYSIS")
print("=" * 55)

supplier_summary = df.groupby('supplier').agg(
    total_orders    = ('order_id',     'count'),
    total_spend     = ('total_amount', 'sum'),
    avg_order_value = ('total_amount', 'mean')
).sort_values('total_spend', ascending=False).reset_index()

supplier_summary['pct_of_spend'] = (
    supplier_summary['total_spend'] / supplier_summary['total_spend'].sum() * 100
).round(1)

supplier_summary['total_spend']     = supplier_summary['total_spend'].map('${:,.2f}'.format)
supplier_summary['avg_order_value'] = supplier_summary['avg_order_value'].map('${:,.2f}'.format)
supplier_summary['pct_of_spend']    = supplier_summary['pct_of_spend'].map('{}%'.format)

print(supplier_summary.to_string(index=False))


# ============================================
# SECTION 2: DEPARTMENT SPEND ANALYSIS
# Business Question: Which departments are driving the most spend?
# ============================================

print("\n" + "=" * 55)
print("SECTION 2: DEPARTMENT SPEND ANALYSIS")
print("=" * 55)

dept_summary = df.groupby('department').agg(
    total_orders = ('order_id',     'count'),
    total_spend  = ('total_amount', 'sum'),
    avg_order    = ('total_amount', 'mean')
).sort_values('total_spend', ascending=False).reset_index()

dept_summary['pct_of_spend'] = (
    dept_summary['total_spend'] / dept_summary['total_spend'].sum() * 100
).round(1)

dept_summary['total_spend'] = dept_summary['total_spend'].map('${:,.2f}'.format)
dept_summary['avg_order']   = dept_summary['avg_order'].map('${:,.2f}'.format)
dept_summary['pct_of_spend'] = dept_summary['pct_of_spend'].map('{}%'.format)

print(dept_summary.to_string(index=False))


# ============================================
# SECTION 3: MONTHLY SPEND TREND
# Business Question: How has spend trended month over month?
# ============================================

print("\n" + "=" * 55)
print("SECTION 3: MONTHLY SPEND TREND")
print("=" * 55)

monthly = df.groupby('month').agg(
    total_orders = ('order_id',     'count'),
    total_spend  = ('total_amount', 'sum')
).reset_index()

monthly['mom_change'] = monthly['total_spend'].pct_change() * 100
monthly['mom_change'] = monthly['mom_change'].map(
    lambda x: f"{x:+.1f}%" if pd.notna(x) else "—"
)
monthly['total_spend'] = monthly['total_spend'].map('${:,.2f}'.format)

print(monthly.to_string(index=False))


# ============================================
# SECTION 4: QUARTERLY SPEND BREAKDOWN
# Business Question: Which quarter had the highest spend?
# ============================================

print("\n" + "=" * 55)
print("SECTION 4: QUARTERLY SPEND BREAKDOWN")
print("=" * 55)

quarterly = df.groupby('quarter').agg(
    total_orders = ('order_id',     'count'),
    total_spend  = ('total_amount', 'sum')
).reset_index()

quarterly['pct_of_annual'] = (
    quarterly['total_spend'] / quarterly['total_spend'].sum() * 100
).round(1)

quarterly['total_spend']   = quarterly['total_spend'].map('${:,.2f}'.format)
quarterly['pct_of_annual'] = quarterly['pct_of_annual'].map('{}%'.format)

print(quarterly.to_string(index=False))


# ============================================
# SECTION 5: ANOMALY DETECTION
# Business Question: Are there suspicious or unusually large orders?
# ============================================

print("\n" + "=" * 55)
print("SECTION 5: ANOMALY DETECTION")
print("=" * 55)

mean_spend  = df['total_amount'].mean()
std_spend   = df['total_amount'].std()
threshold   = mean_spend + (2 * std_spend)

anomalies = df[df['total_amount'] > threshold][[
    'order_id', 'order_date', 'supplier',
    'department', 'item_description', 'total_amount'
]].copy()

anomalies['total_amount'] = anomalies['total_amount'].map('${:,.2f}'.format)

print(f"\nAnomaly threshold (mean + 2 std devs): ${threshold:,.2f}")
print(f"Orders flagged: {len(anomalies)}\n")
print(anomalies.to_string(index=False))


# ============================================
# SECTION 6: CATEGORY SPEND BREAKDOWN
# Business Question: Which spend categories are largest?
# ============================================

print("\n" + "=" * 55)
print("SECTION 6: CATEGORY SPEND BREAKDOWN")
print("=" * 55)

category = df.groupby('category').agg(
    total_orders = ('order_id',     'count'),
    total_spend  = ('total_amount', 'sum'),
    avg_order    = ('total_amount', 'mean')
).sort_values('total_spend', ascending=False).reset_index()

category['pct_of_spend'] = (
    category['total_spend'] / category['total_spend'].sum() * 100
).round(1)

category['total_spend'] = category['total_spend'].map('${:,.2f}'.format)
category['avg_order']   = category['avg_order'].map('${:,.2f}'.format)
category['pct_of_spend'] = category['pct_of_spend'].map('{}%'.format)

print(category.to_string(index=False))


# ============================================
# SECTION 7: PRICE CONSISTENCY CHECK
# Business Question: Are we paying different prices for the same item?
# ============================================

print("\n" + "=" * 55)
print("SECTION 7: PRICE CONSISTENCY CHECK")
print("=" * 55)

price_check = df.groupby('item_description').agg(
    times_purchased = ('order_id',    'count'),
    min_price       = ('unit_price',  'min'),
    max_price       = ('unit_price',  'max'),
    avg_price       = ('unit_price',  'mean')
).reset_index()

price_check['price_variance'] = price_check['max_price'] - price_check['min_price']
price_check = price_check[price_check['price_variance'] > 0].sort_values(
    'price_variance', ascending=False
)

price_check['min_price']      = price_check['min_price'].map('${:,.2f}'.format)
price_check['max_price']      = price_check['max_price'].map('${:,.2f}'.format)
price_check['avg_price']      = price_check['avg_price'].map('${:,.2f}'.format)
price_check['price_variance'] = price_check['price_variance'].map('${:,.2f}'.format)

print("\nItems where we paid different prices across orders:\n")
print(price_check.to_string(index=False))

print("\n" + "=" * 55)
print("   END OF REPORT")
print("=" * 55)
