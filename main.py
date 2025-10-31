import wx
import wx.dataview as dv
import wx.lib.masked as masked
from typing import List, Dict, Any, Tuple, Optional

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

# ---------------------------------------------------
# --- 1. COMPOSANTS RÉUTILISABLES (Refactorisés) ---
# ---------------------------------------------------


class TextInput(wx.TextCtrl):
    """Un champ de texte simple."""

    def __init__(self, parent, value="", *args, **kwargs):
        super().__init__(parent, value=value, *args, **kwargs)


class NumericInput(masked.NumCtrl):
    """Un champ numérique masqué et standardisé."""

    def __init__(self, parent, value: float = 0.0, min_val: float = 0.0,
                 max_val: Optional[float] = None, integerWidth: int = 3,
                 fractionWidth: int = 2, *args, **kwargs):

        limit = max_val is not None
        # masked.NumCtrl n'aime pas max=None, mais limited=False fonctionne.
        effective_max = max_val if limit else 0

        super().__init__(
            parent, value=value, min=min_val, max=effective_max,
            limited=limit, integerWidth=integerWidth,
            fractionWidth=fractionWidth, allowNegative=(min_val < 0),
            *args, **kwargs
        )


class PrimaryButton(wx.Button):
    """Un bouton d'action principal avec une police en gras."""

    def __init__(self, parent, label: str, *args, **kwargs):
        super().__init__(parent, label=label, *args, **kwargs)
        self.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))


class DeleteButton(wx.Button):
    """Un bouton pour les actions de suppression."""

    def __init__(self, parent, label: str = "🗑️ Supprimer", *args, **kwargs):
        super().__init__(parent, label=label, *args, **kwargs)
        # Optionnel: Mettre en couleur (peut ne pas s'afficher sur tous les OS)
        # self.SetForegroundColour(wx.Colour(200, 0, 0))


class CheckBox(wx.CheckBox):
    """Un wrapper simple pour wx.CheckBox pour la consistance."""

    def __init__(self, parent, label: str, *args, **kwargs):
        super().__init__(parent, label=label, *args, **kwargs)


class Choice(wx.Choice):
    """Un wrapper simple pour wx.Choice pour la consistance."""

    def __init__(self, parent, choices: List[str], *args, **kwargs):
        super().__init__(parent, choices=choices, *args, **kwargs)
        if choices:
            self.SetSelection(0)


class BaseDataView(dv.DataViewListCtrl):
    """Une vue de données de base qui simplifie la création de colonnes et la mise à jour."""

    def __init__(self, parent, columns: List[Tuple[str, int, int, int]]):
        super().__init__(parent, style=wx.LC_REPORT | wx.BORDER_SUNKEN)

        for name, width, align, flags in columns:
            self.AppendTextColumn(name, width=width, align=align, flags=flags)

    def update_data(self, data: List[List[str]]):
        """Efface et repeuple la liste avec de nouvelles données."""
        self.DeleteAllItems()
        for row in data:
            self.AppendItem(row)


class GroupBox(wx.StaticBoxSizer):
    """Un conteneur simple qui regroupe des widgets sous un titre."""

    def __init__(self, parent, label: str, orientation: int = wx.VERTICAL):
        box = wx.StaticBox(parent, label=label)
        super().__init__(box, orientation)


class TitleText(wx.StaticText):
    """Texte pour un titre principal de panneau (ex: 'À Propos')."""

    def __init__(self, parent, label: str):
        super().__init__(parent, label=label)
        self.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))


class HeaderText(wx.StaticText):
    """Texte pour un sous-titre de section."""

    def __init__(self, parent, label: str):
        super().__init__(parent, label=label)
        self.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

# ---------------------------------------------------
# --- 2. PANNEAUX DE LA VUE (Composés des composants) ---
# ---------------------------------------------------


