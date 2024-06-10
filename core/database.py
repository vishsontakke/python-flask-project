import os
import importlib
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

# DB_USER     = os.environ.get('DB_USER')
# DB_PASSWORD = ":"+os.environ.get('DB_PASSWORD') if os.environ.get('DB_PASSWORD') else '' 
# DB_HOST     = os.environ.get('DB_HOST')
# DB_PORT     = os.environ.get('DB_PORT')
# DB_DATABASE = os.environ.get('DB_DATABASE')


engine = create_engine('sqlite:///project_1.db')
# engine = create_engine(f"mysql+pymysql://{DB_USER}{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}")
db_session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=engine
                )
            )
            
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import core.models
    Base.metadata.create_all(bind=engine)


def create_db(all_microservices_names=[]):
    _ = importlib.import_module("core.models")
    Base.metadata.create_all(bind=engine)