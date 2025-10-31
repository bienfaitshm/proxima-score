# CHANGELOG


## v0.2.0 (2025-10-31)

### Bug Fixes

- Retirer ubuntu-latest de la matrice des systèmes d'exploitation pour le build
  ([`64f8905`](https://github.com/bienfaitshm/proxima-score/commit/64f8905b6b613279a8abc32705baa7b01da50bf0))

### Features

- Ajouter l'installation des dépendances système nécessaires pour wxPython sur Linux
  ([`2656c91`](https://github.com/bienfaitshm/proxima-score/commit/2656c9157bd46dd4faf17e10fe2dc8535949686a))

- Ajouter l'option --noconsole à PyInstaller pour construire l'exécutable sans console
  ([`cb604cf`](https://github.com/bienfaitshm/proxima-score/commit/cb604cfc285a4ead80344fd77ff53d7c35e039a0))

### Refactoring

- Simplifier l'étape de publication avec python-semantic-release et ajuster la condition de version
  ([`e11318b`](https://github.com/bienfaitshm/proxima-score/commit/e11318b093c3e147a5b74f355766eedb89c48a4c))


## v0.1.0 (2025-10-31)

### Bug Fixes

- Mettre à jour la description du projet dans README.md et pyproject.toml
  ([`2d1dc60`](https://github.com/bienfaitshm/proxima-score/commit/2d1dc60543efa50961074992c2887a84f7268ce8))

- Mettre à jour la version de python-semantic-release à v9 dans le workflow de release
  ([`ff8a622`](https://github.com/bienfaitshm/proxima-score/commit/ff8a622aee3e131af5ae3d48cc0f52f735dded33))

### Features

- Ajouter le fichier pyproject.toml pour la configuration du projet
  ([`5788ea7`](https://github.com/bienfaitshm/proxima-score/commit/5788ea76d8201e8225b2e706b4a688f667353646))

- Ajouter un workflow de release GitHub avec configuration Python et publication sémantique
  ([`fbe0925`](https://github.com/bienfaitshm/proxima-score/commit/fbe0925b39875b690b56d0869680fc9edcd4d4d8))

- Implement PointAllocatorLogic for point distribution and analysis
  ([`85eb096`](https://github.com/bienfaitshm/proxima-score/commit/85eb096c0c343838dd965fcc75a1cc4f4396fca2))

- Added PointAllocatorLogic class to handle the business logic for distributing points across
  courses. - Implemented methods for applying rounding, distributing integer points, and calculating
  the best distribution based on various rounding modes. - Introduced a margin calculation method to
  assess tolerance for point loss against minimum targets. - Included robust validation to ensure
  constraints are respected during point allocation. - Added support for random variations in point
  distribution to enhance allocation strategies.

- Mettre à jour le workflow de release pour inclure la construction multi-OS et ajouter le fichier
  requirements.txt
  ([`90968cc`](https://github.com/bienfaitshm/proxima-score/commit/90968cc46e2732615d9f60992218d2a02ce4be0c))
