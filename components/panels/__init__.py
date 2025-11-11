import wx

from typing import List, Protocol, Any, Dict, TypedDict
from .about import AboutPanel
from .course_management import CourseManagementPanel
from .calculation import CalculationPanel
from .report import ReportPanel
from components.dialog.cours_edit import CourseEditDialog


class BasePanel(wx.Frame):
    def __init__(self, parent: wx.Notebook, controller: Any):
        pass


class PanelObj:
    def __init__(self, panel: BasePanel, name: str, title: str):
        self.panel = panel
        self.name = name
        self.title = title


PANELS: List[PanelObj] = [
    PanelObj(name="courses", panel=CourseManagementPanel,
             title="📚 Gestion des Cours"),
    PanelObj(name="calculation", panel=CalculationPanel,
             title="🧮 Calcul & Optimisation"),
    PanelObj(name="report", panel=ReportPanel, title="📈 Rapport & Marge"),
    PanelObj(name="about", panel=AboutPanel, title="ℹ️ À Propos"),
]


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
        for panel in PANELS:
            frame_panel = panel.panel(self.notebook, controller)
            setattr(self, panel.name, frame_panel)
            self.notebook.AddPage(frame_panel, panel.title)

        # self.management_panel = CourseManagementPanel(
        #     self.notebook, controller)
        # self.calculation_panel = CalculationPanel(self.notebook, controller)
        # self.report_panel = ReportPanel(self.notebook, controller)
        # self.about_panel = AboutPanel(self.notebook, controller)

        # self.notebook.AddPage(self.management_panel, "📚 Gestion des Cours")
        # self.notebook.AddPage(self.calculation_panel,
        #                       "🧮 Calcul & Optimisation")
        # self.notebook.AddPage(self.report_panel, "📈 Rapport & Marge")
        # self.notebook.AddPage(self.about_panel, "ℹ️ À Propos")

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
        if event.GetSelection() == 0 and hasattr(self, "courses"):
            getattr("courses").update_display(self.controller.courses)
        event.Skip()

    def _update_panel(self, name: str):
        def updater(*args, **kwargs):
            if hasattr(self, name):
                getattr(self, name).update_display(*args, **kwargs)
        return updater

    def update_all_views(self, courses: List[Dict[str, Any]],
                         distributed_scores: Dict[str, int] = None,
                         final_results: Dict[str, Any] = None):
        """Met à jour tous les panneaux avec les nouvelles données."""

        # L'onglet 1 (Gestion) est toujours mis à jour
        self._update_panel(name="courses")(courses)

        if final_results:
            # Si nous avons des résultats de calcul, mettre à jour les autres onglets
            total_weight = self.controller.data_handler.get_total_weight(
                courses)
            target_percentage = self.calculation_panel.get_target_value()
            final_mode_name = final_results.get(
                'optimal_mode_name', self.calculation_panel.get_rounding_mode())
            ignore_constraints = self.calculation_panel.get_ignore_constraints()

            self._update_panel("calculation")(
                courses, distributed_scores, final_results, total_weight,
                target_percentage, final_mode_name, ignore_constraints
            )
            # self.calculation_panel.update_display(
            #     courses, distributed_scores, final_results, total_weight,
            #     target_percentage, final_mode_name, ignore_constraints
            # )

            self._update_panel("report")(
                final_results, final_mode_name, ignore_constraints)

            # # self.report_panel.update_display(
            #     final_results, final_mode_name, ignore_constraints
            # # )

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
