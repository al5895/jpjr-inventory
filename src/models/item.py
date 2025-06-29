from . import db
from datetime import datetime

class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    stock = db.Column(db.Integer, default=1, nullable=False)  # NOUVEAU: Quantité en stock
    
    # Flag pour distinguer les articles temporaires et permanents
    is_temporary = db.Column(db.Boolean, default=False, nullable=False)
    
    # Clés étrangères pour les emplacements (nullable pour les articles temporaires)
    zone_id = db.Column(db.Integer, db.ForeignKey('zone.id'), nullable=True)
    furniture_id = db.Column(db.Integer, db.ForeignKey('furniture.id'), nullable=True)
    drawer_id = db.Column(db.Integer, db.ForeignKey('drawer.id'), nullable=True)
    
    # Champs texte pour la compatibilité (nullable pour les articles temporaires)
    zone = db.Column(db.String(100), nullable=True)
    mobilier = db.Column(db.String(100), nullable=True)
    niveau_tiroir = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    borrows = db.relationship('Borrow', backref='item', lazy=True, cascade="all, delete-orphan")
    
    # Relations avec les tables de localisation
    zone_rel = db.relationship('Zone', backref='items', lazy=True)
    furniture_rel = db.relationship('Furniture', backref='items', lazy=True)
    drawer_rel = db.relationship('Drawer', backref='items', lazy=True)

    def __repr__(self):
        if self.is_temporary:
            return f'<Item (Temp) {self.name} - Stock: {self.stock}>'
        return f'<Item {self.name} - Stock: {self.stock}>'
    
    @property
    def is_available(self):
        """Vérifie si l'article est disponible (stock > 0)"""
        return self.stock > 0
    
    @property
    def is_low_stock(self):
        """Vérifie si le stock est faible (seuil configurable)"""
        return self.stock <= 2 and self.stock > 0
    
    @property
    def is_out_of_stock(self):
        """Vérifie si l'article est en rupture de stock"""
        return self.stock <= 0
    
    def decrease_stock(self, quantity=1):
        """Diminue le stock de la quantité spécifiée"""
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False
    
    def increase_stock(self, quantity=1):
        """Augmente le stock de la quantité spécifiée"""
        self.stock += quantity
        
    @property
    def location_info(self):
        """Retourne les informations de localisation formatées"""
        if self.is_temporary:
            return "Article temporaire (sans emplacement)"
        
        zone_name = self.zone_rel.name if self.zone_rel else "Non spécifié"
        furniture_name = self.furniture_rel.name if self.furniture_rel else "Non spécifié"
        drawer_name = self.drawer_rel.name if self.drawer_rel else "Non spécifié"
        
        return f"{zone_name} > {furniture_name} > {drawer_name}"