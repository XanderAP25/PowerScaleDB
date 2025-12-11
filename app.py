from flask import Flask, render_template, request, redirect, url_for
from models import db, Verse, Character, Key, Hax
from sqlalchemy import func

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/powerscale.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ---------------------------
# POWER STATS DEFINITIONS
# ---------------------------

AP_OPTIONS = [
    "Below Average Human", "Human", "Athlete",
    "Street", "Wall", "Small Building", "Building",
    "Large Building", "City Block", "Multi-City Block",
    "Small Town", "Town", "Large Town",
    "Small City", "City",
    "Mountain", "Large Mountain",
    "Island", "Large Island", "Small Country",
    "Country", "Large Country", "Contintent",
    "Multi-Continent", "Moon", "Small Planet",
    "Planet", "Large Planet", "Brown Dwarf",
    "Small Star", "Star", "Large Star",
    "Solar System", "Multi-Solar System", "Galaxy",
    "Multi-Galaxy", "Universe", "High Universe",
    "Universe+", "Low Multiverse", "Multiverse", "Multiverse+",
    "Low Complex Multiverse", "Complex Multiverse", "High Complex Multiverse",
    "Hyperverse", "High Hyperverse", "Low Outerverse", "Outerverse", "High Outerverse",
    "Boundless"
]

TIER_OPTIONS = [
    "10-C","10-B","10-A",
    "9-C","9-B","9-A",
    "8-C", "High 8-C", "8-B", "8-A",
    "Low 7-C", "7-C", "High 7-C",
    "Low 7-B", "7-B",
    "7-A","High 7-A",
    "6-C", "High 6-C", "Low 6-B",
    "6-B", "High 6-B", "6-A",
    "High 6-A",
    "5-C","Low 5-B","5-B","5-A","High 5-A"
    "Low 4-C", "4-C","High 4-C", "4-B","4-A",
    "3-C","3-B","3-A", "High 3-A",
    "Low 2-C", "2-C","2-B","2-A",
    "Low 1-C", "1-C","High 1-C","1-B","High 1-B",
    "Low 1-A","1-A","High 1-A","0"
]

SPEED_OPTIONS = [
    "Below Average",
    "Subsonic",
    "Subsonic+",
    "Supersonic",
    "Supersonic+",
    "Hypersonic",
    "High Hypersonic",
    "Massively Hypersonic",
    "MHS+",
    "Sub-Relativistic",
    "Relativistic",
    "Relativistic+",
    "FTL",
    "FTL+",
    "Massively FTL",
    "Massively FTL+",
    "Immeasurable"
]

DURABILITY_OPTIONS = AP_OPTIONS[:]  # Match AP scale 1:1

AP_TO_TIER = dict(zip(AP_OPTIONS, TIER_OPTIONS))

def tier_from_ap(ap_value):
    return AP_TO_TIER.get(ap_value, "Unknown")


# ---------------------------
# INITIALIZE DB
# ---------------------------
with app.app_context():
    db.create_all()


# ---------------------------
# ROUTES
# ---------------------------

@app.route("/")
def index():
    characters = Character.query.order_by(Character.name).all()
    return render_template("character_list.html", characters=characters)


# ---------------------------
# ADD VERSE
# ---------------------------
@app.route("/add_verse", methods=["GET", "POST"])
def add_verse():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return render_template("verse_form.html", error="Verse name cannot be empty.")

        # prevent duplicates
        existing = Verse.query.filter_by(name=name).first()
        if existing:
            return render_template("verse_form.html", error="Verse already exists.")

        new_verse = Verse(name=name)
        db.session.add(new_verse)
        db.session.commit()

        return redirect(url_for("add_character"))

    return render_template("verse_form.html")



