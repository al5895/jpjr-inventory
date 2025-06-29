from flask import Blueprint, request, jsonify, session
from src.models import db
from src.models.borrow import Borrow
from src.models.item import Item
from src.models.user import User
from datetime import datetime

# Création du blueprint
loans_api_bp = Blueprint('loans_api', __name__, url_prefix='/api/loans')

# Créer un emprunt (ancienne version - conservée pour compatibilité)
@loans_api_bp.route('/create', methods=['POST'])
def create_loan():
    """
    API pour créer un nouvel emprunt (ancienne version)
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user_id = session['user_id']  # Utiliser l'ID de l'utilisateur connecté
    
    data = request.json
    items = data.get('items', [])
    return_date_str = data.get('return_date')
    
    if not items or len(items) == 0:
        return jsonify({'error': 'Aucun article sélectionné pour l\'emprunt'}), 400
    
    if not return_date_str:
        return jsonify({'error': 'Date de retour prévue requise'}), 400
    
    # Convertir la date de retour prévue
    try:
        # Format français: JJ/MM/AAAA
        day, month, year = return_date_str.split('/')
        expected_return_date = datetime(int(year), int(month), int(day))
    except Exception as e:
        return jsonify({'error': f'Format de date invalide: {str(e)}'}), 400
    
    # Vérifier que l'utilisateur existe
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Résultats de l'opération
    results = {
        'success': True,
        'loans': []
    }
    
    try:
        for item_data in items:
            item_id = item_data.get('id')
            
            # Vérifier que l'article existe
            item = db.session.get(Item, item_id)
            if not item:
                continue  # Ignorer les articles inexistants
            
            # Vérifier que l'article n'est pas déjà emprunté
            existing_borrow = db.session.query(Borrow).filter(
                Borrow.item_id == item_id,
                Borrow.return_date == None
            ).first()
            
            if existing_borrow:
                # Ajouter à la liste des articles déjà empruntés
                results['loans'].append({
                    'status': 'error',
                    'error': 'Déjà emprunté',
                    'item_id': item_id,
                    'item_name': item.name,
                    'borrowed_by': {
                        'user_id': existing_borrow.user_id,
                        'user_name': existing_borrow.user.name,
                        'borrow_date': existing_borrow.borrow_date.isoformat()
                    }
                })
                continue
            
            # Créer le nouvel emprunt
            new_borrow = Borrow(
                user_id=user_id,
                item_id=item_id,
                quantity=1,  # Ancienne version = toujours 1
                borrow_date=datetime.now(),
                expected_return_date=expected_return_date
            )
            
            db.session.add(new_borrow)
            db.session.flush()  # Pour obtenir l'ID sans commit immédiat
            
            # Ajouter à la liste des emprunts réussis
            results['loans'].append({
                'status': 'success',
                'id': new_borrow.id,
                'user_id': new_borrow.user_id,
                'user_name': user.name,
                'item_id': new_borrow.item_id,
                'item_name': item.name,
                'borrow_date': new_borrow.borrow_date.isoformat(),
                'expected_return_date': expected_return_date.strftime('%d/%m/%Y')
            })
        
        # Commit des changements si au moins un emprunt a réussi
        if any(loan.get('status') == 'success' for loan in results['loans']):
            db.session.commit()
        else:
            db.session.rollback()
            results['success'] = False
        
        return jsonify(results)
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# NOUVELLE VERSION : Créer un emprunt avec gestion des quantités
@loans_api_bp.route('/create-with-quantities', methods=['POST'])
def create_loan_with_quantities():
    """
    API pour créer un emprunt avec gestion des quantités et décrément automatique du stock
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user_id = session['user_id']
    data = request.json
    items = data.get('items', [])
    return_date_str = data.get('return_date')
    
    if not items or len(items) == 0:
        return jsonify({'error': 'Aucun article sélectionné pour l\'emprunt'}), 400
    
    if not return_date_str:
        return jsonify({'error': 'Date de retour prévue requise'}), 400
    
    # Convertir la date de retour
    try:
        expected_return_date = datetime.fromisoformat(return_date_str)
    except Exception as e:
        return jsonify({'error': f'Format de date invalide: {str(e)}'}), 400
    
    # Vérifier que l'utilisateur existe
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Import local pour éviter problème d'import circulaire
    from src.models.notification import Notification

    # Résultats de l'opération
    results = {
        'success': True,
        'loans': [],
        'notifications': []
    }
    
    try:
        for item_data in items:
            item_id = item_data.get('id')
            quantity = int(item_data.get('quantity', 1))
            is_temporary = item_data.get('isTemporary', False)
            item_name = item_data.get('name', '')
            
            if is_temporary:
                # Créer un article temporaire
                new_temp_item = Item(
                    name=item_name,
                    stock=quantity,
                    is_temporary=True
                )
                db.session.add(new_temp_item)
                db.session.flush()  # Pour obtenir l'ID
                item = new_temp_item
            else:
                # Vérifier que l'article existe
                item = db.session.get(Item, item_id)
                if not item:
                    results['loans'].append({
                        'status': 'error',
                        'error': 'Article non trouvé',
                        'item_name': item_name
                    })
                    continue
                
                # Vérifier que le stock est suffisant
                if item.stock < quantity:
                    results['loans'].append({
                        'status': 'error',
                        'error': f'Stock insuffisant (disponible: {item.stock}, demandé: {quantity})',
                        'item_name': item.name
                    })
                    continue
            
            # Créer l'emprunt
            new_borrow = Borrow(
                user_id=user_id,
                item_id=item.id,
                quantity=quantity,
                borrow_date=datetime.utcnow(),
                expected_return_date=expected_return_date
            )
            
            db.session.add(new_borrow)
            
            # Décrémenter le stock
            if not is_temporary:
                item.decrease_stock(quantity)
                
                # Créer des notifications si nécessaire
                if item.stock == 0:
                    notification = Notification.create_stock_alert(item)
                    if notification:
                        results['notifications'].append(f"Stock épuisé pour '{item.name}'")
                elif item.stock <= 2:
                    notification = Notification.create_low_stock_alert(item)
                    if notification:
                        results['notifications'].append(f"Stock faible pour '{item.name}' (reste {item.stock})")
            
            # Ajouter à la liste des emprunts réussis
            results['loans'].append({
                'status': 'success',
                'user_name': user.name,
                'item_name': item.name,
                'quantity': quantity,
                'return_date': expected_return_date.strftime('%d/%m/%Y')
            })
        
        # Commit des changements si au moins un emprunt a réussi
        successful_loans = [loan for loan in results['loans'] if loan.get('status') == 'success']
        if successful_loans:
            db.session.commit()
            results['message'] = f"{len(successful_loans)} emprunt(s) créé(s) avec succès"
        else:
            db.session.rollback()
            results['success'] = False
            results['error'] = "Aucun emprunt n'a pu être créé"
        
        return jsonify(results)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Retourner un emprunt
