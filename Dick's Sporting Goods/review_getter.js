const axios = require('axios');
const { Pool } = require('pg');
const format = require('pg-format');
const { getProducts } = require('./product_get'); // Assuming you already ported this

// Database configuration
const DB_CONFIG = {
  user: 'admin',
  host: 'raghuserver',
  database: 'SII',
  password: 'raghu@123',
  port: 5432
};

const headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
  'Accept': 'application/json',
  'Accept-Encoding': 'gzip, deflate',
  'Accept-Language': 'en-US,en;q=0.9',
  'Referer': 'https://www.dickssportinggoods.com',
  'Cookie': 'DSG_HIDE_OOS_RC=true; AdditionalLanes=77,94,56,96,61,9; _abck=47FA76FEBD8F86479DA847BE6EB96411~-1~YAAQ6xjQF09oZ0CVAQAAh7hORA1U1ZwxuxOHDFkILVLY657oZICIYNWP5AVVPed5qwxOcNCg51QFuSaH6XB/52qsxQI7QzK6MjOLbbkcsM5RQhNzrHfjD3tY17e/kFfKPVFz0pT4QSbaYqltWnkQwH5btghmXZ22m8etJslVSlZyzfgb24eSWL3Cw6k67tjrohyBjJ7zqp1AK6T3zFn5EG/avibWAifYLZbiTtGEk/Ebwu0J/TgKeO5DZ4rWR85xXP5J5NmPIN9Cni4j2Yw16Nqmq3c4pKT/Qhkme2nmmGsLEYoK5/6MNxXL8wfOGfPK+g+sNjClFEb9mjeZXzHVWh2q2YOPtQ5O/gm1ENzi+dLZYMTR2/rB13Qw/wjQgzedzkU8arKkIS4KrJk7HG+MM3mrfinj2d5TqHuIZLvm1N1V4XpiVDs52nU=~-1~-1~-1; ak_bmsc=DC3C470789482B879E7311668A21DC21~000000000000000000000000000000~YAAQ6xjQF1BoZ0CVAQAAh7hORBr9mM0DQKg8UTjDVqreXvymzfLfBTsaJzDcpCOJKAeC0ZeM5zsrO5rfSuHEvH44AA/nP/lbhGXsaNRNai0cn+G/y1xUv2Q0OOvfEayjKvZK42SqnqZZpYODXEu3zJwDcaIFcSQDrEnLtmxwBmaanUy2n9xoCpNb/toysEmN+1qB6+SlDoFbbsHJbTX6aguCju7CXGooEajKYf3vbqAu+RA+B75yWMPDeQj8ZpNnH4SH31aCz2nisfgVyYkPIY6MryWVb+qmkBWVSHX1A32S2SqCa76X2BMuGrZDbYYLwVH2lxa3xBaRruQnrdjDzy4MehCXgzkqmU1MlsyHyrKUvsAaWTjC; bm_sz=FB128F6956A650DA9B620972C31DC007~YAAQ6xjQF1FoZ0CVAQAAh7hORBrhbYmFuGdauXlie0Ix2CGgrICkeEEhJOnTcng5e/Gun6GO8a6XL7OQx8CFn9/jGg0vEBekoRG69GQTYbMhr2I3K/GqKKj54Vb/2MKSuZ9uRDQk9IHoOXUvzevKVc2KpyKA1MV2+o7HqP4QDPt0XGif5cCinDAlB8aAb6GrMzFxTuDzAYnHtq4VFODJVEgNmu/KMDfdU9ymXTJ/O5iOyOxSemkD5qQyOkvzkDwRdFxFdlcNTDwiGrWf4Bq8R5MS3y6n/GYsJ9MuylvUGwvbx1jLsbvWAGk/lIZt/TEjdv2wCskJGwT87YCOAGDYkxy5Y/M1Qm8v1cJ9PBm3fLixOZ8ygtDSM6+KgHIoY17F1Qj8omD1duio/5MU~3355718~4403248; NNC=1; akaas_AS_EXP_DSG=2147483647~rv=86~id=b0de811ddc24a5a4935e2c36915b53da; dih=desktop; dsg_perf_analysis=NB-0; swimlane_as_exp_dsg=86; whereabouts=46201',
  'Connection': 'keep-alive',
};

