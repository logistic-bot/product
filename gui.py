import wx
import wx.grid as grid

import main


class NewItemDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        super(NewItemDialog, self).__init__(*args, **kwargs)
        self.SetTitle("New item")

        mainPanel = wx.Panel(self)
        panel = wx.Panel(mainPanel)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)

        label = wx.StaticText(mainPanel, label="New item")
        font = label.GetFont().Bold()
        font.PointSize += 1
        label.SetFont(font)
        mainSizer.Add(label, wx.SizerFlags().Center())

        vbox = wx.BoxSizer(wx.VERTICAL)

        nameEntry = wx.TextCtrl(panel, size=(300, -1))
        nameLabel = wx.StaticText(panel, label="Name")
        sizer.Add(nameLabel, wx.SizerFlags().Center())
        sizer.Add(nameEntry, wx.SizerFlags().Center())
        self.nameEntry = nameEntry

        amountEntry = wx.SpinCtrl(panel, min=0, initial=0, max=99999999)
        amountLabel = wx.StaticText(panel, label="Amount")
        sizer.Add(amountLabel, wx.SizerFlags().Center())
        sizer.Add(amountEntry, wx.SizerFlags().Center())
        self.amountEntry = amountEntry

        priceEntry = wx.SpinCtrlDouble(panel, min=0, initial=0, max=99999999, inc=0.01)
        priceLabel = wx.StaticText(panel, label="Price")
        sizer.Add(priceLabel, wx.SizerFlags().Center())
        sizer.Add(priceEntry, wx.SizerFlags().Center())
        self.priceEntry = priceEntry

        cancelButton = wx.Button(panel, label="Cancel")
        sizer.Add(cancelButton, wx.SizerFlags().Center())
        okButton = wx.Button(panel, label="Ok")
        sizer.Add(okButton, wx.SizerFlags().Center())

        mainSizer.Add(panel, wx.SizerFlags().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, 5))
        panel.SetSizer(sizer)
        mainPanel.SetSizer(mainSizer)
        mainSizer.SetSizeHints(self)

        self.Bind(wx.EVT_BUTTON, self.OnOk, okButton)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, cancelButton)

    def OnOk(self, event):
        self.EndModal(wx.ID_OK)

    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def getName(self):
        return self.nameEntry.GetValue()

    def getAmount(self):
        return self.amountEntry.GetValue()

    def getPrice(self):
        return self.priceEntry.GetValue()


