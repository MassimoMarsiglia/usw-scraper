from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Table, Text
from ..database.database import Base
from sqlalchemy.orm import relationship

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