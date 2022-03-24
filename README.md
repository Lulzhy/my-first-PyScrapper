# Objet du dépôt

Ce dépôt correspond à mon premier projet Python après avoir suivi les cours en ligne d'OpenClassroom :

- [Mettez en place votre environnement Python](https://openclassrooms.com/fr/courses/6951236-mettez-en-place-votre-environnement-python)
- [Apprenez les bases du langage Python](https://openclassrooms.com/fr/courses/7168871-apprenez-les-bases-du-langage-python/7289381-tirez-un-maximum-de-ce-cours)

Dans le dernier exercice on procéde à la réalisation d'un ETL *(Extract, Transform, Load)* ce qui m'a donné l'idée d'en faire un pour mon usage personnel.

Effectivement je lis chaque jour des articles sur l'informatique, et bien souvent j'ai besoin d'y revenir ultérieurement afin de retrouver une information. Je suis parti de ce constat comme base de ce projet relativement simple ; pour des usages plus avancés il convient effectivement de l'adapter et/ou d'utiliser des framework comme [Scrapy](https://scrapy.org/). Il s'agit surtout d'une base d'entrainement afin de reprendre le Python que j'avais délaissé depuis mes études *(en version 2.7 !)*.

# Les grandes lignes du programme etl.py
1. Récupérer l'accueil du blog de Manuel Dorne, alias [Korben](https://korben.info/) au format HTML brut
2. Parser grâce à [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) ce html afin de pouvoir en extraire des morceaux
3. Extraire les titres des articles de blog afin d'en obtenir le texte et l'URL
4. Sauvegarder les données dans une base MongoDB

Ici un seul site est traité mais il est assez facile d'adapter `etl.py` afin de fournir une liste d'URL à extraire et de sélecteurs CSS pour compléter la base.

Je fais tourner ce programme automatiquement chaque jour sur un serveur Linux avec [cron](https://doc.ubuntu-fr.org/cron). Je n'ai pas besoin de contrôler qu'un article soit déjà présent en base grâce à l'utilisation d'un index unique sur l'URL ; MongoDB retourne une erreur en cas de doublon et le programme se fini. Comme il n'y a pas de gestion de transaction, seuls les nouveaux articles sont ajoutés. Enfin le fonctionnement de ce programme suppose que Korben ne publie pas une dizaine d'articles par jour :wink: en effet seul les articles de la **première page** sont extraits.

# A venir
Je vais essayer de mettre en place l'utilisation de threads afin de paralléliser certaines fonctions qui n'ont pas besoin d'être synchrones. Une fois le programme à mon goût, ajout du requirements.txt et de derniers détails dans le README.