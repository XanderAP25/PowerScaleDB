from sqlalchemy import func
from app.models import db, Key, Character

def assign_rank(key, verse_id, new_rank):
    if new_rank is None:
        key.rank = None
        return

    new_rank = int(new_rank)

    keys_to_shift = (
        Key.query
        .join(Character)
        .filter(
            Character.verse_id == verse_id,
            Key.rank.isnot(None),
            Key.rank >= new_rank,
            Key.id != key.id
        )
        .order_by(Key.rank.desc())  # IMPORTANT
        .all()
    )

    for k in keys_to_shift:
        k.rank += 1

    key.rank = new_rank

def resequence_ranks(verse_id):
    keys = (
        Key.query
        .join(Character)
        .filter(
            Character.verse_id == verse_id,
            Key.rank.isnot(None)
        )
        .order_by(Key.rank.asc())
        .all()
    )

    for idx, key in enumerate(keys, start=1):
        key.rank = idx

def show_one_key(verse_id):
    subquery = (
        db.session.query(
            Key.character_id,
            func.min(Key.rank).label("best_rank")
        )
        .join(Character)
        .filter(
            Character.verse_id == verse_id,
            Key.rank.isnot(None)
        )
        .group_by(Key.character_id)
        .subquery()
    )

    keys = (
        db.session.query(Key)
        .join(
            subquery,
            (Key.character_id == subquery.c.character_id) &
            (Key.rank == subquery.c.best_rank)
        )
        .order_by(Key.rank.asc())
        .all()
    )

    return keys