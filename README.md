# Plaid Dashboard
This is a dashboard which shows historical transaction data using the plaid api.

### How it works
The dashboard works by pulling data from plaid and storing it locally in CSV files.
This is done in the `update_ledger.py` script which creates both a `raw_ledger.csv` and a `clean_ledger.csv`.
The latter is tailored to each user and uses a `mapping.json` file to map certain plaid categories or merchant names to a user-created category.

The dashboard backend API is in the `retrieve.py` file and the frontend is in the `plaid_frontend` folder.
It reads from the `clean_ledger.csv` file to populate the dashboard.

### How to run
1. Obtain an access token, client id, and secret key from [Plaid Quickstart](https://plaid.com/docs/quickstart/) and store them in ACCESS_TOKEN, CLIENT_ID, and SECRET variables in a `.env` file.
1. Optionally create a mappings.json file formatted: 
```
{
    "category_map": {
        "[plaid category]": "[your category]",
    },
    "name_map": {
        "[merchant name]": "[your category]",
    }
}
```
1. Install the python requirements `pip install -r requirements.txt`
1. Run `python update_ledger.py` script to create the `raw_ledger.csv` and `clean_ledger.csv` files.
1. Run the dashboard by running `python retrieve.py` and then `cd plaid_frontend; ng serve`