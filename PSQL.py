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
import psycopg2


class PSQL:

    def __init__(self,iface):
        self.iface = iface
        self.schema = ""

    # def querySet(
    #         self, dates_dict, cloud_pct_mx, off_nadir_mx, sat_set, stereo_flag, wkt,
    #         crs='4326', schema='vendors', table='dg', geom_field='geom'):
    #     # TODO подумать, как выделить WHERE часть отдельно
    #     date_cond = " AND acqdate < " + "'" + dates_dict['max_date'] + "'" \
    #                 + " AND acqdate > " + "'" + dates_dict['min_date'] + "'"
    #     cloud_cond = " AND cloudcover <= " + str(cloud_pct_mx)
    #     off_nadir_cond = " AND mxoffnadir <= " + str(off_nadir_mx)
    #     # TODO добавить ошибку if platform is null
    #     # Добавляем кавычки, чтобы platform/sat_set не выдавал ошибку (no such table)
    #     sat_cond = " AND platform IN (" + ', '.join(["'%s'" %item for item in sat_set]) + ")"
    #     stereo_cond = " AND stereopair <> 'NONE'" if stereo_flag is True else ""
    #     # Если необходим уникальный ключ (ogc_fid): sql = "SELECT *" + ", row_number() OVER () AS ogc_fid FROM " + schema + \
    #     sql = "SELECT * FROM " + schema + \
    #           "." + table + " WHERE ST_Intersects(" + geom_field + ", ST_GeomFromText('" + wkt + "', " + crs + "))" + \
    #           cloud_cond + off_nadir_cond + sat_cond + stereo_cond + date_cond + " LIMIT 100"
    #     return sql
    def querySet(
            self, order_desc, schema='geoarchive', table='dg_orders'):
        # TODO подумать, как выделить WHERE часть отдельно
        # Добавляем кавычки, чтобы platform/sat_set не выдавал ошибку (no such table)
        order_desc_cond = "AND order_desc = '%s'" % order_desc
        # Если необходим уникальный ключ (ogc_fid): sql = "SELECT *" + ", row_number() OVER () AS ogc_fid FROM " + schema + \
        # '1 = 1' нужно для того, чтобы любой критерий мог начинаться с 'AND' (даже если он один)
        sql = "SELECT * FROM " + schema + \
              "." + table + " WHERE 1 = 1 " + order_desc_cond
        return sql

    def simpleQuery(self):
        try:
            conn = psycopg2.connect("dbname='geodata' user='postgres' host='localhost' password='postgres'")
        except:
            print "I am unable to connect to the database"
        cursor = conn.cursor()
        cursor.execute("""SELECT order_desc FROM geoarchive.dg_orders""")
        order_desc_result = cursor.fetchall()
        order_desc_list = [item[0] for item in order_desc_result]
        return order_desc_list

    # TODO реализовать загрузку в одну строку через iface, делать запрос по *, заменить ogc_fid
    #  (нужно только если на выходе запроса нет ключевых полей) на vendor_id
    def loadSql(self, layerName, sql):
        uri = QgsDataSourceURI()
        uri.setConnection("db.office.innoter.com", "5432", "geodata", "read_user", "user")
        # Если необходим уникальный ключ (ogc_fid): uri.setDataSource("", "(" + sql + ")", "geom", "", "ogc_fid")
        # в качестве последней переменной ВСЕГДА идёт primary key
        uri.setDataSource("", "(" + sql + ")", "geom", "", "order_id")
        vlayer = QgsVectorLayer(uri.uri(), layerName, "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        return vlayer


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
