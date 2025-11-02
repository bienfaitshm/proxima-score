import wx
import wx.dataview as dv
from typing import List, Tuple


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