# ---------------------------
# ADD CHARACTER
# ---------------------------
@app.route("/add", methods=["GET", "POST"])
def add_character():
    verses = Verse.query.order_by(Verse.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        verse_id = request.form.get("verse_id")
        new_verse_name = request.form.get("new_verse", "").strip()

        if not name:
            return redirect(url_for("index"))

        # 1. Handle new verse creation
        if new_verse_name:
            existing = Verse.query.filter_by(name=new_verse_name).first()
            if existing:
                verse_id = existing.id
            else:
                new_verse = Verse(name=new_verse_name)
                db.session.add(new_verse)
                db.session.commit()
                verse_id = new_verse.id

        # 2. If still no verse, reject
        if not verse_id:
            return render_template("character_form.html", verses=verses,
                                   error="Select an existing verse or create a new one.")

        # Create character
        new_char = Character(name=name, verse_id=int(verse_id))
        db.session.add(new_char)
        db.session.commit()

        # Optional Key Creation
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
                    obj = Hax(name=h)
                    db.session.add(obj)
                hax_objects.append(obj)

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
            db.session.commit()

        return redirect(url_for("character_detail", char_id=new_char.id))

    # GET request: supply dropdown data
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



# ---------------------------
# CHARACTER DETAIL
# ---------------------------
@app.route("/character/<int:char_id>")
def character_detail(char_id):
    character = Character.query.get_or_404(char_id)
    return render_template("character_detail.html", character=character)


# ---------------------------
# ADD KEY (WITH MULTI-SELECT HAX)
# ---------------------------
@app.route("/character/<int:char_id>/add_key", methods=["GET", "POST"])
def add_key(char_id):
    character = Character.query.get_or_404(char_id)

    if request.method == "POST":
        key_name = request.form.get("key_name", "").strip()
        ap = request.form.get("ap", "").strip()
        speed = request.form.get("speed", "").strip()
        durability = request.form.get("durability", "").strip()
        notes = request.form.get("notes", "").strip()

        if not key_name or not ap:
            # bare minimum sanity: need a name and AP
            return redirect(url_for("character_detail", char_id=char_id))

        tier = tier_from_ap(ap)  # AP → Tier mapping

        # Multi-select hax from Select2
        raw_hax = request.form.getlist("hax_list")
        hax_objects = []
        for h in raw_hax:
            if h.isdigit():
                obj = Hax.query.get(int(h))
            else:
                obj = Hax(name=h)
                db.session.add(obj)
            if obj is not None:
                hax_objects.append(obj)

        new_key = Key(
            character_id=char_id,
            key_name=key_name,
            ap=ap,
            tier=tier,
            durability=durability or ap,  # default durability to AP if empty
            speed=speed,
            notes=notes,
            hax=hax_objects,
        )

        db.session.add(new_key)
        db.session.commit()

        return redirect(url_for("character_detail", char_id=char_id))

    all_hax = Hax.query.order_by(Hax.name).all()

    return render_template(
        "key_form.html",
        character=character,
        AP=AP_OPTIONS,
        durs=DURABILITY_OPTIONS,
        speeds=SPEED_OPTIONS,
        tiers=TIER_OPTIONS,
        all_hax=all_hax,
        ap_to_tier=AP_TO_TIER,
    )



# ---------------------------
# SHOW ALL KEYS
# ---------------------------
@app.route("/keys")
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


# ---------------------------
# VERSE DETAIL PAGE
# ---------------------------
@app.route("/verse/<int:verse_id>")
def verse_detail(verse_id):
    verse = Verse.query.get_or_404(verse_id)

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
        .filter(Verse.id == verse_id)
        .group_by(Key.id)
        .order_by(Character.name, Key.key_name)
        .all()
    )

    return render_template("verse_detail.html", verse=verse, keys=keys)



# ---------------------------
# LIST ALL HAX
# ---------------------------
@app.route("/hax")
def hax_list():
    hax = Hax.query.order_by(Hax.name).all()
    return render_template("hax_list.html", hax=hax)


# ---------------------------
# ADD HAX MANUALLY
# ---------------------------
@app.route("/hax/add", methods=["GET", "POST"])
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

        return redirect(url_for("hax_list"))

    return render_template("hax_form.html")


# ---------------------------
# VERSE LIST PAGE
# ---------------------------
@app.route("/verses")
def verses_list():
    verses = Verse.query.order_by(Verse.name).all()
    return render_template("verse_list.html", verses=verses)


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
