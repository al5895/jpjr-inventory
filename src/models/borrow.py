from . import db
from datetime import datetime

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)  # NOUVEAU: Quantité empruntée
    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expected_return_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    returned = db.Column(db.Boolean, default=False)

    def __repr__(self):
        item_name = self.item.name if hasattr(self, 'item') and self.item else "Unknown"
        return f'<Borrow {self.user.name} - {item_name} (x{self.quantity})>'
    
    def return_item(self):
        """Retourner l'article emprunté et remettre en stock"""
        if not self.returned:
            self.returned = True
            self.return_date = datetime.utcnow()
            # Remettre la quantité en stock
            if self.item:
                self.item.increase_stock(self.quantity)
            return True
        return False
    
    @property
    def is_overdue(self):
        """Vérifier si l'emprunt est en retard"""
        if self.returned:
            return False
        return datetime.utcnow() > self.expected_return_date
    
    @property
    def days_until_return(self):
        """Nombre de jours jusqu'à la date de retour prévue"""
        if self.returned:
            return 0
        delta = self.expected_return_date - datetime.utcnow()
        return delta.days