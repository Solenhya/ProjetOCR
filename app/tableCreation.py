from dotenv import load_dotenv
load_dotenv()

from db import table_creation

table_creation.CreateTable()