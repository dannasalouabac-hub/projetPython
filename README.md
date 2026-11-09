# LOG ANALYSIS

Le projet a pour objectif de présenter, sous forme de graphiques, les tentatives de connexion au réseau d'ESISA, en précisant, pour chaque pays, le nombre de tentatives de connexion échouées à partir de deux événements principaux :

- Failed password
- Invalid user

En plus de cela, il faut également afficher le nombre de connexions réussies au réseau à l'aide de l'événement :

- Accepted password

Puisque notre projet est un projet orienté Data, nous allons nous baser sur une architecture composée de cinq phases importantes :

- DATA
- INGESTION
- PROCESSING
- STORAGE
- SERVING

Nous allons préciser les modules et les fonctions utilisés dans chacune de ces phases.

# PHASE 1 : DATA

Afin de réaliser notre projet, il est nécessaire de disposer de fichiers d'entrée sur lesquels nous allons effectuer plusieurs opérations.

Pour cela, nous disposons de quatre fichiers de données :

- Deux fichiers texte : auth.log.1 et auth.log.2.
- Deux fichiers compressés au format GZIP : auth.log.3.gz et auth.log.4.gz.

Chaque fichier contient toutes les informations nécessaires à la réalisation du projet. Ces informations sont réparties sur six colonnes :

- 1ère colonne : le mois.
- 2ème colonne :le jour.
- 3ème colonne :l'heure au format h/m/s.
- 4ème colonne :le nom du serveur.
- 5ème colonne :le service ayant généré le log.
- 6ème colonne :le message décrivant le résultat de l'opération.

Pour notre projet, nous nous intéresserons uniquement à quatres éléments : le mois, le jour,l'heure et le message.


# PHASE 2 : INGESTION

Cette phase consiste à lire les différents fichiers de données en fonction de leur format.

Après avoir identifié les fichiers sur lesquels nous allons travailler, nous devons les lire ligne par ligne.

Pour cela, nous avons créé un module nommé read, contenant la fonction ingest, qui prend en entrée le dossier data et retourne une liste contenant les lignes de chaque fichier.

Dans cette fonction, nous avons importé trois modules :

- gzip :pour lire les fichiers compressés au format GZIP.
- os :pour effectuer différentes opérations sur les fichiers et les dossiers.
- os.path :pour faciliter la manipulation des chemins d'accès.

Dans notre fonction, nous utilisons deux méthodes d'ouverture selon le type du fichier :
- gzip.open pour les fichiers compressés au format .gz.
- open pour les fichiers texte classiques.

Enfin, cette fonction retourne une liste contenant les lignes extraites des différents fichiers.

# PHASE 3 : PROCESSING

Cette phase est constituée de quatre opérations essentielles :

- Cleaning.
- Filtrage.
- Transformation.
- Validation.

Pour notre projet, nous avons tout d'abord besoin de connaître les informations associées à chaque adresse IP.

Pour cela, nous avons créé un module nommé geolocation, contenant la fonction geo_location, qui prend en paramètre une adresse IP et retourne les informations géographiques qui lui sont associées en utilisant le service IPinfo.

Ce service permet de rechercher différentes informations relatives à une adresse IP, notamment le pays, la ville, etc. Cependant, il nécessite un token d'authentification pour permettre l'accès à ses fonctionnalités.

Dans cette fonction, plusieurs vérifications sont effectuées afin de s'assurer de la validité des résultats. Elle retourne uniquement le pays et la ville associés à l'adresse IP fournie.

Afin d'extraire les informations dont nous avons besoin, nous avons créé un deuxième module nommé extract_transform, contenant la fonction extract.

Cette fonction prend en entrée une ligne, recherche les éléments concernés (le mois, le jour et le message), puis extrait le message contenant l'un des événements qui nous intéressent : Failed password, Invalid user ou Accepted password.

Après avoir créé ces deux modules, nous avons ajouté un troisième module nommé analyze, contenant la fonction process_rows.

Un utilisateur qui tente de se connecter au réseau peut être un humain ou un robot (bot). Nous pouvons distinguer ces deux types d'utilisateurs en fonction de l'intervalle de temps entre les tentatives de connexion : si cet intervalle est inférieur à trois secondes, la tentative est considérée comme étant effectuée par un robot.

Cette fonction nous permet d'identifier quatre éléments :

1. Le nombre total de messages contenant l'événement Failed password.
2. Le nombre total de messages contenant l'événement Invalid user.
3. Le nombre total de messages contenant l'événement Accepted password.
4. Le type d'utilisateur effectuant la tentative de connexion : humain ou robot.

