
BEGIN
    -- Create the target table if it doesn't exist
    CREATE TABLE IF NOT EXISTS combined_reviews (
        product_name VARCHAR(255),
        rating NUMERIC,
        review_date DATE,
        body TEXT,
        source VARCHAR(50)
    );
    
    -- Clear existing data
    TRUNCATE TABLE combined_reviews;
    
    -- Insert Amazon reviews
    INSERT INTO combined_reviews
    SELECT 
        product_title AS product_name,
        rating,
        CAST(review_date AS DATE) AS review_date,
        body,
        'amazon' AS source
    FROM amazon_reviews;
    
    -- Insert Best Buy reviews
    INSERT INTO combined_reviews
    SELECT 
        product_name,
        review_rating AS rating,
        review_date,
        concat_ws(',', review_title, review_text) AS body,
        'best_buy' AS source
    FROM best_buy_reviews;
    
    -- Insert Dick's Sporting reviews
    INSERT INTO combined_reviews
    SELECT 
        device AS product_name,
        rating,
        CAST(submission_time AS DATE) AS review_date,
        concat_ws(',', title, review_text) AS body,
        'dicks_sporting' AS source
    FROM dicks_sporting_reviews;
    
    -- Insert Horizon reviews
    INSERT INTO combined_reviews
    SELECT 
        product AS product_name,
        CAST(SUBSTRING(rating FROM 1 FOR 1) AS INTEGER) AS rating,
        CAST(date AS DATE) AS review_date,
        concat_ws(',', title, description) AS body,
        'horizon' AS source
    FROM horizon_reviews;
    
    -- Insert Peloton reviews
    INSERT INTO combined_reviews
    SELECT 
        equipment_type AS product_name,
        overall_rating AS rating,
        CAST(review_date AS DATE) AS review_date,
        concat_ws(',', title, body) AS body,
        'peloton' AS source
    FROM peloton_reviews;
    
    -- Insert Target reviews
    INSERT INTO combined_reviews
    SELECT 
        product_name,
        rating,
        CAST(submitted_at AS DATE) AS review_date,
        concat_ws(',', title, review_text) AS body,
        'target' AS source
    FROM target_reviews;
    
    -- Insert TurnTo reviews
    INSERT INTO combined_reviews
    SELECT 
        product_name,
        rating,
        CAST(review_date AS DATE) AS review_date,
        concat_ws(',', title, review_text) AS body,
        'turnto' AS source
    FROM turnto_reviews;
    
    -- Insert Wahoo reviews
    INSERT INTO combined_reviews
    SELECT 
        product_name,
        score AS rating,
        CAST(created_at AS DATE) AS review_date,
        concat_ws(',', title, content) AS body,
        'wahoo' AS source
    FROM wahoo_reviews;
    
    -- Insert Velocore reviews
    INSERT INTO combined_reviews
    SELECT 
        type AS product_name,
        rating,
        CAST(created_date AS DATE) AS review_date,
        concat_ws(',', title, details) AS body,
        'velocore' AS source
    FROM velocore_reviews;
    
    COMMIT;
END;
