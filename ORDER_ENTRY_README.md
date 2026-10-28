# DATA 4000 - Customer Order Entry System

## Description

This Python program connects to a Supabase database to create and verify
customer orders. It retrieves customers and products, validates user input,
calculates order totals, saves orders, and verifies successful insertion.

## Requirements

- Python 3
- A Supabase project configured for this course
- The packages listed in `requirements.txt`

## Setup

Run these commands from the repository root:

1. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

2. Create a local `.env` file using `env.example` as a template. Set
   `SUPABASE_URL` and `SUPABASE_SECRET_KEY` to your own project values. Keep
   `.env` private; it is excluded from Git.

3. Run the program:

   ```powershell
   python order_entry.py
   ```

## Testing results

Record the actual results after testing:

- Text instead of customer ID:
- Nonexistent customer ID:
- Nonexistent product ID:
- Quantity of 0:
- Quantity of -2:
- Quantity of 1.5:
- Quantity of hello:
- Cancelled order:
- Successful insertion:
- Verification query:

## Screenshots

Add terminal screenshots or copied output showing a successful order insertion
and verification. Do not include credentials or other secrets.

## References

Document any libraries or techniques used that were not covered in class.
