from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models import db
from src.models.user import User
from src.models.item import Item
from src.models.borrow import Borrow
from datetime import datetime
from functools import wraps  # Pour le décorateur login_required

# Création du blueprint
main_bp = Blueprint('main', __name__)

# Décorateur pour vérifier la connexion
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Route principale
@main_bp.route('/')
def index():
    """
    Page d'accueil - Redirige vers le tableau de bord si l'utilisateur est connecté,
    ou vers la page de login sinon
    """
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    
    # Récupérer seulement les utilisateurs sans mot de passe (pour la transition)
    users_without_password = db.session.query(User).filter(User.password_hash == None).order_by(User.name).all()
    return render_template('index.html', users_without_password=users_without_password)

# Page de connexion
@main_bp.route('/login', methods=['POST'])
def login():
    """
    Gère la connexion et l'inscription des utilisateurs avec mots de passe
    """
    action = request.form.get('action', 'login')
    user_name = request.form.get('user_name', '').strip()
    password = request.form.get('password', '')
    
    if not user_name:
        flash('Veuillez entrer votre nom', 'danger')
        return redirect(url_for('main.index'))
    
    if action == 'login':
        # Tentative de connexion
        user = db.session.query(User).filter(User.name == user_name).first()
        
        if not user:
            flash('Utilisateur introuvable', 'danger')
            return redirect(url_for('main.index'))
        
        # Vérifier le mot de passe
        if not user.check_password(password):
            flash('Mot de passe incorrect', 'danger')
            return redirect(url_for('main.index'))
        
        # Connexion réussie
        session['user_id'] = user.id
        session['user_name'] = user.name
        flash(f'Bienvenue, {user.name}!', 'success')
        return redirect(url_for('main.dashboard'))
    
    elif action == 'register':
        # Inscription d'un nouvel utilisateur
        email = request.form.get('email', '').strip()
        password_confirm = request.form.get('password_confirm', '')
        
        if not password:
            flash('Le mot de passe est requis', 'danger')
            return redirect(url_for('main.index'))
        
        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas', 'danger')
            return redirect(url_for('main.index'))
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.session.query(User).filter(User.name == user_name).first()
        if existing_user:
            flash('Un utilisateur avec ce nom existe déjà', 'danger')
            return redirect(url_for('main.index'))
        
        # Créer le nouvel utilisateur
        new_user = User(name=user_name, email=email if email else None)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Connexion automatique après inscription
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name
        flash(f'Compte créé avec succès ! Bienvenue, {new_user.name}!', 'success')
        return redirect(url_for('main.dashboard'))
    
    flash('Action non reconnue', 'danger')
    return redirect(url_for('main.index'))

# Connexion rapide avec ID (pour comptes sans mot de passe)
@main_bp.route('/login/<int:user_id>')
def login_with_id(user_id):
    """
    Connexion rapide avec l'ID de l'utilisateur (seulement pour comptes sans mot de passe)
    """
    user = db.session.get(User, user_id)
    if not user:
        flash('Utilisateur non trouvé', 'danger')
        return redirect(url_for('main.index'))
    
    # Si l'utilisateur a déjà un mot de passe, rediriger vers la connexion normale
    if user.has_password():
        flash('Cet utilisateur a un mot de passe. Veuillez utiliser le formulaire de connexion.', 'info')
        return redirect(url_for('main.index'))
    
    # Rediriger vers la définition de mot de passe
    return redirect(url_for('main.set_password', user_id=user_id))

# Route pour définir un mot de passe (comptes existants)
@main_bp.route('/set-password/<int:user_id>', methods=['GET', 'POST'])
def set_password(user_id):
    """
    Permet aux utilisateurs existants de définir un mot de passe
    """
    user = db.session.get(User, user_id)
    if not user:
        flash('Utilisateur non trouvé', 'danger')
        return redirect(url_for('main.index'))
    
    if user.has_password():
        flash('Cet utilisateur a déjà un mot de passe. Utilisez la connexion normale.', 'info')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        if not password:
            flash('Le mot de passe est requis', 'danger')
        elif password != password_confirm:
            flash('Les mots de passe ne correspondent pas', 'danger')
        else:
            # Définir le mot de passe
            user.set_password(password)
            db.session.commit()
            
            # Connexion automatique
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash(f'Mot de passe défini avec succès ! Bienvenue, {user.name}!', 'success')
            return redirect(url_for('main.dashboard'))
    
    return render_template('set_password.html', user=user)

