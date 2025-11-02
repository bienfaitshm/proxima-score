import wx
import wx.dataview as dv
import wx.lib.masked as masked
from typing import List, Dict, Any, Tuple, Optional
from components.panels import PointAllocatorFrame

# Fichiers de logique métier (supposés exister dans le même répertoire)
# Assurez-vous d'avoir ces fichiers, car ils ne faisaient pas partie du code fourni.
try:
    from data import DataHandler
    from services import PointAllocatorLogic, ROUNDING_OPTIONS
except ImportError:
    # Création de stubs pour que le code puisse être analysé
    ROUNDING_OPTIONS = {"Mode 1": "mode1", "Mode 2": "mode2"}

    class DataHandler:
        def load_data(self) -> List: return []
        def save_data(self, data: List): pass

        def get_total_weight(self, courses: List) -> float:
            return sum(c.get('weight', 0) for c in courses)

    class PointAllocatorLogic:
        def calculate_best_distribution(self, *args, **kwargs) -> Tuple[str, Dict]:
            return "Mode 1", {"final_results": {"data": {"results": {}, "global_percentage_achieved": 0.0, "required_total_float": 0.0}, "final_int": 0, "error_margin": 0.0}}

        def calculate_margin(self, *args, **kwargs) -> List: return []

# Constantes
ROUNDING_OPTIONS_KEYS = list(ROUNDING_OPTIONS.keys())
ROUNDING_CHOICES = ROUNDING_OPTIONS_KEYS  # Pour les wx.Choice


class PointAllocatorController:
    def __init__(self, app: wx.App):
        self.data_handler = DataHandler()
        self.logic = PointAllocatorLogic()
        self.courses = self.data_handler.load_data()
        self.last_results: Dict[str, Any] = {}

        self.app_view = PointAllocatorFrame(self)
        self.app_view.update_all_views(self.courses)

    def add_course(self, name: str):
        name = name.strip()
        weight_value = self.app_view.management_panel.get_course_weight_value()

        if not name or weight_value <= 0:
            self.app_view.show_error(
                "Nom du cours requis et pondération doit être positive.", False)
            return

        if any(c['name'].lower() == name.lower() for c in self.courses):
            self.app_view.show_error(f"Le cours '{name}' existe déjà.", False)
            return

        self.courses.append({
            "name": name,
            "weight": weight_value,
            "score_actuel": 0.0,
            "min_pct_cible": 0.0,
            "points_deliberes": 0.0
        })
        self.data_handler.save_data(self.courses)
        self.app_view.clear_add_inputs()
        self.app_view.update_all_views(self.courses)

    def delete_course(self, selected_index: int):
        if selected_index == -1:
            wx.MessageBox("Veuillez sélectionner un cours à supprimer.",
                          "Aucune sélection", wx.OK | wx.ICON_INFORMATION)
            return

        course_name_to_delete = self.courses[selected_index]['name']

        confirm = wx.MessageDialog(
            None, f"Êtes-vous sûr de vouloir supprimer '{course_name_to_delete}' ?",
            'Confirmation de Suppression', wx.YES_NO | wx.ICON_QUESTION
        )
        if confirm.ShowModal() == wx.ID_YES:
            del self.courses[selected_index]
            self.data_handler.save_data(self.courses)
            self.app_view.update_all_views(self.courses)
            wx.MessageBox(f"Le cours '{course_name_to_delete}' a été supprimé.",
                          "Suppression", wx.OK | wx.ICON_INFORMATION)
        confirm.Destroy()

    def update_course_data(self, course_obj: Dict[str, Any], score: float, min_pct: float, deliberated: float):
        """Met à jour le modèle (la validation a déjà eu lieu dans la vue)."""
        course_obj['score_actuel'] = score
        course_obj['min_pct_cible'] = min_pct
        course_obj['points_deliberes'] = deliberated

        self.data_handler.save_data(self.courses)
        self.app_view.update_all_views(self.courses)

    def calculate_scores(self):
        if not self.courses:
            self.app_view.show_error(
                "Veuillez ajouter au moins un cours.", True)
            return

        target_percentage = self.app_view.calculation_panel.get_target_value()
        random_enabled = self.app_view.calculation_panel.random_mode_cb.GetValue()
        random_intensity = self.app_view.calculation_panel.get_random_intensity_value()
        ignore_constraints = self.app_view.calculation_panel.get_ignore_constraints()
        selected_mode = self.app_view.calculation_panel.get_rounding_mode()

        try:
            # Note: La logique de 'calculate_best_distribution' devrait être
            # mise à jour pour accepter 'selected_mode' et l'utiliser si
            # l'optimisation n'est pas souhaitée, ou l'utiliser comme un des modes à tester.
            # Pour l'instant, nous suivons l'ancienne logique.
            best_mode_name, results_summary = self.logic.calculate_best_distribution(
                self.courses, target_percentage, random_enabled,
                random_intensity, ignore_constraints, [selected_mode]
            )

            final_results = results_summary['final_results']
            results_data = final_results['data']

        except ValueError as e:
            self.app_view.show_error(str(e))
            return
        except Exception as e:
            self.app_view.show_error(f"Erreur de calcul inattendue: {e}")
            return

        self.last_results = results_data

        # Ajout du nom du mode optimal aux résultats pour l'affichage
        final_results['optimal_mode_name'] = best_mode_name

        self.app_view.update_all_views(
            self.courses, results_data['results'], final_results)


# --------------------------------------------------
# --- 6. LANCEMENT DE L'APPLICATION ---
# --------------------------------------------------

class PointAllocatorApp(wx.App):
    def OnInit(self):
        self.controller = PointAllocatorController(self)
        return True


if __name__ == "__main__":
    try:
        app = PointAllocatorApp(False)
        app.MainLoop()
    except AttributeError as e:
        print(
            f"Erreur: Une classe ou méthode de wxPython est introuvable. "
            f"Avez-vous installé wxPython, wx.lib.masked, et wx.dataview? Détails: {e}")
    except ImportError as e:
        print(
            f"Erreur: Impossible d'importer un module (data_handler ou point_allocator_logic?). Détails: {e}")
    except Exception as e:
        print(f"Erreur inattendue lors de l'exécution: {e}")
