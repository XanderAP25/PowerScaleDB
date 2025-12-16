from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Verse(db.Model):
    __tablename__ = "verses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)

    characters = db.relationship("Character", backref="verse_obj", cascade="all, delete")


class Character(db.Model):
    __tablename__ = "characters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    verse_id = db.Column(db.Integer, db.ForeignKey("verses.id"), nullable=False)

    keys = db.relationship("Key", backref="character", cascade="all, delete")

key_hax_table = db.Table(
    "key_hax",
    db.Column("key_id", db.Integer, db.ForeignKey("keys.id"), primary_key=True),
    db.Column("hax_id", db.Integer, db.ForeignKey("hax.id"), primary_key=True)
)

class Hax(db.Model):
    __tablename__ = "hax"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)

class Key(db.Model):
    __tablename__ = "keys"

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), nullable=False)

    key_name = db.Column(db.String(200), nullable=False)

    ap = db.Column(db.String(200))
    tier = db.Column(db.String(200))
    durability = db.Column(db.String(200))
    speed = db.Column(db.String(200))
    rank = db.Column(db.Integer, nullable=True)

    notes = db.Column(db.String(2000))

    hax = db.relationship("Hax", secondary=key_hax_table, backref="keys")

    __table_args__ = (
        db.Index("ix_key_verse_rank", "rank"),
    )
