from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Verse, Character, Key, Hax
from .powerstats import (
    AP_OPTIONS, TIER_OPTIONS, SPEED_OPTIONS,
    DURABILITY_OPTIONS, AP_TO_TIER, tier_from_ap
)
from sqlalchemy import func
from app.utils.ranking import assign_rank, resequence_ranks, show_one_key
from sqlalchemy.exc import IntegrityError


bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    characters = Character.query.order_by(Character.name).all()
    return render_template("character_list.html", characters=characters)

# Add Verse

@bp.route("/add_verse", methods=["GET", "POST"])
def add_verse():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return render_template("verse_form.html", error="Verse name cannot be empty.")

        existing = Verse.query.filter_by(name=name).first()
        if existing:
            return render_template("verse_form.html", error="Verse already exists.")

        new_verse = Verse(name=name)
        db.session.add(new_verse)
        db.session.commit()

        return redirect(url_for("main.add_character"))

    return render_template("verse_form.html")

# Add Character

@bp.route("/add", methods=["GET", "POST"])
def add_character():
    verses = Verse.query.order_by(Verse.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        verse_id = request.form.get("verse_id")
        new_verse_name = request.form.get("new_verse", "").strip()

        if not name:
            return redirect(url_for("main.index"))

        if new_verse_name:
            existing = Verse.query.filter_by(name=new_verse_name).first()
            if existing:
                verse_id = existing.id
            else:
                new_verse = Verse(name=new_verse_name)
                db.session.add(new_verse)
                db.session.commit()
                verse_id = new_verse.id

        if not verse_id:
            return render_template("character_form.html", verses=verses,
                                   error="Select an existing verse or create a new one.")

        new_char = Character(name=name, verse_id=int(verse_id))
        db.session.add(new_char)
        db.session.commit()

        key_name = request.form.get("key_name", "").strip()
        ap = request.form.get("ap", "").strip()

        if key_name and ap:
            tier = tier_from_ap(ap)
            speed = request.form.get("speed", "")
            durability = request.form.get("durability", ap)
            notes = request.form.get("notes", "")

            raw_hax = request.form.getlist("hax_list")
            hax_objects = []

            for h in raw_hax:
                if h.isdigit():
                    obj = Hax.query.get(int(h))
                else:
                    obj = Hax.query.filter_by(name=h).first()
                    if not obj:
                        obj = Hax(name=h)
                        db.session.add(obj)
                hax_objects.append(obj)

        rank = request.form.get("rank")

        new_key = Key(
            character_id=new_char.id,
            key_name=key_name,
            ap=ap,
            tier=tier,
            speed=speed,
            durability=durability,
            notes=notes,
            hax=hax_objects
        )

        db.session.add(new_key)
        db.session.flush()  # REQUIRED so new_key.id exists

        if rank:
            assign_rank(new_key, new_char.verse_id, int(rank))

        db.session.commit()


        return redirect(url_for("main.character_detail", char_id=new_char.id))

    all_hax = Hax.query.order_by(Hax.name).all()

    return render_template(
        "character_form.html",
        verses=verses,
        AP=AP_OPTIONS,
        tiers=TIER_OPTIONS,
        speeds=SPEED_OPTIONS,
        durs=DURABILITY_OPTIONS,
        all_hax=all_hax,
        ap_to_tier=AP_TO_TIER
    )

# Character Detail Table

@bp.route("/character/<int:char_id>")
def character_detail(char_id):
    character = Character.query.get_or_404(char_id)
    return render_template("character_detail.html", character=character)

# Add Key

@bp.route("/character/<int:char_id>/add_key", methods=["GET","POST"])
def add_key(char_id):
    character = Character.query.get_or_404(char_id)

    if request.method == "POST":
        key_name = request.form.get("key_name", "").strip()
        ap = request.form.get("ap", "").strip()
        speed = request.form.get("speed", "").strip()
        durability = request.form.get("durability", "").strip()
        notes = request.form.get("notes", "").strip()

        if not key_name or not ap:
            return redirect(url_for("main.character_detail", char_id=char_id))

        tier = tier_from_ap(ap)

        raw_hax = request.form.getlist("hax_list")
        hax_objects = []

        for h in raw_hax:
            if h.isdigit():
                obj = Hax.query.get(int(h))
            else:
                obj = Hax.query.filter_by(name=h).first()
                if not obj:
                    obj = Hax(name=h)
                    db.session.add(obj)
            hax_objects.append(obj)

        rank = request.form.get("rank")

        new_key = Key(
            character_id=char_id,
            key_name=key_name,
            ap=ap,
            tier=tier,
            durability=durability or ap,
            speed=speed,
            notes=notes,
            hax=hax_objects,
        )

        db.session.add(new_key)
        db.session.flush()  # gives new_key.id

        if rank:
            assign_rank(new_key, character.verse_id, rank)

        db.session.commit()

        return redirect(url_for("main.character_detail", char_id=char_id))

    all_hax = Hax.query.order_by(Hax.name).all()

    return render_template(
        "key_form.html",
        character=character,
        AP=AP_OPTIONS,
        durs=DURABILITY_OPTIONS,
        speeds=SPEED_OPTIONS,
        tiers=TIER_OPTIONS,
        all_hax=all_hax,
        ap_to_tier=AP_TO_TIER
    )

# Show all keys

@bp.route("/keys")
def all_keys():
    keys = (
        db.session.query(
            Key.id,
            Key.key_name,
            Key.ap,
            Key.tier,
            Key.speed,
            Key.durability,
            Character.name.label("character"),
            Verse.name.label("verse"),
            func.group_concat(Hax.name, ", ").label("hax_list")
        )
        .select_from(Key)
        .join(Character, Key.character_id == Character.id)
        .join(Verse, Character.verse_id == Verse.id)
        .outerjoin(Key.hax)
        .group_by(Key.id)
        .order_by(Verse.name, Character.name)
        .all()
    )

    return render_template("keys_all.html", keys=keys)

# Show keys within a verse

@bp.route("/verse/<int:verse_id>")
def verse_detail(verse_id):
    verse = Verse.query.get_or_404(verse_id)
    single = request.args.get("single") == "1"

    if single:
        keys = show_one_key(verse_id)
    else:
        keys = (
            Key.query
            .join(Character)
            .filter(Character.verse_id == verse_id)
            .options(
                db.joinedload(Key.character),
                db.joinedload(Key.hax)
            )
            .order_by(Key.rank.asc().nullslast(), Character.name)
            .all()
        )




    return render_template(
        "verse_detail.html",
        verse=verse,
        keys=keys,
        single=single
    )


# Hax list

@bp.route("/hax")
def hax_list():
    hax = Hax.query.order_by(Hax.name).all()
    return render_template("hax_list.html", hax=hax)

# Add Hax

@bp.route("/hax/add", methods=["GET", "POST"])
def add_hax():
    if request.method == "POST":
        name = request.form.get("name", "").strip()

        if not name:
            return render_template("hax_form.html", error="Hax name cannot be empty.")

        existing = Hax.query.filter_by(name=name).first()
        if existing:
            return render_template("hax_form.html", error="Hax already exists.")

        new_hax = Hax(name=name)
        db.session.add(new_hax)
        db.session.commit()

        return redirect(url_for("main.hax_list"))

    return render_template("hax_form.html")

# Show verses

@bp.route("/verses")
def verses_list():
    verses = Verse.query.order_by(Verse.name).all()
    return render_template("verse_list.html", verses=verses)

# DELETION FUNCTIONS

@bp.route("/character/<int:char_id>/delete", methods=["POST"])
def delete_character(char_id):
    character = Character.query.get_or_404(char_id)

    db.session.delete(character)
    db.session.commit()

    return redirect(url_for("main.index"))

@bp.route("/key/<int:key_id>/delete", methods=["POST"])
def delete_key(key_id):
    key = Key.query.get_or_404(key_id)
    verse_id = key.character.verse_id
    old_rank = key.rank

    db.session.delete(key)

    if old_rank is not None:
        keys_to_shift = (
            Key.query
            .join(Character)
            .filter(
                Character.verse_id == verse_id,
                Key.rank.isnot(None),
                Key.rank > old_rank
            )
            .all()
        )

        for k in keys_to_shift:
            k.rank -= 1

    db.session.commit()
    return redirect(url_for("main.character_detail", char_id=key.character_id))


@bp.route("/hax/<int:hax_id>/delete", methods=["POST"])
def delete_hax(hax_id):
    hax = Hax.query.get_or_404(hax_id)

    db.session.delete(hax)
    db.session.commit()

    return redirect(url_for("main.hax_list"))

@bp.route("/verse/<int:verse_id>/delete", methods=["POST"])
def delete_verse(verse_id):
    verse = Verse.query.get_or_404(verse_id)

    db.session.delete(verse)
    db.session.commit()

    return redirect(url_for("main.verses_list"))

# EDIT FUNCTIONS

@bp.route("/character/<int:char_id>/edit", methods=["GET", "POST"])
def edit_character(char_id):
    character = Character.query.get_or_404(char_id)
    verses = Verse.query.order_by(Verse.name).all()

    if request.method == "POST":
        character.name = request.form.get("name", "").strip()
        verse_id = request.form.get("verse_id")
        if verse_id:
            character.verse_id = int(verse_id)

        db.session.commit()
        return redirect(url_for("main.character_detail", char_id=char_id))

    return render_template(
        "edit_character.html",
        character=character,
        verses=verses
    )

@bp.route("/key/<int:key_id>/edit", methods=["GET", "POST"])
def edit_key(key_id):
    key = Key.query.get_or_404(key_id)
    character = key.character
    verse_id = character.verse_id

    if request.method == "POST":
        key.key_name = request.form.get("key_name", "").strip()

        ap = request.form.get("ap", "").strip()
        key.ap = ap
        key.tier = tier_from_ap(ap)

        key.speed = request.form.get("speed", "").strip()
        key.durability = request.form.get("durability", ap)
        key.notes = request.form.get("notes", "").strip()

        new_rank = request.form.get("rank")

        raw_hax = request.form.getlist("hax_list")
        hax_objects = []

        for h in raw_hax:
            if h.isdigit():
                obj = Hax.query.get(int(h))
            else:
                obj = Hax.query.filter_by(name=h).first()
                if not obj:
                    obj = Hax(name=h)
                    db.session.add(obj)
            hax_objects.append(obj)

        if new_rank:
            new_rank = int(new_rank)
            if new_rank != key.rank:
                assign_rank(key, verse_id, new_rank)
        else:
            key.rank = None

        key.hax = hax_objects

        db.session.commit()
        return redirect(url_for("main.character_detail", char_id=character.id))

    all_hax = Hax.query.order_by(Hax.name).all()

    return render_template(
        "edit_key.html",
        key=key,
        character=character,
        AP=AP_OPTIONS,
        durs=DURABILITY_OPTIONS,
        speeds=SPEED_OPTIONS,
        tiers=TIER_OPTIONS,
        all_hax=all_hax,
        ap_to_tier=AP_TO_TIER
    )

@bp.route("/verse/<int:verse_id>/edit", methods=["GET", "POST"])
def edit_verse(verse_id):
    verse = Verse.query.get_or_404(verse_id)

    if request.method == "POST":
        new_name = request.form.get("name", "").strip()
        if new_name:
            verse.name = new_name
            db.session.commit()
        return redirect(url_for("main.verse_detail", verse_id=verse_id))

    return render_template("edit_verse.html", verse=verse)

@bp.route("/hax/<int:hax_id>/edit", methods=["GET", "POST"])
def edit_hax(hax_id):
    h = Hax.query.get_or_404(hax_id)

    if request.method == "POST":
        new_name = request.form.get("name", "").strip()

        if new_name:
            h.name = new_name
            db.session.commit()

        return redirect(url_for("main.hax_list"))

    return render_template("edit_hax.html", hax=h)

# Compare keys

@bp.route("/compare", methods=["GET", "POST"])
def compare_keys():
    # Fetch all keys for dropdowns
    keys = (
        db.session.query(
            Key.id,
            Key.key_name,
            Character.name.label("character"),
            Verse.name.label("verse")
        )
        .select_from(Key)
        .join(Character, Key.character_id == Character.id)
        .join(Verse, Character.verse_id == Verse.id)
        .order_by(Verse.name, Character.name, Key.key_name)
        .all()
    )


    key_a = None
    key_b = None
    error = None

    if request.method == "POST":
        key_a_id = request.form.get("key_a")
        key_b_id = request.form.get("key_b")

        if not key_a_id or not key_b_id:
            error = "Select two keys to compare."
        elif key_a_id == key_b_id:
            error = "You must select two different keys."
        else:
            key_a = Key.query.get(key_a_id)
            key_b = Key.query.get(key_b_id)

            if not key_a or not key_b:
                error = "One or both keys could not be found."

    return render_template(
        "compare_keys.html",
        keys=keys,
        key_a=key_a,
        key_b=key_b,
        error=error
    )

# Prefill key

@bp.route("/key/<int:key_id>/prefill")
def prefill_key(key_id):
    key = Key.query.get_or_404(key_id)

    return {
        "ap": key.ap,
        "tier": key.tier,
        "durability": key.durability,
        "speed": key.speed,
        "notes": key.notes,
        "hax": [
            {"id": h.id, "name": h.name}
            for h in key.hax
        ]
    }

# resequence ranks

@bp.route("/verse/<int:verse_id>/resequence", methods=["POST"])
def resequence_verse(verse_id):
    verse = Verse.query.get_or_404(verse_id)

    resequence_ranks(verse.id)
    db.session.commit()

    return redirect(url_for("main.verse_detail", verse_id=verse.id))
