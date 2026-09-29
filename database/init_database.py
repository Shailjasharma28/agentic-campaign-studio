from database.database import init_db, Base
from database import models

print("Creating Database Tables....")

init_db()

print("Tables created successfully!")
print("Registered tables:", Base.metadata.tables.keys())