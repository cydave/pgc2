import os

import sqlalchemy
from sqlalchemy.orm import sessionmaker


engine = sqlalchemy.create_engine(os.environ["SQLALCHEMY_DATABASE_URI"], pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=True, autocommit=False)
