# CHANGELOG


## v0.1.0 (2025-10-31)

### Bug Fixes

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
