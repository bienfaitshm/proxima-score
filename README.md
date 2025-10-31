# 🌟 Proxima Score : Naviguez vers votre Objectif


[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/votre_utilisateur/proxima-score/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-wxPython-informational)](https://www.wxpython.org/)

## 🎯 Description du Projet

**Proxima Score** est un outil de simulation et d'optimisation conçu pour aider les étudiants et les jurys académiques à planifier et atteindre un pourcentage global de réussite cible. Son nom s'inspire de **Proxima du Centaure**, symbolisant la recherche du chemin le plus court et le plus précis vers l'objectif.

L'application permet de distribuer de manière algorithmique les points restants à gagner ou les points de délibération nécessaires à travers les différents cours, en tenant compte de la pondération de chaque matière et des objectifs de réussite minimaux.

| Contexte | Fonction Principale |
| :--- | :--- |
| **Simulation Étudiante** | Calculer l'effort (les points à gagner) pour atteindre un % global cible et identifier où concentrer les efforts. |
| **Délibération du Jury** | Déterminer la distribution minimale et optimale de points délibérés nécessaires pour faire réussir un étudiant au seuil requis. |

---

## ✨ Fonctionnalités Clés

* **Gestion des Cours :** Ajout, modification et suppression de cours avec leurs pondérations maximales, scores actuels et pourcentages cibles minimaux.
* **Calcul Cible :** Entrée d'un **pourcentage global cible** (ex: 85%) pour déterminer le nombre total de points restants à obtenir.
* **Optimisation de la Distribution :** Répartition intelligente des points nécessaires sur les différents cours, pondérée par leur importance relative.
* **Modes Avancés :**
    * **Simulation Pure :** Permet d'ignorer les contraintes de pourcentage minimal par cours pour tester des scénarios extrêmes.
    * **Variabilité Aléatoire :** Ajoute une petite variation aux résultats pour simuler des scénarios "au cas où".
* **Rapports Détaillés :** Visualisation de la marge de manœuvre (points de perte tolérés) par cours pour atteindre le minimum ciblé.
* **UX/UI Améliorée :** Utilisation de `wx.lib.masked.NumCtrl` pour garantir la saisie de données numériques valides et précises.

---

## ⚙️ Installation et Démarrage

Ce projet nécessite Python 3.x et la librairie `wxPython`.

### Prérequis

```bash
python3 -m pip install wxPython
python3 -m pip install wx.lib.masked
```

### Exécution du Projet

1.  **Cloner le dépôt :**

    ```bash
    git clone [https://github.com/votre_utilisateur/proxima-score.git](https://github.com/votre_utilisateur/proxima-score.git)
    cd proxima-score
    ```

2.  **S'assurer de la structure du code :**

      * Le code principal (`main.py` ou le fichier contenant la classe `PointAllocatorController`)
      * Le module `data_handler.py` (pour la persistance JSON)
      * Le module `point_allocator_logic.py` (pour les calculs d'optimisation)

3.  **Lancer l'application :**

    ```bash
    python3 main.py
    ```



## 🏗️ Architecture et Composants

Le projet est strictement architecturé selon le modèle **Modèle-Vue-Contrôleur (MVC)** pour garantir la modularité et la maintenabilité.

### Modèle (Logique et Données)

  * **`data_handler.py` :** Gère la persistance des données (cours, scores, pondérations) dans un fichier JSON.
  * **`point_allocator_logic.py` :** Contient les algorithmes d'optimisation (calcul de la distribution, application de l'arrondi, calcul de la marge).

### Vue (Interface Utilisateur)

Développée avec **wxPython** et utilise des composants réutilisables (e.g., `NumericInput`, `BaseDataView`, `GroupBox`) pour une interface cohérente et professionnelle :

  * `PointAllocatorFrame` : La fenêtre principale (le conteneur).
  * `CourseManagementPanel` : Gestion de la liste des cours (DataView).
  * `CalculationPanel` : Saisie des objectifs et affichage des résultats optimisés.
  * `ReportPanel` : Rapports détaillés sur les marges et les erreurs d'arrondi.

### Contrôleur (Cœur de Liaison)

  * `PointAllocatorController` : Fait le lien entre les actions de l'utilisateur (Vue) et les opérations logiques (Modèle), puis met à jour l'affichage.

-----

## 🤝 Contribution

Les contributions sont les bienvenues \! Si vous souhaitez améliorer l'algorithme d'optimisation, ajouter des fonctionnalités UX/UI spécifiques au contexte RDC (comme le support d'autres langues locales ou des systèmes de notation spécifiques), veuillez :

1.  Faire un Fork de ce dépôt.
2.  Créer une nouvelle branche (`git checkout -b feature/AmazingFeature`).
3.  Commiter vos changements (`git commit -m 'Add some AmazingFeature'`).
4.  Pousser vers la branche (`git push origin feature/AmazingFeature`).
5.  Ouvrir une Pull Request.

-----

## 📜 Licence

Distribué sous la Licence MIT. Voir `LICENSE` pour plus d'informations.

-----

## 🧑‍💻 Auteur

**BIENFAIT SHOMARI**

  * **Lieu :** Lubumbashi, Haut-Katanga, RDC
  * **Contact :** bienfaitshm@gmail.com