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
from PyQt4.QtSql import *
from qgis.core import *


class Contrlos:

    def __init__(self, dialog):
        self.dlg = dialog

        # облачность (замыкаем слайдер на окошко ввода и наоборот)
        self.dlg.cloud_pct_slider.valueChanged.connect(
            lambda: self.dlg.cloud_pct_mx.setValue(self.dlg.cloud_pct_slider.value()))
        self.dlg.cloud_pct_mx.valueChanged.connect(
            lambda: self.dlg.cloud_pct_slider.setValue(self.dlg.cloud_pct_mx.value()))

    # def slider_cloud_pct(self):

