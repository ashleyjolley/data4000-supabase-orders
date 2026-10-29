# DATA 4000 - Campus Store Order Entry

This Streamlit application reads fictional customers, products, and orders from
the course Supabase project. Users can review a current product price, confirm
an order, and verify the saved record with a separate database query.

## Run locally

Use Python 3.11 or newer. From the repository root:

```powershell
python -m pip install -r requirements.txt
Copy-Item env.example .env
```

Edit `.env` and set your own Supabase URL, Supabase secret key, and a private
classroom app password. Then start the app:

```powershell
streamlit run app.py
```

The app password is required before the application makes any database
requests. Share it only with authorized classmates and the instructor. The
Supabase secret key is privileged and must never be committed or shared.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), create an app
   from this repository, the `main` branch, and `app.py`.
3. In the app's **Settings → Secrets**, add the following TOML values using
   your own credentials and a strong classroom password:

   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_SECRET_KEY = "sb_secret_your_actual_key"
   APP_PASSWORD = "replace-with-a-private-classroom-password"
   ```

4. Deploy and open the app while authorized. Test the hosted app and record
   real results below. Do not put credentials, the app password, or
   unredacted secrets in screenshots or this repository.

### Published application

- Streamlit app URL: https://data4000-supabase-orders-ah4lx9ks8vq2mjurxwbpss.streamlit.app/
- GitHub repository: https://github.com/ashleyjolley/data4000-supabase-orders

The app is deployed, but access is not yet configured. Add `APP_PASSWORD`,
`SUPABASE_URL`, and `SUPABASE_SECRET_KEY` in the app's Streamlit Community
Cloud **Manage app → Settings → Secrets** before using it.

## Features

- Loads customer, product, and order records from Supabase through its API.
- Displays product prices as currency and supports refreshing the data.
- Uses named customer/product choices while retaining their database IDs.
- Requires a review and explicit confirmation before inserting an order.
- Checks the current product price again at submission and requires
  reconfirmation if it changed.
- Retrieves a newly inserted order by its generated ID for verification.
- Shows order history and can filter it by customer, totaling stored sale prices.
- Restricts database access behind a server-checked password gate.

## Testing results

The hosted app is deployed but still needs its secrets configured and the
following tests completed. Replace each pending result with the observed
result after testing:

| Test | Result |
|---|---|
| Open the deployed app with the classroom password | Pending deployment |
| View customers and products loaded from Supabase | Pending deployment |
| Enter an invalid quantity | Pending deployment |
| Submit without confirmation | Pending deployment |
| Confirm and submit one valid order | Pending deployment |
| Verify the new order with a fresh query | Pending deployment |
| Interact with another widget without duplicating the order | Pending deployment |
| Refresh and find the saved order in history | Pending deployment |
| Filter history by customer and view the stored-price total | Pending deployment |

Add screenshots of the order-entry interface and a successfully verified
order after testing the hosted app. Ensure screenshots do not reveal
credentials or the classroom app password.

## Configuration and dependencies

- `app.py` - Streamlit application.
- `database.py` - Supabase API helpers, order insertion, and verification query.
- `config.py` - Local environment and Supabase credential validation.
- `env.example` - Placeholder-only local configuration template.
- `requirements.txt` - Packages installed by Streamlit Community Cloud.

The existing Supabase tables must be provisioned with the course schema and
fictional classroom data. `.env`, `.venv/`, generated Python files, and
`.streamlit/secrets.toml` are excluded from Git.
