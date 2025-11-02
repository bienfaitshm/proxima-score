
from typing import Dict

# Les options d'arrondi disponibles


ROUNDING_OPTIONS: Dict[str, str] = {
    "Arrondi Classique (Optimal)": 'NONE',
    "Arrondi Plafond (Conservateur)": 'CEILING',
    "Arrondi Plancher (Agressif)": 'FLOOR'
}

ROUNDING_OPTIONS_KEYS = list(ROUNDING_OPTIONS.keys())
ROUNDING_CHOICES = ROUNDING_OPTIONS_KEYS
