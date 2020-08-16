from . import db


class Template(db.Model):
    __tablename__ = "templates"

    id = db.Column(db.BigInteger(), primary_key=True)
    text = db.Column(db.Unicode(), nullable=False)
