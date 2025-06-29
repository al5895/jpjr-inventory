from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nouveau champ pour le mot de passe hashé
    is_admin = db.Column(db.Boolean, default=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    borrows = db.relationship('Borrow', backref='user', lazy=True)

    def set_password(self, password):
        """Définir le mot de passe (sera automatiquement hashé)"""
        if password:
            self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifier si le mot de passe fourni est correct"""
        if not self.password_hash:
            return False  # Pas de mot de passe défini
        return check_password_hash(self.password_hash, password)
    
    def has_password(self):
        """Vérifier si l'utilisateur a un mot de passe défini"""
        return self.password_hash is not None
    
    def __repr__(self):
        if self.is_super_admin:
            return f'<Super-Admin {self.name}>'
        elif self.is_admin:
            return f'<Admin {self.name}>'
        return f'<User {self.name}>'
    
    @property
    def role(self):
        """Retourne le rôle de l'utilisateur"""
        if self.is_super_admin:
            return "Super-Admin"
        elif self.is_admin:
            return "Admin"
        return "Utilisateur"