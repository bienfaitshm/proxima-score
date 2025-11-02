
import wx
import wx.dataview as dv
from typing import List, Dict, Any
from components.ui.base import DeleteButton, NumericInput, PrimaryButton, TextInput, GroupBox, CheckBox, Choice
from components.ui.data_view import BaseDataView
from constants import ROUNDING_CHOICES


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
