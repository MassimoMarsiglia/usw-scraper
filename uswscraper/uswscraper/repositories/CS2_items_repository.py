from sqlalchemy.orm import Session, selectinload
from ..models.CS2_items import SkinVariant, Skin, Sticker, Agent, Crate, Keychain

class CS2ItemsRepository:
    """
    Repository for CS2 items.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_all_skin_variants(self):
        """
        Get all skin variants.
        """
        return self.db.query(SkinVariant).all()
    
    def get_all_skin_variants_with_opts(self, wears: bool = True, skin: bool = True):
        """
        Get all skin variants with options for wears and skins.
        """
        query = self.db.query(SkinVariant)

        if wears:
            query = query.options(selectinload(SkinVariant.wear))

        if skin:
            query = query.options(selectinload(SkinVariant.skin))

        return query.all()

    def get_all_skins(self):
        """
        Get all skins.
        """
        return self.db.query(Skin).all()
    
    def get_all_stickers(self):
        """
        Get all stickers.
        """
        return self.db.query(Sticker).all()
    
    def get_all_crates(self):
        """
        Get all cases.
        """
        return self.db.query(Crate).all()
    
    def get_all_agents(self):
        """
        Get all agents.
        """
        return self.db.query(Agent).all()
    
    def get_all_keychains(self):
        """
        Get all keychains.
        """
        return self.db.query(Keychain).all()
    