class CourseManagementPanel(wx.Panel):
    def __init__(self, parent: wx.Notebook, controller: Any):
        wx.Panel.__init__(self, parent)
        self.controller = controller

        vbox = wx.BoxSizer(wx.VERTICAL)

        # --- Panneau d'Ajout ---
        add_box = GroupBox(self, "➕ Ajouter un Nouveau Cours")

        grid = wx.FlexGridSizer(2, 2, 10, 10)
        grid.AddGrowableCol(1)

        self.course_name_entry = TextInput(self)
        self.course_weight_entry = NumericInput(
            self, value=0.0, integerWidth=3, fractionWidth=1
        )

        grid.Add(wx.StaticText(self, label="Nom du Cours:"),
                 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.course_name_entry, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Pondération Max:"),
                 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.course_weight_entry, 1, wx.EXPAND)

        add_box.Add(grid, 0, wx.EXPAND | wx.ALL, 10)

        add_btn = PrimaryButton(self, label="➕ Ajouter le Cours")
        add_btn.Bind(wx.EVT_BUTTON, self._on_add_course)
        add_box.Add(add_btn, 0, wx.ALIGN_RIGHT |
                    wx.TOP | wx.BOTTOM | wx.RIGHT, 10)

        vbox.Add(add_box, 0, wx.EXPAND | wx.ALL, 10)

        # --- Panneau d'Affichage ---
        display_box = GroupBox(self, "Liste des Cours et Données Actuelles")

        self.total_weight_label = wx.StaticText(
            self, label="Pondération Totale Maximale: 0.0")
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.total_weight_label.SetFont(font)
        display_box.Add(self.total_weight_label, 0, wx.TOP |
                        wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 10)

        self.course_list_view = BaseDataView(self, columns=[
            ("Nom du Cours", 250, wx.ALIGN_LEFT, dv.DATAVIEW_COL_RESIZABLE),
            ("Pondération Max", 120, wx.ALIGN_CENTER, 0),
            ("Total Actuel", 120, wx.ALIGN_CENTER, 0),
            ("% Cible Min", 120, wx.ALIGN_CENTER, 0),
        ])

        self.course_list_view.Bind(
            dv.EVT_DATAVIEW_ITEM_ACTIVATED, self._on_edit_course_data_dialog)
        display_box.Add(self.course_list_view, 1, wx.EXPAND)

        delete_btn = DeleteButton(self, label="🗑️ Supprimer Cours Sélectionné")
        delete_btn.Bind(wx.EVT_BUTTON, self._on_delete_course)
        display_box.Add(delete_btn, 0, wx.ALIGN_RIGHT | wx.TOP, 10)

        vbox.Add(display_box, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(vbox)

    def _on_add_course(self, event):
        self.controller.add_course(self.course_name_entry.GetValue())

    def _on_delete_course(self, event):
        selected_index = self.course_list_view.GetSelectedRow()
        self.controller.delete_course(selected_index)

    def _on_edit_course_data_dialog(self, event):
        selected_index = self.course_list_view.GetSelectedRow()
        if selected_index != -1:
            # Délégué à la Frame principale pour montrer la dialogue
            self.controller.app_view.show_edit_course_dialog(
                self.controller.courses[selected_index], selected_index
            )
        event.Skip()

    def get_course_weight_value(self) -> float:
        return self.course_weight_entry.GetValue()

    def update_display(self, courses: List[Dict[str, Any]]):
        total_weight = self.controller.data_handler.get_total_weight(courses)
        self.total_weight_label.SetLabel(
            f"Pondération Totale Maximale: {total_weight:.1f}")

        data_for_view = []
        for course in courses:
            total_actuel = course.get(
                'score_actuel', 0.0) + course.get('points_deliberes', 0.0)
            data_for_view.append([
                course['name'],
                f"{course['weight']:.1f}",
                f"{total_actuel:.1f}",
                f"{course.get('min_pct_cible', 0.0):.1f}%"
            ])
        self.course_list_view.update_data(data_for_view)

    def clear_inputs(self):
        self.course_name_entry.SetValue("")
        self.course_weight_entry.SetValue(0.0)


class CalculationPanel(wx.Panel):
    """Panneau de calcul et de résultats (Onglet 2)."""

    def __init__(self, parent: wx.Notebook, controller: Any):
        wx.Panel.__init__(self, parent)
        self.controller = controller

        main_vbox = wx.BoxSizer(wx.VERTICAL)
        top_grid = wx.FlexGridSizer(1, 2, 10, 10)
        top_grid.AddGrowableRow(0)
        top_grid.AddGrowableCol(0)
        top_grid.AddGrowableCol(1)

        # 1. PARAMÈTRES DE CALCUL (COLONNE GAUCHE)
        params_box = GroupBox(self, "⚙️ Paramètres de Calcul")
        params_inner_grid = wx.FlexGridSizer(5, 2, 10, 10)
        params_inner_grid.AddGrowableCol(1)

        self.target_percentage_ctrl = NumericInput(
            self, value=85.0, max_val=100.0, size=(100, -1)
        )
        self.rounding_mode_choice = Choice(self, choices=ROUNDING_CHOICES)
        self.ignore_constraints_cb = CheckBox(
            self, label="Mode Simulation Pure (Ignorer % Cible Min)"
        )
        self.random_mode_cb = CheckBox(
            self, label="Activer Variabilité Aléatoire"
        )
        self.random_mode_cb.Bind(
            wx.EVT_CHECKBOX, self._on_toggle_random_options)

        self.random_intensity_label = wx.StaticText(
            self, label="Intensité Aléatoire (0.0-0.5):")
        self.random_intensity_ctrl = NumericInput(
            self, value=0.1, max_val=0.5, integerWidth=1, size=(100, -1)
        )

        params_inner_grid.Add(wx.StaticText(
            self, label="Pourcentage Global CIBLE (0-100):"), 0, wx.ALIGN_CENTER_VERTICAL)
        params_inner_grid.Add(self.target_percentage_ctrl, 1, wx.EXPAND)
        params_inner_grid.Add(wx.StaticText(
            self, label="Mode d'Arrondi SUGGÉRÉ/UTILISÉ:"), 0, wx.ALIGN_CENTER_VERTICAL)
        params_inner_grid.Add(self.rounding_mode_choice, 1, wx.EXPAND)
        params_inner_grid.Add(self.ignore_constraints_cb,
                              0, wx.ALIGN_CENTER_VERTICAL)
        params_inner_grid.Add(self.random_mode_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        params_inner_grid.Add(self.random_intensity_label,
                              0, wx.ALIGN_CENTER_VERTICAL)
        params_inner_grid.Add(self.random_intensity_ctrl, 1, wx.EXPAND)

        params_box.Add(params_inner_grid, 1, wx.EXPAND | wx.ALL, 10)
        top_grid.Add(params_box, 1, wx.EXPAND)

        # 2. RÉSULTATS ET ACTION (COLONNE DROITE)
        results_box = GroupBox(self, "✅ Résultats Globaux et Action")

        calculate_btn = PrimaryButton(self, label="CALCULER & OPTIMISER")
        calculate_btn.Bind(wx.EVT_BUTTON, self._on_calculate_scores)
        results_box.Add(calculate_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        result_font = wx.Font(14, wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.result_label = wx.StaticText(
            self, label="Résultat : Entrez une cible et cliquez sur CALCULER.")
        self.result_label.SetFont(result_font)
        self.optimization_label = wx.StaticText(self, label="")

        results_box.Add(self.result_label, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        results_box.Add(self.optimization_label, 0,
                        wx.ALIGN_CENTER | wx.BOTTOM, 10)
        top_grid.Add(results_box, 1, wx.EXPAND | wx.ALL, 10)

        main_vbox.Add(top_grid, 0, wx.EXPAND | wx.ALL, 10)

        # 3. Résultats Détaillés par Cours
        results_box_bottom = GroupBox(self, "📊 Résultats Détaillés par Cours")

        self.course_results_view = BaseDataView(self, columns=[
            ("Cours", 250, wx.ALIGN_LEFT, dv.DATAVIEW_COL_RESIZABLE),
            ("Total Actuel", 120, wx.ALIGN_CENTER, 0),
            ("Pts À GAGNER", 120, wx.ALIGN_CENTER, 0),
            ("% Final", 100, wx.ALIGN_CENTER, 0),
        ])
        results_box_bottom.Add(self.course_results_view, 1, wx.EXPAND)
        main_vbox.Add(results_box_bottom, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(main_vbox)
        self._on_toggle_random_options()

    def _on_calculate_scores(self, event):
        self.controller.calculate_scores()

    def _on_toggle_random_options(self, event=None):
        enable = self.random_mode_cb.GetValue()
        self.random_intensity_label.Enable(enable)
        self.random_intensity_ctrl.Enable(enable)

    def get_target_value(self) -> float:
        return self.target_percentage_ctrl.GetValue()

    def get_random_intensity_value(self) -> float:
        return self.random_intensity_ctrl.GetValue()

    def get_rounding_mode(self) -> str:
        index = self.rounding_mode_choice.GetSelection()
        return ROUNDING_CHOICES[index]

    def get_ignore_constraints(self) -> bool:
        return self.ignore_constraints_cb.GetValue()

    def update_display(self, courses: List[Dict[str, Any]], distributed_scores: Dict[str, int] = None,
                       final_results: Dict[str, Any] = None, total_weight: float = 0.0,
                       target_percentage: float = 0.0, final_mode_name: str = "",
                       ignore_constraints: bool = False):

        if not final_results:
            self.result_label.SetLabel(
                "Résultat : Entrez une cible et cliquez sur CALCULER.")
            self.optimization_label.SetLabel("")
            self.course_results_view.update_data([])
            return

        results_data = final_results['data']
        self.result_label.SetLabel(
            f"🎯 Objectif: {target_percentage:.2f}% | Réussi: {results_data['global_percentage_achieved']:.2f}% "
            f"(Total Pts À GAGNER: {final_results['final_int']})"
        )
        self.optimization_label.SetLabel(
            f"Mode d'Arrondi Optimal: {final_mode_name} | Erreur: {final_results['error_margin']:+.2f} points"
        )

        data_for_view = []
        for course in courses:
            name = course['name']
            weight = course['weight']
            score_actuel = course.get(
                'score_actuel', 0.0) + course.get('points_deliberes', 0.0)

            pts_a_gagner = distributed_scores.get(name, 0)
            total_final = score_actuel + pts_a_gagner
            pct_final = (total_final / weight) * 100 if weight > 0 else 0.0

            data_for_view.append([
                name,
                f"{score_actuel:.1f} / {weight:.1f}",
                str(pts_a_gagner),
                f"{pct_final:.2f}%"
            ])
        self.course_results_view.update_data(data_for_view)


class ReportPanel(wx.Panel):
    def __init__(self, parent: wx.Notebook, controller: Any):
        wx.Panel.__init__(self, parent)
        self.controller = controller

        vbox = wx.BoxSizer(wx.VERTICAL)

        summary_box = GroupBox(self, "📈 Rapport Global et Erreur d'Arrondi")
        self.theoretical_result_label = wx.StaticText(
            self, label="Total Théorique Flottant: N/A\nTotal Entier Attribué: N/A\nErreur d'Arrondi: N/A"
        )
        summary_box.Add(self.theoretical_result_label,
                        0, wx.EXPAND | wx.ALL, 10)
        vbox.Add(summary_box, 0, wx.EXPAND | wx.ALL, 10)

        margin_box = GroupBox(
            self, "📉 Marge de Manœuvre (Points de perte tolérés pour atteindre le % min)")
        self.margin_report_view = BaseDataView(self, columns=[
            ("Nom du Cours", 300, wx.ALIGN_LEFT, dv.DATAVIEW_COL_RESIZABLE),
            ("Pts À GAGNER Alloués", 180, wx.ALIGN_CENTER, 0),
            ("Marge (Pts / %)", 250, wx.ALIGN_CENTER, 0),
        ])
        margin_box.Add(self.margin_report_view, 1, wx.EXPAND)
        vbox.Add(margin_box, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(vbox)

    def update_display(self, final_results: Dict[str, Any], rounding_mode_name: str, ignore_constraints: bool):
        results_data = final_results['data']
        theoretical_float = results_data.get('required_total_float', 0.0)
        final_int = final_results['final_int']
        error_margin = final_results['error_margin']

        self.theoretical_result_label.SetLabel(
            f"Mode d'Arrondi Utilisé: **{rounding_mode_name}** (Optimal)\n"
            f"Total Théorique Flottant À GAGNER: {theoretical_float:.2f}\n"
            f"Total Entier À GAGNER Alloué: {final_int}\n"
            f"Erreur d'Arrondi (optimisation): {error_margin:+.2f} points"
        )

        data_for_view = []
        if not ignore_constraints and self.controller.last_results:
            try:
                margin_report_data = self.controller.logic.calculate_margin(
                    self.controller.courses,
                    self.controller.last_results['results']
                )
            except Exception:
                margin_report_data = []

            for report_item in margin_report_data:
                data_for_view.append([
                    report_item.get('name', 'N/A'),
                    str(report_item.get('points_allocated', 0)),
                    f"{report_item.get('final_margin', 0.0):.2f} pts ({report_item.get('max_loss_pct', 0.0):.2f}%)"
                ])
        else:
            data_for_view.append(
                ["N/A", "N/A", "Marge désactivée en mode Simulation Pure ou données manquantes."]
            )

        self.margin_report_view.update_data(data_for_view)


class AboutPanel(wx.Panel):
    """Panneau À Propos utilisant les nouveaux composants de texte."""

    def __init__(self, parent: wx.Notebook, controller: Any):
        wx.Panel.__init__(self, parent)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # TITRE MIS À JOUR
        title = TitleText(self, "🌟 Proxima Score : L'Optimisation Ciblée")
        vbox.Add(title, 0, wx.ALIGN_LEFT | wx.ALL, 20)

        # SLOGAN ASTRONOMIQUE
        slogan = wx.StaticText(
            self, label="L'outil d'alignement pour atteindre votre **Nyota** (étoile) académique. Développé pour le contexte de Lubumbashi.")
        slogan.Wrap(600)
        slogan.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT,
                               wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        vbox.Add(slogan, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)

        # ... le reste du code du AboutPanel ...
        # ... (le reste de la section 'Architecture' et 'Améliorations')

        ux_title = HeaderText(self, "Améliorations UX/UI & Refactorisation")
        vbox.Add(ux_title, 0, wx.LEFT | wx.TOP, 20)

        ux_content = (
            "  •   Composants Réutilisables : `NumericInput`, `BaseDataView`, `PrimaryButton`, etc., pour un code modulaire.\n"
            "  •   Contrôles Numériques Masqués : Utilisation de **wx.lib.masked.NumCtrl** via `NumericInput`.\n"
            "  •   Modularité : Chaque onglet est un `wx.Panel` autonome et chaque dialogue est une classe `wx.Dialog`."
        )
        ux_text = wx.StaticText(self, label=ux_content)
        ux_text.Wrap(600)
        vbox.Add(ux_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)

        note = wx.StaticText(
            self, label="Ce projet est construit selon l'architecture Modèle-Vue-Contrôleur (MVC).")
        vbox.Add(note, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        self.SetSizer(vbox)


# --------------------------------------------------
# --- 3. DIALOGUE MODALE (Refactorisée) ---
# --------------------------------------------------

class CourseEditDialog(wx.Dialog):
    """Dialogue modale pour éditer les détails d'un cours."""

    def __init__(self, parent: wx.Window, course_obj: Dict[str, Any]):
        title = f"Modifier : {course_obj['name']}"
        super().__init__(parent, title=title, size=(400, 300))
        self.course_obj = course_obj

        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(4, 2, 10, 10)
        grid.AddGrowableCol(1)

        # Utilisation des composants refactorisés
        self.score_ctrl = NumericInput(
            self, value=course_obj.get('score_actuel', 0.0), max_val=course_obj['weight']
        )
        self.min_pct_ctrl = NumericInput(
            self, value=course_obj.get('min_pct_cible', 0.0), max_val=100.0
        )
        self.deliberated_ctrl = NumericInput(
            self, value=course_obj.get('points_deliberes', 0.0), max_val=course_obj['weight']
        )

        grid.Add(wx.StaticText(self, label="Score Actuel:"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.score_ctrl, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="% Cible Min (0-100):"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.min_pct_ctrl, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Points Délibérés (+):"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deliberated_ctrl, 1, wx.EXPAND)
        grid.Add(wx.StaticText(
            self, label=f"Pondération Max: {course_obj['weight']:.1f}"), 0, wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 15)

        # Boutons standards OK/Cancel
        btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        self.SetSizer(sizer)

    def get_values(self) -> Tuple[float, float, float]:
        """Retourne les valeurs des champs."""
        return (
            self.score_ctrl.GetValue(),
            self.min_pct_ctrl.GetValue(),
            self.deliberated_ctrl.GetValue()
        )

    def validate_values(self) -> bool:
        """Valide les données avant de fermer."""
        score, min_pct, deliberated = self.get_values()
        weight = self.course_obj['weight']

        if not (0 <= score <= weight):
            return False
        if not (0 <= min_pct <= 100):
            return False
        # Assumant que les points délibérés ne peuvent pas dépasser la pondération totale
        if not (0 <= deliberated <= weight):
            return False

        return True


# --------------------------------------------------
# --- 4. VUE PRINCIPALE (CONTENEUR) ---
# --------------------------------------------------

class PointAllocatorFrame(wx.Frame):
    def __init__(self, controller: Any):
        wx.Frame.__init__(
            self, None, title="🌟 Proxima Score : Naviguez vers votre objectif")

        self.controller = controller

        self.SetSize((1000, 750))
        self.SetMinSize((700, 600))

        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.notebook = wx.Notebook(main_panel)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_tab_change)

        # Composition des panneaux
        self.management_panel = CourseManagementPanel(
            self.notebook, controller)
        self.calculation_panel = CalculationPanel(self.notebook, controller)
        self.report_panel = ReportPanel(self.notebook, controller)
        self.about_panel = AboutPanel(self.notebook, controller)

        self.notebook.AddPage(self.management_panel, "📚 Gestion des Cours")
        self.notebook.AddPage(self.calculation_panel,
                              "🧮 Calcul & Optimisation")
        self.notebook.AddPage(self.report_panel, "📈 Rapport & Marge")
        self.notebook.AddPage(self.about_panel, "ℹ️ À Propos")

        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)
        main_panel.SetSizer(main_sizer)

        self.Center()
        self.Show()

    def show_edit_course_dialog(self, course_obj: Dict[str, Any], index: int):
        """Affiche la dialogue d'édition et gère la boucle de validation."""
        dlg = CourseEditDialog(self, course_obj)

        while True:
            if dlg.ShowModal() != wx.ID_OK:
                # L'utilisateur a annulé
                break

            # L'utilisateur a cliqué sur OK, nous validons
            if dlg.validate_values():
                score, min_pct, deliberated = dlg.get_values()
                # Envoi des données valides au contrôleur
                self.controller.update_course_data(
                    course_obj, score, min_pct, deliberated
                )
                break  # Sortir de la boucle
            else:
                # Validation échouée, on affiche une erreur et la dialogue RESTE ouverte
                self.show_error(
                    "Veuillez vérifier les valeurs (Score et % min doivent être dans les limites autorisées).",
                    is_modal=True
                )

        dlg.Destroy()

    def _on_tab_change(self, event):
        if event.GetSelection() == 0:
            self.management_panel.update_display(self.controller.courses)
        event.Skip()

    def update_all_views(self, courses: List[Dict[str, Any]],
                         distributed_scores: Dict[str, int] = None,
                         final_results: Dict[str, Any] = None):
        """Met à jour tous les panneaux avec les nouvelles données."""

        # L'onglet 1 (Gestion) est toujours mis à jour
        self.management_panel.update_display(courses)

        if final_results:
            # Si nous avons des résultats de calcul, mettre à jour les autres onglets
            total_weight = self.controller.data_handler.get_total_weight(
                courses)
            target_percentage = self.calculation_panel.get_target_value()
            final_mode_name = final_results.get(
                'optimal_mode_name', self.calculation_panel.get_rounding_mode())
            ignore_constraints = self.calculation_panel.get_ignore_constraints()

            self.calculation_panel.update_display(
                courses, distributed_scores, final_results, total_weight,
                target_percentage, final_mode_name, ignore_constraints
            )

            self.report_panel.update_display(
                final_results, final_mode_name, ignore_constraints
            )

            # Basculer vers l'onglet des résultats
            self.notebook.SetSelection(1)

    def show_error(self, message: str, to_management: bool = False, is_modal: bool = False):
        """Affiche une boîte de dialogue d'erreur."""
        style = wx.OK | wx.ICON_ERROR
        if is_modal:
            # Assure que la boîte de dialogue d'erreur reste au-dessus de la dialogue modale
            style |= wx.STAY_ON_TOP

        wx.MessageBox(message, "Erreur", style)

        if to_management:
            self.notebook.SetSelection(0)

    def clear_add_inputs(self):
        self.management_panel.clear_inputs()


# --------------------------------------------------
# --- 5. CONTRÔLEUR (LOGIQUE DE LIAISON) ---
# --------------------------------------------------

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
