# app/powerstats.py

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
    "5-C","Low 5-B","5-B","5-A","High 5-A",
    "Low 4-C", "4-C","High 4-C", "4-B","4-A",
    "3-C","3-B","3-A", "High 3-A",
    "Low 2-C", "2-C","2-B","2-A",
    "Low 1-C", "1-C","High 1-C","1-B","High 1-B",
    "Low 1-A","1-A","High 1-A","0"
]

SPEED_OPTIONS = [
    "Below Human",
    "Human",
    "Athletic Human",
    "Peak Human",
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

DURABILITY_OPTIONS = AP_OPTIONS[:]  # identical scale

AP_TO_TIER = dict(zip(AP_OPTIONS, TIER_OPTIONS))

def tier_from_ap(ap_value):
    return AP_TO_TIER.get(ap_value, "Unknown")
