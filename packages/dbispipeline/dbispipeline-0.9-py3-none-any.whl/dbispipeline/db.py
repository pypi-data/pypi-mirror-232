"""Module containing DB connectors."""
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from .utils import LOGGER
from .utils import load_project_config

Base = declarative_base()


class ClassProperty(object):
    """Wrapper to annotate functions as classpropertyies."""

    def __init__(self, fget):
        """Initializes the wrapper."""
        self.fget = fget

    def __get__(self, cls, owner):
        """Handles the getter."""
        return self.fget.__get__(None, owner)()


class DB():
    """Database connector class."""

    _config = None
    _engine = None
    _session = None

    @ClassProperty
    @classmethod
    def engine(cls):
        """Engine property."""
        if cls._engine is None:
            try:
                cls._engine = create_engine(
                    cls._db_connection_uri(),
                    pool_pre_ping=True,
                )
            except ModuleNotFoundError as e:
                LOGGER.error(
                    'Could not establish DB connection. If you are using a '
                    'database other than SQLite, you might need to install an '
                    'additional package. The original exception was: '
                )
                raise e
            LOGGER.debug('connecting to database')
            Base.metadata.create_all(cls._engine)
            LOGGER.debug('connection established')
        return cls._engine

    @ClassProperty
    @classmethod
    def session(cls):
        """Session property."""
        if cls._session is None:
            cls._session = sessionmaker()
            cls._session.configure(bind=cls.engine)
        return cls._session

    @classmethod
    def _db_connection_uri(cls):
        if cls._config is None:
            cls._config = load_project_config()

        db_conf = cls._config['database']

        if 'url' in db_conf:
            return db_conf['url']

        driver = db_conf.get('driver', 'postgresql')

        host = db_conf.get('host', 'localhost')
        port = db_conf.get('port', 5432)
        user = db_conf.get('user','postgresql')
        database = db_conf.get('database', 'dbispipeline')
        password = db_conf.get('password', None)



        db_uri = URL.create(drivername=driver,
                     username=user,
                     password=password,
                     host=host,
                     port=port,
                     database=database)
        LOGGER.debug("connecting to db: %s://%s", driver, host)
        return db_uri


class DbModel(Base):
    """Model used to store the results in the db."""

    @declared_attr
    def __tablename__(cls):  # noqa N805
        try:
            config = load_project_config()
            return config['database']['result_table']
        except KeyError:
            return 'results'

    id = Column(Integer, primary_key=True)  # noqa: A003
    project_name = Column(String)
    date = Column(DateTime, default=func.now())
    git_commit_id = Column(String)
    git_remote_url = Column(String)
    git_is_dirty = Column(Boolean)
    sourcefile = Column(String)
    config = Column(String)
    dataloader = Column(JSON)
    pipeline = Column(JSON)
    evaluator = Column(JSON)
    outcome = Column(JSON)
    platform = Column(JSON)
    requirements = Column(JSON)
