# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoGet
                                 A QGIS plugin
 Поиск, выборка и экспорт метаданных из интегрированной БД поставщиков
                              -------------------
        begin                : 2016-07-22
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Innoter
        email                : innoter@innoter.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from geo_get_dialog import GeoGetDialog
import os
# импорт моих модулей
from geometry import Geomerty
from PSQL import PSQL
from controls import *

class GeoGet:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeoGet_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = GeoGetDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Innoter GeoGet')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GeoGet')
        self.toolbar.setObjectName(u'GeoGet')

        # подключение моих модулей
        self.Geometry = Geomerty(self.iface)
        self.PSQL = PSQL(self.iface)

        self.Cloud_pct_control = SyncedSlider(self.dlg.cloud_pct_slider, self.dlg.cloud_pct_mx)
        self.Angle_control = SyncedSlider(self.dlg.angle_slider, self.dlg.angle_mx)
        # мои переменный
        self.last_used_path = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeoGet', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GeoGet/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Innoter GeoGet'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def populateGui(self):
        """Make the GUI live."""

        # TODO удалить этот импорт
        self.iface.addVectorLayer(
            os.path.join(os.path.dirname(__file__), r"testData\test_polygon.shp"), 'test_poly_2', 'ogr')

        self.populateComboBox(
            self.dlg.v_layer_list, self.get_layer_names(), u'Выберите слой', True)
        self.dlg.in_browse_btn.clicked.connect(self.select_input_file)
        # слой выбран, переключаем текущую [currentIndex()] вкладку на следующую
        self.dlg.v_layer_list.activated.connect(
            lambda: self.dlg.parameters_toolBox.setCurrentIndex(int(self.dlg.parameters_toolBox.currentIndex()) + 1))



        # TODO удалить этот тест-блок
        # layer = self.Geometry.get_layer("test_poly")
        # geometry = self.Geometry.get_geometry(layer)
        # self.dlg.test_textBrowser.append(str(geometry))
        # if str(self.dlg.v_layer_list.currentText()) != u'Выберите слой' or None:
        self.dlg.v_layer_list.activated.connect(lambda: self.zoom2layer(str(self.dlg.v_layer_list.currentText())))
        self.dlg.search_btn.clicked.connect(lambda: self.t_search_db(str(self.dlg.v_layer_list.currentText())))





    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&Innoter GeoGet'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        self.populateGui()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def populateComboBox(self, combo, list, predef, sort):
        # procedure to fill specified combobox with provided list
        combo.blockSignals(True)
        combo.clear()
        model = QStandardItemModel(combo)
        predefInList = None
        for elem in list:
            try:
                item = QStandardItem(unicode(elem))
            except TypeError:
                item = QStandardItem(str(elem))
            model.appendRow(item)
            if elem == predef:
                predefInList = elem
        if sort:
            model.sort(0)
        combo.setModel(model)
        if predef != "":
            if predefInList:
                combo.setCurrentIndex(combo.findText(predefInList))
            else:
                combo.insertItem(0, predef)
                combo.setCurrentIndex(0)
        combo.blockSignals(False)

    def get_layers_list(self):
        """Возвращает список открытых векторных полигональных слоёв (QgsVectorLayer objects)"""
        # http://gis.stackexchange.com/questions/124866/how-to-identify-polygon-point-shapefiles-in-python/124870#124870
        vector_type_index = 0
        polygon_type_index = 2
        layers = [layer for layer in self.iface.legendInterface().layers() if
                  layer.type() == vector_type_index and layer.geometryType() == polygon_type_index]
        return layers

    def get_layer_names(self):
        """ Загружаем список открытых слоёв в диалог "выбор контура (v_layer_list)."""
        layer_list = []
        layers = self.get_layers_list()
        for layer in layers:
            layer_path = layer.source()
            # layer_name = os.path.basename(layer_path)
            layer_list.append(layer_path)
            # # TODO учесть, что есть это:
            # layer_list.append(layer.name())
        return layer_list

    def select_input_file(self):
        if self.last_used_path == None:
            filename = QFileDialog.getOpenFileName(
                self.dlg, u"Укажите файл контура ", "", u'Полигоны (*.shp *.kml *tab *geojson)')
            # записываем в self.last_used_path последний использовавшийся каталог
            self.last_used_path = os.path.dirname(filename)
        else:
            filename = QFileDialog.getOpenFileName(
                self.dlg, u"Укажите файл контура ", self.last_used_path, u'Полигоны (*.shp *.kml *tab *geojson)')
        # TODO отображать в списке только имя контура без пути и расшир (реализовать через словарь? (т.к. нужен и путь)
        if filename:
            self.dlg.v_layer_list.insertItem(self.dlg.v_layer_list.count(), filename)
            self.dlg.v_layer_list.setCurrentIndex(self.dlg.v_layer_list.count() - 1)
            # TODO лучше всего загружать слой в QGIS вместе с результатами
            self.load_layer(filename, os.path.basename(filename), 'ogr')
        else:
            pass

    def load_layer(self, path, name, data_provider):
        lyr = self.iface.addVectorLayer(path, name.split('.')[0], data_provider)
        # zoom to newly loaded layer
        self.zoom2layer(lyr.source())
        # слой выбран, переключаем текущую [currentIndex()] вкладку на следующую
        self.dlg.parameters_toolBox.setCurrentIndex(int(self.dlg.parameters_toolBox.currentIndex()) + 1)

    def zoom2layer(self, layer_path):
        layers = self.get_layers_list()
        for layer in layers:
            if layer.source() == layer_path:
                self.iface.setActiveLayer(layer)
                self.iface.zoomToActiveLayer()
                break

    def t_search_db(self, layer_path):
        # TODO разобраться, почему при выборе "очистить результаты" (после поиска без опции) удляются не все слои
        if self.dlg.clear_results_chbx.isChecked():
            layers = self.clear_results(self.get_layers_list())
        else:
            layers = [layer for layer in self.get_layers_list() if not layer.name().startswith('results_')]
        for layer in layers:
            if layer.source() == layer_path:
                lyr = self.Geometry.get_layer(layer_path)
                wkt = self.Geometry.get_geometry(lyr)
                # TODO добавить поддержку минимальной облачности (аккуратно, во внутр. БД есть -9999)
                sql = self.PSQL.querySet(
                    self.Cloud_pct_control.get_mx_value(), self.Angle_control.get_mx_value(), wkt)
                self.PSQL.loadSql('results_GE01', sql)
                break

    def clear_results(self, layer_list):
        """Удаляет из реестра слоёв результаты предыдущего поиска"""
        for layer in layer_list:
            if layer.name().startswith('results_'):
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
                layer_list.remove(layer)
        return layer_list


