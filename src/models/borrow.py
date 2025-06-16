from . import db
from datetime import datetime

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expected_return_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    returned = db.Column(db.Boolean, default=False)

    def __repr__(self):
        item_name = self.item.name if hasattr(self, 'item') and self.item else "Unknown"
        return f'<Borrow {self.user.name} - {item_name}>'
