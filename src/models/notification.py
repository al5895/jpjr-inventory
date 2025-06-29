from . import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(300), nullable=False)
    type = db.Column(db.String(50), default='info', nullable=False)  # info, warning, danger, success
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)  # Lié à un article si applicable
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    auto_dismiss = db.Column(db.Boolean, default=False)  # Se ferme automatiquement après un temps
    
    # Relation avec l'article
    item = db.relationship('Item', backref='notifications', lazy=True)

    def __repr__(self):
        return f'<Notification {self.type}: {self.message[:30]}...>'
    
    @staticmethod
    def create_stock_alert(item):
        """Créer une notification de stock épuisé"""
        if item.stock <= 0:
            # Vérifier si une alerte existe déjà pour cet article
            existing = Notification.query.filter_by(
                item_id=item.id,
                type='danger',
                is_active=True
            ).first()
            
            if not existing:
                notification = Notification(
                    message=f"Stock épuisé pour l'article '{item.name}'",
                    type='danger',
                    item_id=item.id,
                    is_active=True
                )
                db.session.add(notification)
                return notification
        return None
    
    @staticmethod
    def create_low_stock_alert(item, threshold=2):
        """Créer une notification de stock faible"""
        if 0 < item.stock <= threshold:
            # Vérifier si une alerte existe déjà
            existing = Notification.query.filter_by(
                item_id=item.id,
                type='warning',
                is_active=True
            ).first()
            
            if not existing:
                notification = Notification(
                    message=f"Stock faible pour l'article '{item.name}' (reste {item.stock})",
                    type='warning',
                    item_id=item.id,
                    is_active=True
                )
                db.session.add(notification)
                return notification
        return None
    
    @staticmethod
    def dismiss_stock_alerts(item):
        """Supprimer les alertes de stock pour un article (quand le stock est rechargé)"""
        alerts = Notification.query.filter_by(
            item_id=item.id,
            is_active=True
        ).filter(Notification.type.in_(['danger', 'warning'])).all()
        
        for alert in alerts:
            alert.is_active = False