Enfin, elle retourne une liste de tuples contenant les informations suivantes : la date, l'heure, l'événement, l'adresse IP, le type d'utilisateur, la ville, le pays et le nom d'utilisateur.

# PHASE 4 : STORAGE

Cette phase consiste à stocker les résultats obtenus afin de pouvoir les exploiter ultérieurement.

Le SGBD utilisé dans notre projet est PostgreSQL, choisi pour ses performances et ses fonctionnalités.

Pour cela, nous avons créé un module nommé database.

Dans ce module, nous avons importé un nouveau module, psycopg2, qui assure la connexion entre Python et PostgreSQL.

Nous avons également créé une fonction nommée save_events, qui prend en entrée la liste de tuples générée par la fonction process_rows et exécute deux requêtes principales :

- Première requête :création de la table auth_events, dans laquelle nous allons stocker les informations.
- Deuxième requête : insertion de tous les résultats obtenus grâce à la fonction process_rows.

Entre ces deux requêtes, une troisième opération permet de vérifier que la colonne username a bien été créée.

Après l'installation du SGBD, nous avons configuré le nom d'utilisateur (username) et le mot de passe (password) nécessaires à la connexion. Enfin, nous avons créé le serveur qui hébergera notre base de données.

# PHASE 5 : SERVING

Dans cette phase, nous devons afficher les différents tableaux de bord (dashboards) correspondant aux résultats obtenus. Ils sont au nombre de trois :

1. Dashboard des tentatives de connexion échouées

Le premier dashboard permet d'afficher, pour chaque pays, le nombre d'événements de type Failed password et Invalid user.

Il est assuré par le module dashboard, qui contient deux fonctions :

- Première fonction :fetch_country_counts

  Cette fonction récupère les informations stockées dans la base de données et retourne une liste de tuples contenant le pays ainsi que le nombre d'événements Failed password et Invalid user pour chaque pays. Les résultats sont classés par ordre décroissant selon la somme des deux nombres obtenus.

- Deuxième fonction :show_dashboard

  Cette fonction affiche une figure Matplotlib avec les 20 pays ayant le plus d'événements et un message au centre du graphique lorsqu'aucune donnée n'est disponible.

 2. Dashboard des types d'utilisateurs

Le deuxième dashboard permet d'afficher, pour chaque pays, le nombre de tentatives de connexion effectuées par des utilisateurs humains et des robots.

Il est assuré par le module actor_dashboard, qui contient également deux fonctions :

- Première fonction :fetch_country_actor_counts

  Cette fonction récupère les informations stockées dans la base de données et retourne une liste de tuples contenant le pays ainsi que le nombre de tentatives effectuées par des utilisateurs humains et des robots pour chaque pays. Les résultats sont classés par ordre décroissant selon la somme des deux nombres obtenus.

- Deuxième fonction :show_dashboard

  Cette fonction affiche une figure Matplotlib avec les 20 pays ayant le plus d'événements et un message au centre du graphique lorsqu'aucune donnée n'est disponible.

 3. Dashboard des connexions réussies

Le troisième dashboard permet d'afficher les noms des utilisateurs qui se sont connectés avec succès au serveur de l'école.

Il est assuré par le module successful_user_dashboard, qui contient à son tour deux fonctions :

- Première fonction :fetch_successful_connection_counts

  Cette fonction récupère les informations stockées dans la base de données et retourne une liste de tuples contenant le nom de chaque utilisateur ainsi que son nombre de connexions réussies.

- Deuxième fonction :show_dashboard

  Cette fonction affiche une figure Matplotlib à partir des résultats retournés par la première fonction. Elle affiche également un message au centre du graphique lorsqu'aucune donnée n'est disponible.

Afin d'assurer le fonctionnement des différentes fonctions, nous avons importé cinq modules :

- os :pour lire les variables d'environnement.
-pathlib :pour faciliter la manipulation des chemins d'accès.
- webbrowser : pour ouvrir automatiquement les différents fichiers SVG dans le navigateur.
- matplotlib.pyplot : pour construire les graphiques avec Python.
- psycopg2 : pour assurer la connexion entre PostgreSQL et Python.

Afin d'exécuter toutes les fonctions, nous avons eu recours au module main, dans lequel nous avons créé une fonction main qui appelle toutes les fonctions dans un ordre précis : lecture des fichiers, extraction des informations nécessaires, traitement des données, stockage des résultats et, enfin, affichage des différents dashboards.

Les adresses IP associées aux résultats UNKNOWN ou NOT FOUND sont exclues de l'affichage.

Enfin, pour exécuter le programme, il faut déclarer une variable d'environnement nommée DATABASE_URL, qui contient l'URL de connexion à la base de données.