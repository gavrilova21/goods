import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

meta = sa.MetaData()
Base = declarative_base(metadata=meta)


class Users(Base):
    __tablename__ = "user"
    user_id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)
    first_name = sa.Column(sa.String, nullable=True)
    last_name = sa.Column(sa.String, nullable=True)


class Tokens(Base):
    __tablename__ = "token"
    id = sa.Column(sa.Integer, primary_key=True)
    access_token = sa.Column(sa.String, nullable=False, unique=True)
    refresh_token = sa.Column(sa.String, nullable=False)
    exp_date = sa.Column(sa.String, nullable=False)


def row_to_dict(table, row: dict) -> dict:
    fields = table.columns.keys()
    data = {}
    for field in fields:
        if field == "password":
            continue
        data[field] = row[field]
    return data
