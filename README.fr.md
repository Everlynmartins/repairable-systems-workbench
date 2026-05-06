Atelier Visuel pour Systèmes Réparables

Vue d’ensemble

Repairable Systems Visual Workbench est une application de bureau indépendante pour l’analyse exploratoire de la fiabilité des systèmes réparables. Elle fournit une interface visuelle pour saisir des données de défaillance, ajuster un modèle de Processus en Loi de Puissance, générer des graphiques de diagnostic et exporter des résultats statistiques.

Ce projet est une implémentation logicielle indépendante fondée sur des méthodes statistiques publiques pour les processus NHPP, la modélisation par Processus en Loi de Puissance et l’analyse de croissance de fiabilité. Il ne s’agit pas d’une publication officielle, d’une approbation, d’une certification ni d’un outil validé par une organisation normative, un éditeur ou une institution tierce.

Fonctionnalités principales

1. Saisie visuelle des données avec des tableaux de type feuille de calcul
2. Prise en charge des données pour un élément unique, plusieurs éléments avec un horizon commun d’observation, plusieurs éléments avec des horizons d’observation différents et des données groupées par intervalle
3. Estimation de beta, lambda et de l’intensité de défaillance z(t)
4. Graphiques des défaillances cumulées, graphiques log log, graphiques QQ, graphiques TTT et graphiques d’intensité
5. Bandes de confiance fondées sur le bootstrap pour les courbes du modèle lorsque cette option est activée
6. Évaluation de l’adéquation par simulation de Cramer von Mises
7. Exportation des graphiques et des résumés statistiques
8. Prise en charge d’une interface multilingue

Noyau mathématique

L’application implémente la forme du Processus en Loi de Puissance

Lambda(t) = lambda t^beta

z(t) = lambda beta t^(beta moins 1)

Les valeurs critiques de Cramer von Mises sont calculées par simulation Monte Carlo au moment de l’exécution. Le programme ne contient pas de tables reproduites de valeurs critiques. À chaque simulation, des échantillons uniformes ordonnés sont générés, le paramètre relatif de forme est réestimé, la statistique de Cramer von Mises est calculée et le quantile demandé est utilisé comme seuil critique.

Les limites de confiance pour z(t) sont calculées à partir d’approximations analytiques et de procédures bootstrap, selon l’option sélectionnée. Aucune tabulation intégrée n’est utilisée pour ces calculs.

Exemples de données

Les exemples intégrés sont synthétiques et générés uniquement pour la démonstration du logiciel. Ils ne sont copiés d’aucune publication protégée ni d’aucune source de données propriétaire.

Structure du projet

run_workbench.py
    Point d’entrée principal utilisé pour démarrer l’application.

repairable_workbench/i18n.py
    Texte de l’interface, traductions, libellés et dictionnaires de langue.

repairable_workbench/math_core.py
    Estimation statistique, ajustement de modèle, calculs d’adéquation, intervalles de confiance, routines bootstrap et génération de valeurs critiques par Monte Carlo.

repairable_workbench/results.py
    Conteneurs de résultats et résumés statistiques formatés.

repairable_workbench/plotting.py
    Utilitaires de préparation des graphiques et prise en charge des courbes du modèle.

repairable_workbench/resources.py
    Importation, exportation, sauvegarde, exemples synthétiques et ressources auxiliaires.

repairable_workbench/ui_components.py
    Composants visuels réutilisables, y compris des tableaux de données de type feuille de calcul.

repairable_workbench/visual.py
    Interface graphique principale et disposition de l’application.

Installation

Python 3.10 ou une version plus récente est recommandé.

Installez les paquets requis avec

pip install numpy scipy matplotlib

Exécution de l’application

Depuis le dossier du projet, exécutez

python run_workbench.py

Exemple Windows

cd "C:\Users\Windows\Documents\Projects\modular_workbench_v3"
C:\Users\Windows\AppData\Local\Programs\Python\Python313\python.exe .\run_workbench.py

Si le fichier ZIP crée un dossier imbriqué, entrez dans le dossier interne qui contient run_workbench.py et le répertoire repairable_workbench avant d’exécuter la commande.

Changement principal récent

Le principal fichier modifié dans cette version est

repairable_workbench/math_core.py

L’ancienne logique fondée sur une table fixe pour le seuil de Cramer von Mises a été remplacée par la génération de valeurs critiques par Monte Carlo.

Notes de publication

Ce dépôt est destiné à un logiciel indépendant à vocation éducative et d’ingénierie. Avant une publication publique, évitez d’ajouter du texte protégé, des tables reproduites, des captures d’écran, des figures, des logos ou des exemples copiés de normes commerciales, de livres, de manuels ou de rapports internes propriétaires.

Noms recommandés pour le dépôt

repairable_systems_workbench
nhpp_reliability_workbench
power_law_process_workbench

Description courte suggérée pour le dépôt

Atelier visuel indépendant pour l’analyse de fiabilité des systèmes réparables utilisant des méthodes NHPP et Processus en Loi de Puissance.

Licence

Ajoutez un fichier de licence avant de publier le projet. Pour une publication publique en code ouvert, les options courantes sont MIT, BSD 3 Clause, Apache 2.0 ou GPL 3.0, selon le niveau de permissivité souhaité pour les conditions de réutilisation.