const BASE_URL = "www.dickssportinggoods.com";
const API_KEY = "cahWEzSiPp0IPkqzl0gm4jqVhsyCj0T2DLPYonOqIqDoc";
const LIMIT = 100;

// Create database connection pool
const pool = new Pool(DB_CONFIG);

// Connect to the database
async function createConnection() {
  try {
    const client = await pool.connect();
    return client;
  } catch (error) {
    console.error(`Error connecting to PostgreSQL: ${error}`);
    return null;
  }
}

// Fetch reviews with pagination
async function fetchReviews(offset, productId) {
  const params = new URLSearchParams({
    passkey: API_KEY,
    apiVersion: "5.4",
    Filter: `productId:${productId}`,
    Limit: LIMIT,
    Offset: offset,
    Sort: "SubmissionTime:desc"
  }).toString();

  try {
    const url = `https://${BASE_URL}/p/reviews-api/data/reviews.json?${params}`;
    const response = await axios.get(url, { headers });
    
    if (response.status !== 200) {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
    
    return response.data;
  } catch (error) {
    console.error(`Error fetching reviews: ${error.message}`);
    throw error;
  }
}

// Parse a single review
function parseReview(review) {
  return {
    id: review.Id,
    rating: review.Rating,
    title: review.Title,
    review_text: review.ReviewText,
    author: review.UserNickname,
    location: review.UserLocation,
    submission_time: review.SubmissionTime,
    is_recommended: review.IsRecommended,
    secondary_ratings: JSON.stringify(review.SecondaryRatings || {}),
    context_data: JSON.stringify(review.ContextDataValues || {}),
    badges: JSON.stringify(review.Badges || {}),
    photos: JSON.stringify(review.Photos || []),
    pros: review.Pros,
    cons: review.Cons
  };
}

// Insert reviews into the database
async function insertReviews(client, reviews, name) {
  const insertSql = `
    INSERT INTO dicks_reviews (
      id, device, rating, title, type, review_text, author, location, submission_time,
      is_recommended, secondary_ratings, context_data, badges, photos, pros, cons
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
    ON CONFLICT (id) DO NOTHING;
  `;

  try {
    await client.query('BEGIN');
    
    for (const review of reviews) {
      const values = [
        review.id,
        name,
        review.rating,
        review.title,
        'Exercise Bike',
        review.review_text,
        review.author,
        review.location,
        review.submission_time,
        review.is_recommended,
        review.secondary_ratings,
        review.context_data,
        review.badges,
        review.photos,
        review.pros,
        review.cons
      ];
      
      await client.query(insertSql, values);
    }
    
    await client.query('COMMIT');
    console.log(`Inserted ${reviews.length} reviews into the database.`);
  } catch (error) {
    await client.query('ROLLBACK');
    console.error(`Error inserting reviews: ${error}`);
  }
}

// Scrape all reviews for a product
async function scrapeAllReviews(productId, productName) {
  const allReviews = [];
  let offset = 0;

  const client = await createConnection();
  if (!client) return;

  try {
    while (true) {
      console.log(`Fetching reviews from offset ${offset}...`);
      const data = await fetchReviews(offset, productId);
      const reviews = data.Results || [];
      
      if (reviews.length === 0) {
        break; // No more reviews to fetch
      }

      // Parse reviews
      for (const review of reviews) {
        const parsedReview = parseReview(review);
        allReviews.push(parsedReview);
      }

      // Update offset for pagination
      offset += LIMIT;

      // Stop if we've fetched all reviews
      if (offset >= data.TotalResults) {
        break;
      }
    }

    // Save results to database
    await insertReviews(client, allReviews, productName);
    console.log(`Scraping complete. Total reviews collected: ${allReviews.length}`);
  } catch (error) {
    console.error(`Error scraping reviews: ${error}`);
  } finally {
    client.release();
  }
}

// Scrape reviews for a specific search term
async function scrapeReviewsBySearchTerm(searchTerm) {
  const productList = await getProducts(searchTerm);
  const results = [];

  for (const [productId, productName] of productList) {
    await scrapeAllReviews(productId, productName);
    results.push({ productId, productName });
  }
  return results;
}

// Main function
async function main() {
  await scrapeReviewsBySearchTerm("exercise bike");
}

// Run the script if executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  scrapeAllReviews,
  scrapeReviewsBySearchTerm,
  fetchReviews,
  parseReview,
  DB_CONFIG
};