# Tableau de bord
@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Tableau de bord principal de l'application
    """
    user_id = session['user_id']
    user = db.session.get(User, user_id)
    
    if not user:
        flash('Utilisateur non trouvé', 'danger')
        session.clear()
        return redirect(url_for('main.index'))
    
    # Récupérer les articles disponibles (non empruntés)
    subquery = db.session.query(Borrow.item_id).filter(Borrow.return_date == None)
    available_items = db.session.query(Item).filter(
        ~Item.id.in_(subquery)
    ).order_by(Item.name).all()
    
    return render_template('dashboard.html', 
                           user=user, 
                           available_items=available_items)

# Mes emprunts
@main_bp.route('/my-borrows')
@login_required
def my_borrows():
    """
    Page affichant tous les emprunts en cours de l'utilisateur
    """
    user_id = session['user_id']
    user = db.session.get(User, user_id)
    
    if not user:
        flash('Utilisateur non trouvé', 'danger')
        session.clear()
        return redirect(url_for('main.index'))
    
    # Récupérer les emprunts en cours de l'utilisateur
    current_borrows = db.session.query(Borrow).filter(
        Borrow.user_id == user_id,
        Borrow.return_date == None
    ).all()
    
    return render_template('my_borrows.html', 
                           user=user, 
                           current_borrows=current_borrows)

# Page Recherche d'articles
@main_bp.route('/search-articles')
@login_required
def search_articles():
    """Page de recherche d'articles pour tous les utilisateurs"""
    return render_template('search_articles.html')

# API de recherche d'articles
@main_bp.route('/api/search-items')
@login_required
def api_search_items():
    """API pour rechercher des articles - accessible à tous"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'items': []})
    
    # Recherche dans les articles
    items = db.session.query(Item).filter(
        Item.name.ilike(f'%{query}%')
    ).order_by(Item.name).limit(20).all()
    
    results = []
    for item in items:
        # Vérifier si emprunté
        is_borrowed = db.session.query(Borrow).filter(
            Borrow.item_id == item.id, 
            Borrow.return_date == None
        ).first() is not None
        
        results.append({
            'id': item.id,
            'name': item.name,
            'stock': item.stock,
            'is_temporary': item.is_temporary,
            'is_borrowed': is_borrowed,
            'zone_name': item.zone_rel.name if item.zone_rel else None,
            'furniture_name': item.furniture_rel.name if item.furniture_rel else None,
            'drawer_name': item.drawer_rel.name if item.drawer_rel else None
        })
    
    return jsonify({'items': results})

    # Route sécurisée pour initialiser le premier super-admin
@main_bp.route('/init-super-admin/<string:username>/<string:secret_key>')
def init_super_admin(username, secret_key):
    """
    Route sécurisée pour créer le premier super-admin.
    Ne fonctionne que s'il n'y a aucun super-admin existant.
    """
    # Vérifier le mot de passe secret
    expected_secret = "JPJR-ADMIN-2024-SECURE"  # Changez ce mot de passe
    if secret_key != expected_secret:
        return "Accès refusé - Clé incorrecte", 403
    
    # Vérifier qu'aucun super-admin n'existe déjà
    existing_super_admin = db.session.query(User).filter(User.is_super_admin == True).first()
    if existing_super_admin:
        return f"Un super-admin existe déjà : {existing_super_admin.name}", 400
    
    # Trouver l'utilisateur à promouvoir
    user = db.session.query(User).filter(User.name == username).first()
    if not user:
        return f"Utilisateur '{username}' non trouvé. Créez d'abord ce compte.", 404
    
    # Promouvoir en super-admin
    user.is_admin = True
    user.is_super_admin = True
    db.session.commit()
    
    return f"""
    <h2>✅ Super-admin créé avec succès !</h2>
    <p><strong>{username}</strong> est maintenant super-administrateur.</p>
    <p><a href="/">Retour à l'application</a></p>
    <hr>
    <small>Cette route ne fonctionnera plus maintenant qu'un super-admin existe.</small>
    """

# Déconnexion
@main_bp.route('/logout')
def logout():
    """
    Déconnecte l'utilisateur et nettoie la session
    """
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('main.index'))
