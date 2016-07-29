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


class SyncedSlider:

    def __init__(self, slider_obj, mx_box_obj, mn_box_obj=None):

        self.mx_box_obj = mx_box_obj
        self.slider_obj = slider_obj

        self.slider_obj.valueChanged.connect(
            lambda: self.mx_box_obj.setValue(self.slider_obj.value()))
        self.mx_box_obj.valueChanged.connect(
            lambda: self.slider_obj.setValue(self.mx_box_obj.value()))

    def get_mx_value(self):
        curr_value = self.mx_box_obj.value()
        return curr_value
