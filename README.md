# Objet du dépôt

Ce dépôt correspond à mon premier projet Python après avoir suivi les cours en ligne d'OpenClassroom :

- [Mettez en place votre environnement Python](https://openclassrooms.com/fr/courses/6951236-mettez-en-place-votre-environnement-python)
- [Apprenez les bases du langage Python](https://openclassrooms.com/fr/courses/7168871-apprenez-les-bases-du-langage-python/7289381-tirez-un-maximum-de-ce-cours)

Dans le dernier exercice on procéde à la réalisation d'un ETL *(Extract, Transform, Load)* ce qui m'a donné l'idée d'en faire un pour mon usage personnel.

Effectivement je lis chaque jour des articles sur l'informatique, et bien souvent j'ai besoin d'y revenir ultérieurement afin de retrouver une information. Je suis parti de ce constat comme base de ce projet relativement simple ; pour des usages plus avancés il convient effectivement de l'adapter et/ou d'utiliser des framework comme [Scrapy](https://scrapy.org/). Il s'agit surtout d'une base d'entrainement afin de reprendre le Python que j'avais délaissé depuis mes études *(en version 2.7 !)*.

# Les grandes lignes du programme etl.py
Le programme fonctionne avec des processus ce qui permet de paralléliser le traitement de chaque site qui m'intéresse.
J'envisageais au début l'utilisation de thread puis en me renseignant plus en détail et en effectuant des tests je me suis rendu compte que **dans ce cas précis** les processus sont plus efficaces.
Chaque site a sa propre fonction comme les sélections dans le document HTML diffèrent, mais j'ai essayé de mettre en commun le plus d'éléments possible. Globalement chaque site est ainsi traité :
1. Requête pour récupérer l'accueil
2. Formater la réponse avec BeautifulSoup afin de profiter de l'API pour sélectionner facilement du contenu
3. Persister les données dans MongoDB

Seul l'accueil est récupéré car j'envisage de faire fonctionner ce programme chaque jour avec [cron](https://doc.ubuntu-fr.org/cron) sur l'une de mes machines Linux ; ainsi je suis à peu près sûr de ne rater aucun article (ou il faudrait en avoir publié un paquet) :wink: