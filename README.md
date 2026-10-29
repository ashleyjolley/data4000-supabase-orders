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

Test	Expected Behavior
1. Enter text instead of a customer ID:	Displays a helpful error message and asks again.
2. Enter a customer ID that does not exist:	Rejects the invalid ID and asks again.
3. Enter a product ID that does not exist:	Rejects the invalid ID and asks again.
4. Enter quantity 0, -2, 1.5, or hello:	Rejects each invalid quantity and asks again.
5. Cancel at the confirmation prompt (N):	Cancels the order without inserting a record into Supabase.
6. Confirm a valid order (Y):	Successfully inserts exactly one order into Supabase.
7. Retrieve the newly created order:	Retrieves the saved order from Supabase and displays it in the verification table.