@loans_api_bp.route('/<int:loan_id>/return', methods=['POST'])
def return_loan(loan_id):
    """
    API pour retourner un emprunt et remettre en stock
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    # Vérifier que l'emprunt existe
    borrow = db.session.get(Borrow, loan_id)
    if not borrow:
        return jsonify({'error': 'Emprunt non trouvé'}), 404
    
    # Vérifier que l'article n'a pas déjà été retourné
    if borrow.return_date is not None:
        return jsonify({'error': 'Cet article a déjà été retourné'}), 400
    
    try:
        # Marquer l'emprunt comme retourné et remettre en stock
        success = borrow.return_item()
        
        if success:
            # Supprimer les alertes de stock si le stock est rechargé
            if borrow.item and borrow.item.stock > 0:
                from src.models.notification import Notification
                Notification.dismiss_stock_alerts(borrow.item)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'loan': {
                    'id': borrow.id,
                    'user_id': borrow.user_id,
                    'user_name': borrow.user.name,
                    'item_id': borrow.item_id,
                    'item_name': borrow.item.name,
                    'quantity': borrow.quantity,
                    'borrow_date': borrow.borrow_date.isoformat(),
                    'return_date': borrow.return_date.isoformat()
                }
            })
        else:
            return jsonify({'error': 'L\'article était déjà retourné'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Liste des emprunts
@loans_api_bp.route('', methods=['GET'])
def get_loans():
    """
    API pour récupérer la liste des emprunts
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    # Récupérer les paramètres de filtrage
    user_id = request.args.get('user_id') or session['user_id']  # Utiliser l'ID de l'utilisateur connecté par défaut
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    
    # Construire la requête de base
    query = db.session.query(Borrow)
    
    # Appliquer les filtres
    if user_id:
        query = query.filter(Borrow.user_id == user_id)
    
    if active_only:
        query = query.filter(Borrow.return_date == None)
    
    # Récupérer les résultats
    borrows = query.order_by(Borrow.borrow_date.desc()).all()
    
    # Formater les résultats
    results = []
    for borrow in borrows:
        item = borrow.item
        
        # Construire le résultat avec toutes les informations attendues par le frontend
        loan_data = {
            'id': borrow.id,
            'user_id': borrow.user_id,
            'user_name': borrow.user.name,
            'item_id': item.id,
            'item_name': item.name,
            'quantity': borrow.quantity,  # NOUVEAU: Quantité empruntée
            'borrow_date': borrow.borrow_date.isoformat(),  # Format ISO pour JavaScript
            'expected_return_date': borrow.expected_return_date.isoformat() if borrow.expected_return_date else None,
            'return_date': borrow.return_date.isoformat() if borrow.return_date else None,
            'is_temporary': item.is_temporary,
            'is_overdue': borrow.is_overdue,  # NOUVEAU: En retard
            'days_until_return': borrow.days_until_return  # NOUVEAU: Jours restants
        }
        
        # Ajouter les informations de localisation pour les articles conventionnels
        if not item.is_temporary:
            loan_data.update({
                'item_zone': item.zone,
                'item_mobilier': item.mobilier,
                'item_niveau_tiroir': item.niveau_tiroir,
                'item_location_info': item.location_info
            })
        
        results.append(loan_data)
    
    return jsonify(results)
