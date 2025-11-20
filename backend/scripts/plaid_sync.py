from dotenv import load_dotenv
from logic.sync_logic import plaid_sync

def main():
    plaid_sync()

if __name__ == "__main__":
    load_dotenv()
    main()