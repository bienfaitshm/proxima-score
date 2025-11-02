import wx
import wx.dataview as dv
from typing import List, Dict, Any, Tuple
from components.ui.base import DeleteButton, NumericInput, PrimaryButton, TextInput, GroupBox
from components.ui.data_view import BaseDataView


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
