# DATA 4000 - Customer Order Entry System

## Description

This Python program connects to a Supabase database
to create and verify customer orders.

The program retrieves customers and products,
validates user input, calculates order totals,
saves orders, and verifies successful insertion.

## Requirements

- Python 3
- Supabase database
- supabase Python library
- python-dotenv

## Setup

1. Clone the GitHub repository.
2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Copy `env.example` to `.env`.
4. Add your own Supabase URL and secret key to `.env`. Do not share or commit
   this file; it is excluded from Git.
5. Run:

   ```powershell
   python order_entry.py
   ```

## Testing Results

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

Include terminal screenshots or copied output
showing a successful order insertion and verification.
Do not include credentials or other secrets.

## References

Document any libraries or techniques used
that were not covered in class.
