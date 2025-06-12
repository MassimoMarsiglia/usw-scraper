import os
import requests
import enum
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Enum,
    ForeignKey,
    Table,
    Text,
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

# --- Database Schema Definition ---
Base = declarative_base()

# Association Tables for Many-to-Many relationships
skin_collections_table = Table(
    "skin_collections",
    Base.metadata,
    Column("skin_id", String, ForeignKey("skins.id"), primary_key=True),
    Column("collection_id", String, ForeignKey("collections.id"), primary_key=True),
)

skin_crates_table = Table(
    "skin_crates",
    Base.metadata,
    Column("skin_id", String, ForeignKey("skins.id"), primary_key=True),
    Column("crate_id", String, ForeignKey("crates.id"), primary_key=True),
)

sticker_crates_table = Table(
    "sticker_crates",
    Base.metadata,
    Column("sticker_id", String, ForeignKey("stickers.id"), primary_key=True),
    Column("crate_id", String, ForeignKey("crates.id"), primary_key=True),
)

agent_collections_table = Table(
    "agent_collections",
    Base.metadata,
    Column("agent_id", String, ForeignKey("agents.id"), primary_key=True),
    Column("collection_id", String, ForeignKey("collections.id"), primary_key=True),
)

skin_wears_table = Table(
    "skin_wears",
    Base.metadata,
    Column("skin_id", String, ForeignKey("skins.id"), primary_key=True),
    Column("wear_id", String, ForeignKey("wears.id"), primary_key=True),
)

# --- Normalized Tables ---

class Rarity(Base):
    __tablename__ = "rarities"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    color = Column(String)

class Weapon(Base):
    __tablename__ = "weapons"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

class Pattern(Base):
    __tablename__ = "patterns"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

class Wear(Base):
    __tablename__ = "wears"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

class Team(Base):
    __tablename__ = "teams"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

class Category(Base):
    __tablename__ = "categories"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

class Style(Base):
    __tablename__ = "styles"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String)

class TournamentEvent(Base):
    __tablename__ = "tournament_events"
    name = Column(String, primary_key=True)

class TournamentTeam(Base):
    __tablename__ = "tournament_teams"
    name = Column(String, primary_key=True)

class StickerEffect(Base):
    __tablename__ = "sticker_effects"
    name = Column(String, primary_key=True)

class StickerType(Base):
    __tablename__ = "sticker_types"
    name = Column(String, primary_key=True)


# --- Main Item Tables ---

class Skin(Base):
    __tablename__ = "skins"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    weapon_id = Column(String, ForeignKey("weapons.id"))
    pattern_id = Column(String, ForeignKey("patterns.id"))
    min_float = Column(Float)
    max_float = Column(Float)
    rarity_id = Column(String, ForeignKey("rarities.id"))
    stattrak = Column(Boolean)
    souvenir = Column(Boolean)
    paint_index = Column(String)
    team_id = Column(String, ForeignKey("teams.id"))
    image = Column(String)

    weapon = relationship("Weapon")
    pattern = relationship("Pattern")
    rarity = relationship("Rarity")
    team = relationship("Team")
    wears = relationship("Wear", secondary=skin_wears_table)
    collections = relationship("Collection", secondary=skin_collections_table, back_populates="skins")
    crates = relationship("Crate", secondary=skin_crates_table, back_populates="skins")
    variants = relationship("SkinVariant", back_populates="skin")

class SkinVariant(Base):
    __tablename__ = "skin_variants"
    id = Column(String, primary_key=True)
    skin_id = Column(String, ForeignKey("skins.id"))
    name = Column(String, nullable=False)
    # Remove description - inherit from skin
    weapon_id = Column(String, ForeignKey("weapons.id"))
    category_id = Column(String, ForeignKey("categories.id"))
    pattern_id = Column(String, ForeignKey("patterns.id"))
    min_float = Column(Float)  # Keep - specific to variant
    max_float = Column(Float)  # Keep - specific to variant
    wear_id = Column(String, ForeignKey("wears.id"))
    stattrak = Column(Boolean)
    souvenir = Column(Boolean)
    paint_index = Column(String)
    rarity_id = Column(String, ForeignKey("rarities.id"))
    market_hash_name = Column(String)
    team_id = Column(String, ForeignKey("teams.id"))
    style_id = Column(Integer, ForeignKey("styles.id"))
    legacy_model = Column(Boolean)
    image = Column(String)

    skin = relationship("Skin", back_populates="variants")
    weapon = relationship("Weapon")
    category = relationship("Category")
    pattern = relationship("Pattern")
    wear = relationship("Wear")
    rarity = relationship("Rarity")
    team = relationship("Team")
    style = relationship("Style")