class InventoryMainView(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(InventoryMainView, self).__init__(*args, **kwargs)

        panel = wx.Panel(self)

        welcome_text = wx.StaticText(
            panel, label="Welcome to the inventory management system"
        )
        font = welcome_text.GetFont()
        welcome_font = font.Bold()
        welcome_font.PointSize += 3
        welcome_text.SetFont(welcome_font)

        version_text = wx.StaticText(panel, label="Version 1.0.0")
        version_font = font
        version_font.PointSize -= 3
        version_font.SetWeight(wx.FONTWEIGHT_LIGHT)
        version_text.SetFont(version_font)

        self.grid = grid.Grid(panel)

        newButton = wx.Button(panel, label="New item")
        deleteButton = wx.Button(panel, label="Delete item")

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(newButton)
        buttonSizer.Add(deleteButton, wx.SizerFlags().Border(wx.LEFT, 10))

        self.Bind(wx.EVT_BUTTON, self.OnNewItem, newButton)
        self.Bind(wx.EVT_BUTTON, self.OnDeleteItem, deleteButton)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(welcome_text, wx.SizerFlags().Border(wx.TOP | wx.LEFT, 10))
        sizer.Add(version_text, wx.SizerFlags().Border(wx.LEFT, 25))
        sizer.Add(buttonSizer, wx.SizerFlags().Border(wx.LEFT, 10))
        sizer.Add(self.grid, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.makeMenuBar()
        self.CreateStatusBar()
        self.create_connection()

        colcount = self.inventory.columncount
        rowcount = self.inventory.rowcount
        self.grid.CreateGrid(rowcount, colcount)

        self.update_grid()

        self.Bind(grid.EVT_GRID_CELL_CHANGING, self.OnGridCellChanging)
        self.Bind(grid.EVT_GRID_CELL_CHANGED, self.OnGridCellChanged)

        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def OnNewItem(self, event):
        dialog = NewItemDialog(self)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            price = dialog.getPrice()
            amount = dialog.getAmount()
            name = dialog.getName()
            self.inventory.new_item(name, price, amount)
            self.update_grid()


    def OnDeleteItem(self, event):
        choices = [
            "{} - {}".format(id, name)
            for id, name in self.inventory.get_id_name_pairs()
        ]
        if choices != []:  # don't do anything if there are no items
            dialog = wx.SingleChoiceDialog(
                self, "Delete item", "What item would you like to delete?", choices
            )
            result = dialog.ShowModal()
            if result == wx.ID_OK:
                choice = dialog.GetSelection()
                id = self.inventory.get_ids()[choice]
                self.inventory.delete(id)
                self.update_grid()

    def OnGridCellChanged(self, event):
        col = event.GetCol()
        row = event.GetRow()
        old = event.GetString()
        new = self.grid.GetCellValue(row, col)
        if old != new:  # ensure no infinite loop
            id = int(self.grid.GetCellValue(row, 0))
            if col == 2:  # price
                value = float(new)
                self.inventory.set_price(id, value)
            elif col == 3:  # amount
                value = int(new)
                self.inventory.set_amount(id, value)
            elif col == 1:  # name
                self.inventory.set_name(id, new)

    def OnGridCellChanging(self, event):
        col = event.GetCol()
        row = event.GetRow()
        new = event.GetString()
        if col == 2:
            try:
                _ = float(new)
            except ValueError:
                event.Veto()
        elif col == 3:
            try:
                _ = int(new)
            except ValueError:
                event.Veto()

    def create_connection(self):
        self.inventory = main.Inventory()

    def update_grid(self, event=None):
        self.SetStatusText("Updating view...")
        colcount = self.inventory.columncount
        rowcount = self.inventory.rowcount
        self.grid.SetColLabelValue(0, "id")
        self.grid.SetColLabelValue(1, "name")
        self.grid.SetColLabelValue(2, "price")
        self.grid.SetColLabelValue(3, "amount")

        old_rowcount = self.grid.GetNumberRows()
        self.grid.DeleteRows(numRows=old_rowcount)
        self.grid.AppendRows(numRows=rowcount)

        ids = self.inventory.get_ids()
        for id in ids:
            row = ids.index(id)  # we can do this because we know ids are unique
            self.grid.SetCellValue(row, 0, str(id))  # id
            self.grid.SetCellValue(row, 1, self.inventory.get_name_from_id(id))  # name
            self.grid.SetCellValue(
                row, 2, str(self.inventory.get_price_from_id(id))
            )  # price
            self.grid.SetCellValue(
                row, 3, str(self.inventory.get_amount_from_id(id))
            )  # amount
            self.grid.SetReadOnly(row, 0)

        for i in range(rowcount):
            self.grid.DisableColResize(i)
            self.grid.SetColMinimalWidth(i, 1)
        for i in range(colcount):
            self.grid.DisableRowResize(i)
            self.grid.SetRowMinimalHeight(i, 1)

        self.grid.HideRowLabels()
        self.grid.AutoSize()
        self.SetStatusText("Ready.")

    def makeMenuBar(self):
        fileMenu = wx.Menu()
        exitItem = fileMenu.Append(
            -1, "&Quit\tCtrl-Q", "Save all changes and exit the application"
        )
        updateItem = fileMenu.Append(-1, "&Update\tCtrl-R", "Update")

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.update_grid, updateItem)

    def OnExit(self, event):
        self.SetStatusText("Closing database connection...")
        self.inventory.close()
        self.Destroy()


if __name__ == "__main__":
    app = wx.App()
    frame = InventoryMainView(None, title="Inventory Management System")
    frame.Show()
    app.MainLoop()
