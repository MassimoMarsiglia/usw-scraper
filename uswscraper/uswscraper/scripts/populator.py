import os
import sys
import requests
import enum
from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import sessionmaker

# Fix imports - use absolute imports with path setup
# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Now use absolute imports
from uswscraper.uswscraper.models.CS2_items import Agent, BaseWeapon, Category, Collectible, Collection, Crate, Graffiti, Key, Keychain, MusicKit, Patch, Pattern, Rarity, Skin, SkinVariant, Sticker, StickerEffect, StickerType, Style, Team, TournamentEvent, TournamentTeam, Weapon, Wear
from uswscraper.uswscraper.database.database import Base

# --- Data Population Logic ---

API_BASE_URL = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/"

def get_json_data(endpoint):
    """Fetches JSON data from a given API endpoint."""
    try:
        print(f"Fetching data from {endpoint}...")
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {endpoint}: {e}")
        return None

def populate_rarities(session):
    """Pre-populate all rarity types to avoid foreign key violations."""
    print("Pre-populating rarities...")
    
    # Define all common CS2 rarities
    rarities = [
        {"id": "rarity_ancient", "name": "Ancient", "color": "#eb4b4b"},
        {"id": "rarity_ancient_weapon", "name": "Ancient", "color": "#eb4b4b"}, 
        {"id": "rarity_common", "name": "Common", "color": "#b0c3d9"},
        {"id": "rarity_common_weapon", "name": "Consumer Grade", "color": "#b0c3d9"},
        {"id": "rarity_contraband", "name": "Contraband", "color": "#e4ae39"},
        {"id": "rarity_default", "name": "Default", "color": "#000000"},
        {"id": "rarity_immortal", "name": "Immortal", "color": "#8847ff"},
        {"id": "rarity_legendary", "name": "Legendary", "color": "#d32ce6"},
        {"id": "rarity_mythical", "name": "Mythical", "color": "#8847ff"},
        {"id": "rarity_mythical_weapon", "name": "Classified", "color": "#d32ce6"},
        {"id": "rarity_rare", "name": "Rare", "color": "#4b69ff"},
        {"id": "rarity_rare_weapon", "name": "Restricted", "color": "#8847ff"},
        {"id": "rarity_uncommon", "name": "Uncommon", "color": "#5e98d9"},
        {"id": "rarity_uncommon_weapon", "name": "Mil-Spec Grade", "color": "#4b69ff"},
        # Additional agent-specific rarities
        {"id": "rarity_legendary_character", "name": "Master Agent", "color": "#d32ce6"},
        {"id": "rarity_mythical_character", "name": "Superior Agent", "color": "#8847ff"},
        {"id": "rarity_rare_character", "name": "Exceptional Agent", "color": "#4b69ff"},
        {"id": "rarity_uncommon_character", "name": "Distinguished Agent", "color": "#5e98d9"},
        # Other possible rarities that might be needed
        {"id": "rarity_ancient_character", "name": "Extraordinary Agent", "color": "#eb4b4b"},
        {"id": "rarity_common_character", "name": "Agent", "color": "#b0c3d9"}
    ]
    
    for rarity in rarities:
        session.merge(Rarity(**rarity))
    
    session.commit()
    print("Rarities pre-populated.")

