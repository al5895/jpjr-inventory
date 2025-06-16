from flask import Blueprint, request, jsonify, session
from src.models import db
from src.models.item import Item

# Création du blueprint
utils_bp = Blueprint('utils', __name__)

# Autocomplétion pour la recherche d'articles
@utils_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    """
    Fournit des suggestions pour l'autocomplétion de la recherche d'articles
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    query = request.args.get('term', '')
    if not query or len(query) < 2:
        return jsonify([])
    
    # Rechercher les articles correspondant à la requête
    items = db.session.query(Item).filter(
        Item.name.ilike(f'%{query}%')
    ).order_by(Item.name).limit(10).all()
    
    # Formater les résultats
    results = []
    for item in items:
        results.append({
            'id': item.id,
            'label': f"{item.name} - {item.location_info}",
            'value': item.name
        })
    
    return jsonify(results)
