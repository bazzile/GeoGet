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
# from askcredentialdialog import askCredentialDialog

import os.path
import datetime

class PSQL:

    def __init__(self,iface):
        self.iface = iface
        self.schema = ""

    def querySet(
            self, cloud_pct_mx, wkt, crs='4326', schema='geoarchive', table='imagery', geom_field='geom'):
        # TODO подумать, как выделить WHERE часть отдельно
        cloud_cond = " AND cloud_pct <= " + str(cloud_pct_mx)
        sql = "SELECT *" + ", row_number() OVER () AS ogc_fid FROM " + schema + \
              "." + table + " WHERE ST_Intersects(" + geom_field + ", ST_GeomFromText('" + wkt + "', " + crs + "))" + \
              cloud_cond
        return sql

    # TODO реализовать загрузку в одну строку через iface, делать запрос по *, заменить ogc_fid
    #  (нужно только если на выходе запроса нет ключевых полей) на vendor_id
    def loadSql(self, layerName, sql):
        uri = QgsDataSourceURI()
        uri.setConnection("localhost", "5432", "innoter", "postgres", "postgres")
        uri.setDataSource("", "(" + sql + ")", "geom", "", "ogc_fid")
        vlayer = QgsVectorLayer(uri.uri(), layerName, "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)


    # def setConnection(self, conn='MyDB'):
    #     s = QSettings()
    #     s.beginGroup("PostgreSQL/connections/"+conn)
    #     currentKeys = s.childKeys()
    #     #print "keys: ", currentKeys
    #     self.PSQLDatabase=s.value("database", "" )
    #     self.PSQLHost=s.value("host", "" )
    #     self.PSQLUsername=s.value("username", "" )
    #     self.PSQLPassword=s.value("password", "" )
    #     self.PSQLPort=s.value("port", "" )
    #     self.PSQLService=s.value("service", "" )
    #     s.endGroup()
    #     self.db = QSqlDatabase.addDatabase("QPSQL")
    #     self.db.setHostName(self.PSQLHost)
    #     self.db.setPort(int(self.PSQLPort))
    #     self.db.setDatabaseName(self.PSQLDatabase)
    #     self.db.setUserName(self.PSQLUsername)
    #     self.db.setPassword(self.PSQLPassword)