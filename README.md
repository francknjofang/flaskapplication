    Application de Cartes Mémoire

----------------------------------------------------------------------------------------------------------------------------

    Introduction

    Cette application Flask a été conçue pour créer, gérer et étudier des cartes mémoire pour l'apprentissage. Elle offre des fonctionnalités pour les utilisateurs enregistrés ainsi qu'un compte administrateur avec des droits étendus.

    Fonctionnalités

    Inscription et Connexion : Les utilisateurs peuvent créer un compte et se connecter pour accéder aux fonctionnalités.
    Gestion des Cartes : Ajouter, modifier, et supprimer des cartes mémoire par module.
    Étude des Cartes : Les utilisateurs peuvent étudier les cartes mémoire par module avec des réponses mélangées pour les tests.


    Compte Administrateur

        Identifiants :
        Username: admin
        Email: admin@gmail.com
        Password: '1234'
        Droits : Ce compte dispose de tous les droits et peut gérer l'ensemble des fonctionnalités de l'application.

-----------------------------------------------------------------------------------------------------------------------------------------
   
    Guide d'Utilisation

    Installation :

    
    Installer les dépendances : pip install flask flask_sqlalchemy SQLAlchemy
    Configuration de la Base de Données : confère app.py
    L'application utilise SQLite. La base de données est stockée dans MemoryCard.db.
    Lancement de l'Application :
    Exécuter le script Python app.py ou flask run(en environement virtuel)


    Utilisation :

    Accéder à l'application via le navigateur à l'adresse : http://localhost:5000.
    Se connecter avec les identifiants ou utiliser le compte administrateur pour accéder à toutes les fonctionnalités.

    Développement

    Langage : Python avec Flask.
    Base de Données : SQLite.
-----------------------------------------------------------------------------------------------------------------------------------------
    Structure du Projet :

    app.py : Le script principal de l'application.
    templates/ : Dossier contenant les fichiers HTML pour les vues.
    instance/ : Dossier contenant la Base de donnée
    static/ : Dossier contenant les fichiers JS, css, jpj
    .venv : environement virtuel + bibliothèque néceéssaire au deploiement du serveur flask
    dates.txt : fichier contenant les dates pendant lesquels vous passez le teste
    README.md : Ce fichier.