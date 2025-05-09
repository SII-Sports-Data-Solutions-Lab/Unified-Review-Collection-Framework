# Split Reviews by Sentence

This module provides functionality to split product reviews into sentences and store them in a database. It is designed for use with a PostgreSQL database and can be used as a standalone script or imported as a module in other Python projects.

## Features
- Connects to a PostgreSQL database
- Fetches unprocessed reviews
- Splits each review into sentences using the `sentencex` library
- Stores the split sentences in a separate table
- Skips non-English reviews

## Requirements
- Python 3.8+
- PostgreSQL database with the required tables (`combined_reviews`, `review_sentences`)
- Python packages: `psycopg2`, `sentencex`, `langdetect`, `python-dotenv`, `google-generativeai` (optional)

Install dependencies:
```bash
pip install psycopg2-binary sentencex langdetect python-dotenv google-generativeai
```

## Usage

### As a Script
You can run the notebook as a script (after converting to `.py`) or copy the code into a Python file. The main logic is encapsulated in the `process_reviews()` function.

```python
from split_reviews import process_reviews
process_reviews()
```

### As a Notebook
You can run all cells in the notebook to process reviews interactively.

## Configuration
- Update the `DB_CONFIG` dictionary in the code with your database credentials.
- Optionally, set the `GEMINI_API_KEY` in your environment variables or `.env` file if you want to use Gemini models.

## Database Schema
- `combined_reviews` table must have columns: `id`, `body`, `processed` (boolean)
- `review_sentences` table must have columns: `review_id`, `sentence_num`, `sentence`

## License
MIT
