from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# One engine per process  manages the connection pool.
# pool_pre_ping=True checks connection health before reuse,
# which handles dropped connections gracefully.
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    # FastAPI dependency that yields a DB session per request.
    # The finally block guarantees cleanup even if the route throws.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
