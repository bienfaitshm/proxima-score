
import wx
import wx.dataview as dv
from typing import List, Dict, Any
from components.ui.base import DeleteButton, NumericInput, PrimaryButton, TextInput, GroupBox, CheckBox, Choice
from components.ui.data_view import BaseDataView
from constants import ROUNDING_CHOICES


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
