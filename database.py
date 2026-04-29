from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite (для разработки). Для PostgreSQL замените URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./recipes.db"
# PostgreSQL пример:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/recipedb"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Только для SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Функция получения сессии БД (для Dependency Injection FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()