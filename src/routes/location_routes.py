from flask import Blueprint, request, jsonify, render_template
from src.models import db
from src.models.location import Zone, Furniture, Drawer
from src.models.item import Item
from sqlalchemy.exc import IntegrityError

location_bp = Blueprint('location', __name__, url_prefix='/api/location')

# Ce blueprint ne contient plus que des APIs pour les emplacements

# API pour les zones
@location_bp.route('/zones', methods=['GET', 'POST'])
def api_zones():
    if request.method == 'GET':
        zones = Zone.query.all()
        return jsonify([{
            'id': zone.id,
            'name': zone.name,
            'description': zone.description
        } for zone in zones])
    
    elif request.method == 'POST':
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'error': 'Le nom de la zone est requis'}), 400
        
        # Vérifier si la zone existe déjà
        existing_zone = Zone.query.filter_by(name=name).first()
        if existing_zone:
            return jsonify({'error': 'Une zone avec ce nom existe déjà'}), 400
        
        # Créer la nouvelle zone
        zone = Zone(name=name, description=description)
        db.session.add(zone)
        
        try:
            db.session.commit()
            return jsonify({
                'id': zone.id,
                'name': zone.name,
                'description': zone.description
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@location_bp.route('/zones/<int:zone_id>', methods=['DELETE'])
def api_delete_zone(zone_id):
    # Vérifier si des articles utilisent cette zone
    items = Item.query.filter_by(zone_id=zone_id).first()
    if items:
        return jsonify({'error': 'Cette zone est utilisée par des articles et ne peut pas être supprimée'}), 400
    
    zone = db.session.get(Zone, zone_id)
    if not zone:
        return jsonify({'error': 'Zone non trouvée'}), 404
    
    # Supprimer tous les meubles associés à cette zone
    furniture_list = Furniture.query.filter_by(zone_id=zone_id).all()
    for furniture in furniture_list:
        # Supprimer tous les tiroirs associés à ce meuble
        drawers = Drawer.query.filter_by(furniture_id=furniture.id).all()
        for drawer in drawers:
            db.session.delete(drawer)
        db.session.delete(furniture)
    
    db.session.delete(zone)
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API pour les meubles
@location_bp.route('/furniture', methods=['GET', 'POST'])
def api_furniture():
    if request.method == 'GET':
        zone_id = request.args.get('zone_id')
        
        if zone_id:
            furniture_list = Furniture.query.filter_by(zone_id=zone_id).all()
        else:
            furniture_list = Furniture.query.all()
        
        result = []
        for furniture in furniture_list:
            zone = db.session.get(Zone, furniture.zone_id)
            result.append({
                'id': furniture.id,
                'name': furniture.name,
                'description': furniture.description,
                'zone_id': furniture.zone_id,
                'zone_name': zone.name if zone else 'Inconnue'
            })
        
        return jsonify(result)
    
    elif request.method == 'POST':
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        zone_id = data.get('zone_id')
        
        if not name:
            return jsonify({'error': 'Le nom du meuble est requis'}), 400
        
        if not zone_id:
            return jsonify({'error': 'La zone est requise'}), 400
        
        # Vérifier si la zone existe
        zone = db.session.get(Zone, zone_id)
        if not zone:
            return jsonify({'error': 'Zone non trouvée'}), 404
        
        # Vérifier si un meuble avec le même nom existe déjà dans cette zone
        existing_furniture = Furniture.query.filter_by(name=name, zone_id=zone_id).first()
        if existing_furniture:
            return jsonify({'error': 'Un meuble avec ce nom existe déjà dans cette zone'}), 400
        
        # Créer le nouveau meuble
        furniture = Furniture(name=name, description=description, zone_id=zone_id)
        db.session.add(furniture)
        
        try:
            db.session.commit()
            return jsonify({
                'id': furniture.id,
                'name': furniture.name,
                'description': furniture.description,
                'zone_id': furniture.zone_id,
                'zone_name': zone.name
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@location_bp.route('/furniture/<int:furniture_id>', methods=['DELETE'])
def api_delete_furniture(furniture_id):
    # Vérifier si des articles utilisent ce meuble
    items = Item.query.filter_by(furniture_id=furniture_id).first()
    if items:
        return jsonify({'error': 'Ce meuble est utilisé par des articles et ne peut pas être supprimé'}), 400
    
    furniture = db.session.get(Furniture, furniture_id)
    if not furniture:
        return jsonify({'error': 'Meuble non trouvé'}), 404
    
    # Supprimer tous les tiroirs associés à ce meuble
    drawers = Drawer.query.filter_by(furniture_id=furniture_id).all()
    for drawer in drawers:
        db.session.delete(drawer)
    
    db.session.delete(furniture)
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API pour les tiroirs
@location_bp.route('/drawers', methods=['GET', 'POST'])
def api_drawers():
    if request.method == 'GET':
        furniture_id = request.args.get('furniture_id')
        
        if furniture_id:
            drawers = Drawer.query.filter_by(furniture_id=furniture_id).all()
        else:
            drawers = Drawer.query.all()
        
        result = []
        for drawer in drawers:
            furniture = db.session.get(Furniture, drawer.furniture_id)
            zone = None
            if furniture:
                zone = db.session.get(Zone, furniture.zone_id)
            
            result.append({
                'id': drawer.id,
                'name': drawer.name,
                'description': drawer.description,
                'furniture_id': drawer.furniture_id,
                'furniture_name': furniture.name if furniture else 'Inconnu',
                'zone_id': furniture.zone_id if furniture else None,
                'zone_name': zone.name if zone else 'Inconnu'
            })
        
        return jsonify(result)
    
    elif request.method == 'POST':
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        furniture_id = data.get('furniture_id')
        
        if not name:
            return jsonify({'error': 'Le nom du tiroir est requis'}), 400
        
        if not furniture_id:
            return jsonify({'error': 'Le meuble est requis'}), 400
        
        # Vérifier si le meuble existe
        furniture = db.session.get(Furniture, furniture_id)
        if not furniture:
            return jsonify({'error': 'Meuble non trouvé'}), 404
        
        # Vérifier si un tiroir avec le même nom existe déjà dans ce meuble
        existing_drawer = Drawer.query.filter_by(name=name, furniture_id=furniture_id).first()
        if existing_drawer:
            return jsonify({'error': 'Un tiroir avec ce nom existe déjà dans ce meuble'}), 400
        
        # Créer le nouveau tiroir
        drawer = Drawer(name=name, description=description, furniture_id=furniture_id)
        db.session.add(drawer)
        
        try:
            db.session.commit()
            return jsonify({
                'id': drawer.id,
                'name': drawer.name,
                'description': drawer.description,
                'furniture_id': drawer.furniture_id,
                'furniture_name': furniture.name
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@location_bp.route('/drawers/<int:drawer_id>', methods=['DELETE'])
def api_delete_drawer(drawer_id):
    # Vérifier si des articles utilisent ce tiroir
    items = Item.query.filter_by(drawer_id=drawer_id).all()
    
    if items:
        # Limiter à 3 noms d'articles pour l'affichage
        item_names = [item.name for item in items]
        item_display = ', '.join(item_names[:3])
        if len(items) > 3:
            item_display += ' et d\'autres'
        
        # Message d'erreur détaillé
        error_message = f"Ce tiroir contient {len(items)} article(s) ({item_display}) et ne peut pas être supprimé. "
        error_message += "Veuillez d'abord déplacer ces articles vers un autre tiroir ou les supprimer."
        
        return jsonify({
            'error': error_message,
            'items': [{'id': item.id, 'name': item.name} for item in items[:10]],  # Limiter à 10 articles pour la réponse
            'item_count': len(items)
        }), 400
    
    # Supprimer le tiroir
    drawer = db.session.get(Drawer, drawer_id)
    if not drawer:
        return jsonify({'error': 'Tiroir non trouvé'}), 404
    
    db.session.delete(drawer)
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            'error': 'Ce tiroir est référencé par d\'autres éléments et ne peut pas être supprimé',
            'details': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
