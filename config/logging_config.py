import logging
from logging.handlers import RotatingFileHandler
import os

# Crée le dossier de logs s'il n'existe pas
if not os.path.exists('logs'):
    os.mkdir('logs')

def setup_logging(app):
    # Si un gestionnaire par défaut est présent, le supprimer pour éviter les doublons
    if app.logger.handlers:
        app.logger.removeHandler(app.logger.handlers[0])

    # Formatter pour les logs
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(name)s.%(funcName)s] - %(message)s'
    )

    # Handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    # En mode production (app.debug est False), n'afficher que les WARNINGS et ERREURS dans la console.
    # En mode debug, afficher les messages DEBUG et supérieurs.
    console_handler.setLevel(logging.WARNING if not app.debug else logging.DEBUG)

    # Handler pour le fichier de log général (avec rotation)
    file_handler = RotatingFileHandler(
        'logs/jpjr.log', maxBytes=10240, backupCount=10
    )
    file_handler.setFormatter(formatter)
    # En mode production (app.debug est False), enregistrer les messages INFO et supérieurs dans jpjr.log.
    # En mode debug, enregistrer les messages DEBUG et supérieurs.
    file_handler.setLevel(logging.INFO if not app.debug else logging.DEBUG)

    # Handler pour le fichier d'erreurs (avec rotation)
    error_handler = RotatingFileHandler(
        'logs/error.log', maxBytes=10240, backupCount=10
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # Ajoute les handlers au logger de l'application
    # Le logger racine est configuré pour capturer les logs de toutes les bibliothèques (ex: SQLAlchemy)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)

    if not app.debug:
        # En mode production, réduire la verbosité de Werkzeug
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

    app.logger.info("Configuration de la journalisation terminée. Mode debug: %s", app.debug)
