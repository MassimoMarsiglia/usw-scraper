import time
import uswscraper.uswscraper.database.database
from dotenv import load_dotenv

def main():

    load_dotenv()  # Load environment variables from .env file
    db = uswscraper.uswscraper.database.database.DatabaseManager()
    db.connect()
    db.init_db()
    time.sleep(5)  # Wait for the database to initialize
main()