def populate_database(session):
    """Fetches data from all endpoints and populates the database."""
    
    print("Starting data population... This may take a moment.")
    
    # First, pre-populate rarities to avoid foreign key violations
    populate_rarities(session)
    
    # Process fixed reference data tables first
    # Populate teams, patterns, categories, etc.
    reference_data = {
        "teams": Team,
        "patterns": Pattern,
        "wears": Wear,
        "categories": Category,
        "tournament_events": TournamentEvent,
        "tournament_teams": TournamentTeam,
        "sticker_effects": StickerEffect,
        "sticker_types": StickerType
    }
    
    # Extract and create all reference data from each endpoint first
    print("Pre-populating reference data...")
    for endpoint, model_class in [
        ("skins.json", ["weapon", "pattern", "team"]),
        ("stickers.json", ["tournament_event", "tournament_team", "effect", "type"]),
        ("skins_not_grouped.json", ["category", "style", "wear"])
    ]:
        data = get_json_data(endpoint)
        if data:
            for item in data:
                if not item:
                    continue
                    
                for ref_type in model_class:
                    if item.get(ref_type):
                        if ref_type == "weapon":
                            session.merge(Weapon(id=item[ref_type]['id'], name=item[ref_type]['name']))
                        elif ref_type == "pattern":
                            session.merge(Pattern(**item[ref_type]))
                        elif ref_type == "team":
                            session.merge(Team(**item[ref_type]))
                        elif ref_type == "category":
                            session.merge(Category(**item[ref_type]))
                        elif ref_type == "style":
                            session.merge(Style(**item[ref_type]))
                        elif ref_type == "wear":
                            session.merge(Wear(**item[ref_type]))
                        elif ref_type == "tournament_event":
                            session.merge(TournamentEvent(name=item[ref_type]))
                        elif ref_type == "tournament_team":
                            session.merge(TournamentTeam(name=item[ref_type]))
                        elif ref_type == "effect":
                            session.merge(StickerEffect(name=item[ref_type]))
                        elif ref_type == "type":
                            session.merge(StickerType(name=item[ref_type]))
    
    # Now commit all reference data before proceeding
    session.commit()
    print("Reference data pre-populated.")

    # Process Skins (Grouped)
    skins_data = get_json_data("skins.json")
    if skins_data:
        for item in skins_data:
            # Skip if item is None
            if not item:
                continue
                
            if item.get('rarity'): session.merge(Rarity(**item['rarity']))
            if item.get('weapon'): session.merge(Weapon(id=item['weapon']['id'], name=item['weapon']['name']))
            if item.get('pattern'): session.merge(Pattern(**item['pattern']))
            if item.get('team'): session.merge(Team(**item['team']))

            skin = session.get(Skin, item['id'])
            if not skin:
                skin = Skin(
                    id=item['id'], name=item['name'], description=item.get('description'),
                    weapon_id=item.get('weapon', {}).get('id') if item.get('weapon') else None,
                    pattern_id=item.get('pattern', {}).get('id') if item.get('pattern') else None,
                    min_float=item.get('min_float'), max_float=item.get('max_float'),
                    rarity_id=item.get('rarity', {}).get('id') if item.get('rarity') else None,
                    stattrak=item.get('stattrak'), souvenir=item.get('souvenir'),
                    paint_index=item.get('paint_index'),
                    team_id=item.get('team', {}).get('id') if item.get('team') else None,
                    image=item.get('image')
                )
                session.add(skin)  # Add skin to session immediately
            
            if item.get('wears'):
                for wear_data in item['wears']:
                    if wear_data:  # Check if wear_data is not None
                        wear_obj = session.merge(Wear(**wear_data))
                        if wear_obj not in skin.wears: skin.wears.append(wear_obj)

            if item.get('collections'):
                for coll_data in item['collections']:
                    if coll_data:  # Check if coll_data is not None
                        coll_obj = session.merge(Collection(id=coll_data['id'], name=coll_data['name'], image=coll_data.get('image')))
                        if coll_obj not in skin.collections: skin.collections.append(coll_obj)

            if item.get('crates'):
                for crate_data in item['crates']:
                    if crate_data:  # Check if crate_data is not None
                        crate_obj = session.merge(Crate(id=crate_data['id'], name=crate_data['name'], image=crate_data.get('image')))
                        if crate_obj not in skin.crates: skin.crates.append(crate_obj)

        session.commit()
        print("Skins (grouped) populated.")
    
    # Process Skin Variants (Not Grouped)
    skins_not_grouped_data = get_json_data("skins_not_grouped.json")
    if skins_not_grouped_data:
        for item in skins_not_grouped_data:
            # Skip if item is None
            if not item:
                continue
                
            if item.get('category'): session.merge(Category(**item['category']))
            if item.get('style'): session.merge(Style(**item['style']))
            if item.get('wear'): session.merge(Wear(**item['wear']))

            session.merge(SkinVariant(
                id=item['id'], skin_id=item.get('skin_id'), name=item['name'],
                weapon_id=item.get('weapon', {}).get('id') if item.get('weapon') else None,
                category_id=item.get('category', {}).get('id') if item.get('category') else None,
                pattern_id=item.get('pattern', {}).get('id') if item.get('pattern') else None,
                min_float=item.get('min_float'), max_float=item.get('max_float'),
                wear_id=item.get('wear', {}).get('id') if item.get('wear') else None,
                stattrak=item.get('stattrak'), souvenir=item.get('souvenir'),
                paint_index=item.get('paint_index'),
                rarity_id=item.get('rarity', {}).get('id') if item.get('rarity') else None,
                market_hash_name=item.get('market_hash_name'),
                team_id=item.get('team', {}).get('id') if item.get('team') else None,
                style_id=item.get('style', {}).get('id') if item.get('style') else None,
                legacy_model=item.get('legacy_model'), image=item.get('image')
            ))
        session.commit()
        print("Skin Variants (non-grouped) populated.")
    
    # Process Stickers (with proper normalization)
    stickers_data = get_json_data("stickers.json")
    if stickers_data:
        for item in stickers_data:
            # Skip if item is None
            if not item:
                continue
                
            # Add related normalized entities
            if item.get('rarity'): session.merge(Rarity(**item['rarity']))
            if item.get('tournament_event'): session.merge(TournamentEvent(name=item['tournament_event']))
            if item.get('tournament_team'): session.merge(TournamentTeam(name=item['tournament_team']))
            if item.get('effect'): session.merge(StickerEffect(name=item['effect']))
            if item.get('type'): session.merge(StickerType(name=item['type']))

            # Use merge instead of add to handle duplicates
            sticker = session.merge(Sticker(
                id=item['id'], name=item['name'], description=item.get('description'),
                rarity_id=item.get('rarity', {}).get('id') if item.get('rarity') else None,
                tournament_event_name=item.get('tournament_event'),
                tournament_team_name=item.get('tournament_team'),
                type_name=item.get('type'),
                effect_name=item.get('effect'),
                market_hash_name=item.get('market_hash_name'),
                image=item.get('image')
            ))

            if item.get('crates'):
                for crate_data in item['crates']:
                    if crate_data:
                        crate_obj = session.merge(Crate(id=crate_data['id'], name=crate_data['name'], image=crate_data.get('image')))
                        if crate_obj not in sticker.crates:
                            sticker.crates.append(crate_obj)
            
        session.commit()
        print("Stickers populated.")
    
    # Process remaining endpoints
    endpoints = {
        "keychains.json": Keychain, "collections.json": Collection, "crates.json": Crate, 
        "keys.json": Key, "collectibles.json": Collectible, "agents.json": Agent, 
        "patches.json": Patch, "graffiti.json": Graffiti, "music_kits.json": MusicKit, 
        "base_weapons.json": BaseWeapon
    }

    for endpoint, model in endpoints.items():
        data = get_json_data(endpoint)
        if data:
            for item in data:
                # Use pop to remove keys that are handled by relationships or not in the model
                rarity_data = item.pop('rarity', None)
                team_data = item.pop('team', None)
                item.pop('collections', None); item.pop('crates', None); item.pop('contains', None)
                item.pop('contains_rare', None); item.pop('loot_list', None)
                # Remove additional unsupported fields
                item.pop('first_sale_date', None)
                item.pop('tournament_event', None)
                item.pop('tournament_team', None)
                item.pop('effect', None)
                item.pop('type', None)
                item.pop('model_player', None)
                item.pop('special_notes', None)
                item.pop('marketable', None)
                
                # Add foreign keys back if they existed
                if rarity_data: item['rarity_id'] = rarity_data.get('id')
                if team_data: item['team_id'] = team_data.get('id')

                session.merge(model(**item))
            session.commit()
            print(f"{model.__tablename__.capitalize()} populated.")

from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    # url = os.getenv("DATABASE_URL", f"sqlite://../../{DB_FILE}")
    DB_NAME = os.getenv("DB_NAME", "cs2_items.db")
    # DB_PATH = f"sqlite:///../../{DB_NAME}"
    DB_PATH = "postgresql+psycopg2://citizix_user:S3cret@localhost:5433/citizix_db"
    print(f"Using database path: {DB_PATH}")
    engine = create_engine(url=DB_PATH)
    
    Base.metadata.create_all(engine)
    print(f"Database schema created in '{DB_NAME}'.")
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        populate_database(session)
        print("\nDatabase population complete!")
    except Exception as e:
        print(f"\nAn error occurred during population: {e}")
        session.rollback()
    finally:
        print("Closing database session.")
        session.close()
