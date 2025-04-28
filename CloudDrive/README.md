# Cloud Drive

Google Drive  développé en Django, HTML et JavaScript. Ce projet vise à fournir une interface pour gérer des fichiers et des dossiers, similaire à Google Drive.

## Table des matières

- [Technologies utilisées](#technologies-utilisées)
- [Arborescence du projet](#Arborescence-du-projet)
- [Installation](#installation)


## Technologies utilisées

- *Django == [5.1.2]* - Framework web Python
- *SQLite* - Base de données
- *HTML/CSS* - Frontend
- *JavaScript* - Interactions dynamiques


# Arborescence du projet


```
project_django_real
│
└───projet_django
    │
    └───cloud_drive
        │
        └───cloud_drive
        │   │
        │   └───__pycache__
        │   │
        │   ├───asgi.py
        │   ├───__init__.py
        │   ├───settings.py
        │   ├───urls.py
        │   └───wsgi.py
        │
        └───drive
            │
            └───__pycache__
            │
            └───migrations
            │
            └───static
                │
                └───drive
                    │
                    └───css
                    │
                    └───js
            │
            └───templates
    │
    ├───__init__.py
    ├───admin.py
    ├───apps.py
    ├───forms.py
    ├───models.py
    ├───tests.py
    ├───urls.py
    ├───views.py
    │
    └───media
    │
    └───db.sqlite3
    │
    └───manage.py
    │
    └───requirements.txt
    │
    └───venv
        │
        └───Include
        │
        └───Lib
        │
        └───Scripts
        │
        └───pyvenv.cfg
    │
    └───README.md
    │
    └───requirements.txt


```

## Installation

1. *Telecharger le dossier du projet et Déziper :*

   Ouvrir le dossier sur Vscode puis dans le terminal executer la commande suivante


   ```bash
    cd Project_django_real (3)\Project_django_real\projet_django\
    ```

2. *Créer un environnement virtuel :*
   
    Sur macOS/Linux :
    ```bash
    python -m venv env
    source env/bin/activate
    ```
    Sur Windows : 
    ```bash
    python -m venv env
    env\Scripts\activate
    ```

3.  Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

4.  Se déplacer dans le projet :
    ```bash
    cd Project_django_real (3)\Project_django_real\projet_django\cloud_drive
    ```

5. *Effectuer les migrations :*
 Avant de lancer le projet, exécutez les migrations pour configurer la base de données :
    ```bash
    python manage.py migrate
    ```
6. *Lancer le projet :*
  Pour démarrer le serveur de développement :
    ```bash
    python manage.py runserver
    ```
 Le projet sera accessible à l'adresse http://127.0.0.1:8000/.
    
    Exemple d'un compte créé: 
      
     Nom d'utilisateur: kenneth
     Mots de Passe: Kingdu97

