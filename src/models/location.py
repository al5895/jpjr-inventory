from datetime import datetime
from . import db

class Zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation avec les meubles
    furniture = db.relationship('Furniture', backref='zone', lazy=True)
    
    def __repr__(self):
        return f'<Zone {self.name}>'

class Furniture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    zone_id = db.Column(db.Integer, db.ForeignKey('zone.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation avec les tiroirs/niveaux
    drawers = db.relationship('Drawer', backref='furniture', lazy=True)
    
    def __repr__(self):
        return f'<Furniture {self.name} in Zone {self.zone_id}>'
    
    # Contrainte d'unicité: un meuble avec le même nom ne peut pas exister dans la même zone
    __table_args__ = (
        db.UniqueConstraint('name', 'zone_id', name='unique_furniture_per_zone'),
    )

class Drawer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    furniture_id = db.Column(db.Integer, db.ForeignKey('furniture.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Drawer {self.name} in Furniture {self.furniture_id}>'
    
    # Contrainte d'unicité: un tiroir avec le même nom ne peut pas exister dans le même meuble
    __table_args__ = (
        db.UniqueConstraint('name', 'furniture_id', name='unique_drawer_per_furniture'),
    )
