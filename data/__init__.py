import json
import os
from typing import List, Dict, Any


class DataHandler:
    """
    Gère la persistance des données (cours) via un fichier JSON.
    """

    FILE_NAME = 'courses_data.json'

    def load_data(self) -> List[Dict[str, Any]]:
        """Charge les données des cours depuis le fichier JSON."""
        if not os.path.exists(self.FILE_NAME):
            return []
        try:
            with open(self.FILE_NAME, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(
                f"Avertissement: Fichier {self.FILE_NAME} corrompu. Retourne une liste vide.")
            return []
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            return []

    def save_data(self, courses: List[Dict[str, Any]]):
        """Sauvegarde les données des cours dans le fichier JSON."""
        try:
            with open(self.FILE_NAME, 'w', encoding='utf-8') as f:
                json.dump(courses, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données: {e}")

    def get_total_weight(self, courses: List[Dict[str, Any]]) -> float:
        """Calcule la pondération totale maximale de tous les cours."""
        return sum(c['weight'] for c in courses)

# --- FIN data_handler.py ---
