from PyQt6 import QtCore, QtWidgets

from pygenplot.models.data_tree_model import DataTreeItem, DataTreeModel, FlattenDataTreeProxyModel

class DatasetsWidget(QtWidgets.QWidget):

    dataset_selected = QtCore.pyqtSignal(dict)

    def __init__(self,*args,**kwargs):

        super(DatasetsWidget,self).__init__(*args,**kwargs)

        self._build()

    def _build(self):

        main_layout = QtWidgets.QVBoxLayout()

        units_column = DataTreeItem._headers.index("units")

        self._tab_widget = QtWidgets.QTabWidget()

        self._datasets_tableview = QtWidgets.QTableView()
        self._datasets_tableview.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self._datasets_tableview.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self._datasets_tableview.setSortingEnabled(True)
        self._datasets_tableview.setShowGrid(False)
        self._tab_widget.addTab(self._datasets_tableview,"Table view")

        self._datasets_treeview = QtWidgets.QTreeView()
        self._tab_widget.addTab(self._datasets_treeview,"Tree view")

        main_layout.addWidget(self._tab_widget)

        self._selected_dataset_lineedit = QtWidgets.QLineEdit()
        main_layout.addWidget(self._selected_dataset_lineedit)

        self.setLayout(main_layout)

    def get_selected_dataset_axis_info(self):        
        current_widget = self._tab_widget.currentWidget()
        model = current_widget.model()
        if model is None:
            return []
        current_index = current_widget.currentIndex()
        axis_dataset_info = model.data(current_index,DataTreeModel.AxisInfoRole)
        return axis_dataset_info

    def get_selected_dataset_info(self):
        current_widget = self._tab_widget.currentWidget()
        model = current_widget.model()
        if model is None:
            return {}

        current_index = current_widget.currentIndex()
        dataset_info = model.data(current_index,DataTreeModel.DatasetInfoRole)
        return dataset_info

    def on_select_dataset(self,index,emitting_widget):
        if emitting_widget == self._datasets_tableview:
            tree_index = self._datasets_tableview.model().mapToSource(index)
            self._datasets_treeview.setCurrentIndex(tree_index)
        else:
            table_index = self._datasets_tableview.model().mapFromSource(index)
            self._datasets_tableview.setCurrentIndex(table_index)
            self._selected_dataset_lineedit.setText("")
            if not table_index.isValid():
                return

        dataset_info = self.get_selected_dataset_info()
        self._selected_dataset_lineedit.setText(dataset_info["path"])        
        self.dataset_selected.emit(dataset_info)

    def on_dataset_autocomplete(self):
        selected_dataset_path = self._selected_dataset_lineedit.text()
        datatree_model = self._datasets_treeview.model()
        index = datatree_model.get_index_from_path(selected_dataset_path)
        if not index.isValid():
            return

        self._datasets_treeview.setCurrentIndex(index)
        table_index = self._datasets_tableview.model().mapFromSource(index)
        self._datasets_tableview.selectRow(table_index.row())

        dataset_info = self.get_selected_dataset_info()
        self.dataset_selected.emit(dataset_info)

    def on_sort_datasets(self,old_to_new_indexes):
        current_row = self._datasets_tableview.currentIndex().row()
        if current_row == -1:
            return
        new_row_index = old_to_new_indexes.index(current_row)
        self._datasets_tableview.selectRow(new_row_index)

    def set_model(self,data_model):

        self._datasets_treeview.setModel(data_model)
        self._datasets_treeview.clicked.connect(lambda index,emitting_widget=self._datasets_treeview : self.on_select_dataset(index,emitting_widget))
        if data_model is None:
            self._datasets_tableview.setModel(None)
        else:
            datasets = data_model.get_registered_datasets()
            completer = QtWidgets.QCompleter(datasets)
            completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
            completer.activated.connect(self.on_dataset_autocomplete)
            self._selected_dataset_lineedit.setCompleter(completer)

            proxy_model = FlattenDataTreeProxyModel()
            proxy_model.setSourceModel(data_model)
            self._datasets_tableview.setModel(proxy_model)
            self._datasets_tableview.clicked.connect(lambda index,emitting_widget=self._datasets_tableview : self.on_select_dataset(index,emitting_widget))
            proxy_model.data_sorted.connect(self.on_sort_datasets)

    def update(self):

        model = self._datasets_treeview.model()
        if model is None:
            return
        model.layoutChanged.emit()


