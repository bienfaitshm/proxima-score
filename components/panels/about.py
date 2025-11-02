import wx
from typing import Any
from components.ui.base import HeaderText, TitleText


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
