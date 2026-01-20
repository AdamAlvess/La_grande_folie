# La Grande Folie

Voici le fonctionnement de notre jeu de ferme réalisé dans le cadre du cours de programmation orientée objet (POO).

Le principe est de concevoir une ferme qui fonctionne de manière automatique et évolue afin de faire face aux intempéries ainsi qu’aux conditions de travail difficiles.

La gestion repose sur la génération de revenus grâce à la culture de légumes, leur stockage, la préparation de soupe et la vente de la production.

Nous devont également gérer les employés et le matériel disponible, notamment les tracteur afin d'être rentable, et de survivre le plus longtemps possible.

Pour notre fonctionnement, nous utilisons UV, un outil permettant de gérer l’environnement Python et d’exécuter les commandes du projet de manière isolée et reproductible.

Nous disposons donc des commandes suivantes :
- uv run python -m ferme.minimal_logiciel                       --> lancer le client
- uv run python "commande indiquée dans le README Chronobios"   --> lancer le serveur
- uv run python launch.py                                       --> lancer l’ensemble du projet en même temps

On utilise GitHub action. A chaque push de la branche Tests, tout les test sont éffectués. A la fin, un mail de rapport des tests est envoyé.
