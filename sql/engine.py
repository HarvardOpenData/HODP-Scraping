import os
import typing as T

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists
from sql.models import Base


def init_session(
        db_name: str,
        local: bool = False,
        url: sqlalchemy.engine.url.URL = None):
    """Initializes a connection to Cloud SQL

        Parameters:
            db_name: name of the database to create a session for.
            local: option for local testing with the Cloud SQL proxy.
            url: custom url to initialize mysql on. Only works when in
            local mode.

        Returns:
            sqlalchemy Session
    """
    connection_name, db_user, db_pass = _get_db_credentials()
    if local:
        url = sqlalchemy.engine.url.URL(
            drivername='mysql+pymysql',
            username=db_user,
            password=db_pass,
            database=db_name,
            host='localhost'
        ) if url is None else url
    else:
        url = sqlalchemy.engine.url.URL(
            drivername='mysql+pymysql',
            username=db_user,
            password=db_pass,
            database=db_name,
            query={
                f'unix_socket': '/cloudsql/{connection_name}'
            }
        )

    engine = sqlalchemy.create_engine(url, echo=True)

    if not database_exists(engine.url):
        create_database(engine.url)

    Session = sessionmaker(bind=engine, autoflush=True)
    Base.metadata.create_all(engine)

    return Session()


def _get_db_credentials(
        keys: T.Tuple[str, str, str] = (
            'CLOUD_SQL_CONNECTION_NAME', 'DB_USER', 'DB_PASS')
) -> T.Tuple[str, str, str]:
    connection_name, user, password = keys
    try:
        connection_name = os.environ[connection_name]
        user = os.environ[user]
        password = os.environ[password]

    except KeyError:
        raise Exception(
            "_get_db_credentials: failed to get db credentials. Did you set them as environment variables? 🐨")

    return connection_name, user, password
