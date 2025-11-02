import wx
import wx.dataview as dv
from typing import List, Dict, Any
from components.ui.base import DeleteButton, NumericInput, PrimaryButton, TextInput, GroupBox
from components.ui.data_view import BaseDataView


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

        display_box.Add(
            self.total_weight_label, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 10)

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
