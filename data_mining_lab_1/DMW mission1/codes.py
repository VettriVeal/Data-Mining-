ATTACH 'host=localhost port=5433 dbname=annapurna user=annapurna password=annapurna'
AS pg (TYPE postgres);

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_category;
DROP TABLE IF EXISTS dim_store;

CREATE TABLE dim_store AS
SELECT
    store_id,
    store_name,
    address_line,
    city,
    state,
    region,
    floor_area_sqft,
    opened_on
FROM pg.public.stores;

CREATE TABLE dim_category AS
SELECT
    category_id,
    category_name,
    department,
    gst_rate
FROM pg.public.product_categories;

CREATE TABLE dim_product AS
SELECT
    product_sk,
    product_code,
    product_name,
    category_id,
    brand,
    pack_size,
    uom,
    valid_from,
    valid_to,
    is_current
FROM pg.public.products;

CREATE TABLE dim_date AS
SELECT
    d::DATE AS date_key,
    EXTRACT(YEAR FROM d)::INTEGER AS year,
    EXTRACT(MONTH FROM d)::INTEGER AS month,
    STRFTIME(d, '%B') AS month_name,
    EXTRACT(DAY FROM d)::INTEGER AS day,
    STRFTIME(d, '%A') AS day_of_week
FROM generate_series(
    DATE '2024-01-01',
    DATE '2024-12-31',
    INTERVAL '1 day'
) AS t(d);

CREATE TABLE fact_sales AS
SELECT
    c.business_date AS date_key,
    regexp_extract(c.bill_no, '^(S[0-9]{2})/', 1) AS store_id,
    p.product_sk,
    p.category_id,
    c.bill_no,
    c.line_no,
    c.line_type,
    c.qty,
    c.unit_price,
    c.qty * c.unit_price AS line_amount
FROM canonical_sales c
LEFT JOIN pg.public.products p
    ON c.product_code = p.product_code
   AND c.business_date >= p.valid_from
   AND c.business_date <= p.valid_to;

SELECT 'dim_store' AS table_name, COUNT(*) AS row_count FROM dim_store
UNION ALL
SELECT 'dim_category', COUNT(*) FROM dim_category
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date
UNION ALL
SELECT 'fact_sales', COUNT(*) FROM fact_sales;