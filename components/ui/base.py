import wx
import wx.dataview as dv
import wx.lib.masked as masked
from typing import List, Dict, Any, Tuple, Optional


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
