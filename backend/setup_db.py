import asyncio
from app.services.db_seed import initialize_database
from update_db import update_bangalore

async def main():
    print("Initializing and seeding database...")
    await initialize_database()
    print("Updating Bangalore with new amusement parks...")
    update_bangalore()
    print("Database fully setup and updated!")

if __name__ == "__main__":
    asyncio.run(main())
