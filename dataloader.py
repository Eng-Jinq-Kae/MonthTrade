from sqlalchemy import text, create_engine
import pandas as pd

engine = create_engine(
    "postgresql+psycopg2://mthtradeuser:123@localhost:5432/MthTrade"
)

query = text("""
    SELECT * FROM "RefSection"
""")

with engine.connect() as conn:
    df = pd.read_sql(query, conn)

print(df)