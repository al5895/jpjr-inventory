# JPJR / Je prends, je rends

Créé par **Les Frères Poulain**.

JPJR est une petite application web développée avec Flask pour gérer un inventaire d'objets et suivre les emprunts. Elle intègre une interface d'administration, une API JSON et des commandes vocales optionnelles via OpenAI.

**Vidéo de présentation du projet :** [Lien YouTube](https://www.youtube.com/watch?v=ZFS_MIF8jPY&t)

## 🚀 Démarrage Rapide

1.  Créez et activez un environnement virtuel Python :
    ```bash
    # Créer l'environnement (une seule fois)
    python -m venv venv

    # Activer l'environnement (pour chaque nouvelle session de terminal)
    # Sur Windows :
    venv\Scripts\activate
    # Sur macOS/Linux :
    source venv/bin/activate
    ```
2.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```
3.  Créez un fichier `.env` à partir de `.env.example` et configurez les variables pour la base de données et l'API (voir `docs/documentation_technique.md` pour plus de détails).
4.  Lancez l'application :
    ```bash
    python -m src.app
    ```

Par défaut, l'application utilise SQLite. Vous pouvez passer à PostgreSQL en définissant `DB_TYPE=postgresql` dans votre fichier `.env`.

## ✨ Fonctionnalités Clés

*   🗃️ **Gestion d'Inventaire Détaillée :** Organisez avec précision vos articles, utilisateurs et emplacements de stockage (zones, meubles, tiroirs).
*   🤝 **Suivi d'Emprunts Efficace :** Enregistrez les prêts, définissez des dates de retour et gardez un œil sur les articles empruntés.
*   📦 **Flexibilité des Articles : Conventionnels & Temporaires**
    *   **Articles Conventionnels :** Vos objets permanents, soigneusement rangés avec un emplacement fixe (ex: "Zone: Bureau, Meuble: Étagère").
    *   **Articles Temporaires :** Pour les besoins du moment ! Créez-les à la volée, souvent par une simple commande vocale (ex: "piles").
*   🔌 **API JSON Robuste :** Intégrez JPJR à d'autres outils ou services grâce à des points de terminaison complets pour les articles, prêts, emplacements et services d'IA.
*   🎙️ **Commandes Vocales Intelligentes (propulsées par 4o Transcribe et GPT-4o-mini) :**
    *   **Depuis le Tableau de Bord (Dashboard) :**
        *   ⚡ **Ajout Rapide "Temporaire" :** Dictez et ajoutez instantanément des articles sans emplacement prédéfini.
        *   🧠 **Mode "Complet" (Recherche/Ajout Intelligent) :** L'IA identifie vos articles, les rapproche de votre inventaire existant ou crée de nouveaux articles temporaires. (Note : peut solliciter davantage l'API pour une pertinence accrue).
    *   🏠 **Page Dédiée "Ajout Vocal Conventionnel" :** Dictez le nom de l'article ET son emplacement (Zone, Meuble, Tiroir) pour l'intégrer parfaitement à votre système de rangement, avec l'aide de l'IA pour un rapprochement intelligent.
*   💬 **Dialogue avec vos Données (via GPT-4o-mini) :** Posez des questions en langage naturel sur votre inventaire directement depuis la barre de menu !
*   📄 **Export PDF Pratique :** Obtenez une copie de votre inventaire complet au format PDF en un clic.

## 🗄️ Base de Données : Flexibilité SQLite & PostgreSQL

*   **SQLite (par défaut) :** Idéal pour une utilisation locale et un développement rapide. La base de données est un simple fichier dans le projet.
*   **PostgreSQL :** Recommandé pour une utilisation plus robuste. Il permet d'exposer la base de données à des outils externes, notamment pour des applications d'intelligence artificielle qui pourraient avoir besoin d'analyser les données d'inventaire.

## 🏗️ Structure du Projet

```
config/         # Modules de configuration
docs/           # Documentation technique
src/            # Code source de l'application
    app.py      # Point d'entrée de Flask
    models/     # Modèles SQLAlchemy
    routes/     # Blueprints (groupes de routes)
    static/     # Fichiers statiques (CSS, JS, images)
    templates/  # Modèles Jinja2
tests/          # Tests unitaires et d'intégration
```

## ©️ Licence

Ce projet est sous licence [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](http://creativecommons.org/licenses/by-nc-sa/4.0/).

[![Licence CC BY-NC-SA 4.0](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/4.0/)

See the [technical documentation](docs/documentation_technique.md) for a complete guide.