class Sticker(Base):
    __tablename__ = "stickers"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    rarity_id = Column(String, ForeignKey("rarities.id"))
    tournament_event_name = Column(String, ForeignKey("tournament_events.name"))
    tournament_team_name = Column(String, ForeignKey("tournament_teams.name"))
    type_name = Column(String, ForeignKey("sticker_types.name"))
    effect_name = Column(String, ForeignKey("sticker_effects.name"))
    market_hash_name = Column(String)
    image = Column(String)
    
    rarity = relationship("Rarity")
    tournament_event = relationship("TournamentEvent")
    tournament_team = relationship("TournamentTeam")
    type = relationship("StickerType")
    effect = relationship("StickerEffect")
    crates = relationship("Crate", secondary=sticker_crates_table, back_populates="stickers")

class Keychain(Base):
    __tablename__ = "keychains"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    rarity_id = Column(String, ForeignKey("rarities.id"))
    market_hash_name = Column(String)
    image = Column(String)

    rarity = relationship("Rarity")

class Collection(Base):
    __tablename__ = "collections"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    image = Column(String)

    skins = relationship("Skin", secondary=skin_collections_table, back_populates="collections")
    agents = relationship("Agent", secondary=agent_collections_table, back_populates="collections")

class Crate(Base):
    __tablename__ = "crates"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String)
    market_hash_name = Column(String)
    image = Column(String)
    rental = Column(Boolean, default=False)

    skins = relationship("Skin", secondary=skin_crates_table, back_populates="crates")
    stickers = relationship("Sticker", secondary=sticker_crates_table, back_populates="crates")

class Key(Base):
    __tablename__ = "keys"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    market_hash_name = Column(String)
    image = Column(String)

class Collectible(Base):
    __tablename__ = "collectibles"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    rarity_id = Column(String, ForeignKey("rarities.id"))
    image = Column(String)
    genuine = Column(Boolean, default=False)
    type = Column(String)
    market_hash_name = Column(String)
    
    rarity = relationship("Rarity")

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    rarity_id = Column(String, ForeignKey("rarities.id"))
    team_id = Column(String, ForeignKey("teams.id"))
    image = Column(String)
    market_hash_name = Column(String)
    
    rarity = relationship("Rarity")
    team = relationship("Team")
    collections = relationship("Collection", secondary=agent_collections_table, back_populates="agents")

class Patch(Base):
    __tablename__ = "patches"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    rarity_id = Column(String, ForeignKey("rarities.id"))
    image = Column(String)
    market_hash_name = Column(String)
    
    rarity = relationship("Rarity")

class Graffiti(Base):
    __tablename__ = "graffiti"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    rarity_id = Column(String, ForeignKey("rarities.id"))
    image = Column(String)
    market_hash_name = Column(String)
    
    rarity = relationship("Rarity")

class MusicKit(Base):
    __tablename__ = "music_kits"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    rarity_id = Column(String, ForeignKey("rarities.id"))
    image = Column(String)
    market_hash_name = Column(String)
    exclusive = Column(Boolean, default=False)

    rarity = relationship("Rarity")

class BaseWeapon(Base):
    __tablename__ = "base_weapons"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    image = Column(String)

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

def populate_database(session):
    """Fetches data from all endpoints and populates the database."""
    
    print("Starting data population... This may take a moment.")

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
    DB_PATH = f"sqlite:///../../{DB_NAME}"
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
