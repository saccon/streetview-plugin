# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StreetView
                                 A QGIS plugin
 StreetView
                              -------------------
        begin                : 2014-01-20
        copyright            : (C) 2014 by StreetView
        email                : StreetView
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

import subprocess
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from .resources_rc import *

from qgis.PyQt.QtCore import Qt, QEventLoop, QVariant
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QInputDialog, QPushButton
from qgis.PyQt.QtGui import QIcon, QColor

# Import the code for the dialog
import os.path
import math
import webbrowser  




from .resources_rc import *    
    
rb=QgsRubberBand(iface.mapCanvas(),QgsWkbTypes.GeometryType.PointGeometry )
rl=QgsRubberBand(iface.mapCanvas(),QgsWkbTypes.GeometryType.LineGeometry )




premuto= False
linea=False
point0=iface.mapCanvas().getCoordinateTransform().toMapCoordinates(0, 0)
point1=iface.mapCanvas().getCoordinateTransform().toMapCoordinates(0, 0)
class StreetView:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        # locale = QtCore.QSettings().value("locale/userLocale", defaultValue="")[0:2]
        # localePath = os.path.join(self.plugin_dir, 'i18n', 'streetview_{}.qm'.format(locale))

        # if os.path.exists(localePath):
        #     self.translator = QTranslator()
        #     self.translator.load(localePath)
        #
        #     if qVersion() > '4.3.3':
        #         QCoreApplication.installTranslator(self.translator)
         


    def initGui(self):
        self.action = QAction(QIcon(":/plugins/streetview/icon.png"),u"StreetView", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&StreetView", self.action)
        
    def unload(self):
        self.iface.removePluginMenu(u"&StreetView", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self): 
        # Get google streetview wms (the blue lines) and add it to the layer tree
        uri = "type=xyz&url=https://mts2.google.com/mapslt?lyrs%3Dsvv%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D%26w%3D256%26h%3D256%26hl%3Den%26style%3D40,18&zmax=18&zmin=0&http-header:referer="
        rlayer = QgsRasterLayer(uri, 'StreetView Abdeckung', 'wms')
        if rlayer.isValid():
            root = QgsProject.instance().layerTreeRoot()
            QgsProject.instance().addMapLayer(rlayer, False)
            root.insertLayer(0, rlayer)
        tool = PointTool(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(tool)  
    
       
  
class PointTool(QgsMapTool):  

        
        def __init__(self, canvas):
        
            QgsMapTool.__init__(self, canvas)
            self.canvas = canvas    

        def canvasPressEvent(self, event):
            x = event.pos().x()
            y = event.pos().y()
            global rb ,premuto ,point0
            if not premuto: 
              premuto=True
              rb=QgsRubberBand(iface.mapCanvas(),QgsWkbTypes.GeometryType.PointGeometry )
              rb.setColor ( QColor("red") )
              point0 = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
              rb.addPoint(point0)  
  
        def canvasMoveEvent(self, event):
              x = event.pos().x()
              y = event.pos().y()        
              global premuto,point0,point1,linea,rl
              if premuto:
               if not linea:              
                rl.setColor ( QColor("red") )
                point1 = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
                rl.addPoint(point0)  
                rl.addPoint(point1)
                linea=True
               else:
                if linea: 
                  point1 = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
                  rl.reset(QgsWkbTypes.LineGeometry)
                  rl.addPoint(point0)  
                  rl.addPoint(point1)
                  
                  
      
        def canvasReleaseEvent(self, event):
            global premuto,linea,rb,rl,point1,point0
            angle = math.atan2(point1.x() - point0.x(), point1.y() - point0.y())
            angle = math.degrees(angle)if angle>0 else (math.degrees(angle) + 180)+180
            premuto=False
            linea=False
            actual_crs = self.canvas.mapSettings().destinationCrs()
            crsDest = QgsCoordinateReferenceSystem(4326)  # WGS 84 / UTM zone 33N
            xform = QgsCoordinateTransform(actual_crs, crsDest,QgsProject.instance())
            pt1 = xform.transform(point0)
           
            print ('https://www.google.com/maps/@?api=1&map_action=pano&pano=tu510ie_z4ptBZYo2BGEJg&viewpoint='+str(pt1.y())+','+str(pt1.x())+'&heading='+str(int(angle)) +'&pitch=10&fov=250')
            webbrowser.open_new('https://www.google.com/maps/@?api=1&map_action=pano&viewpoint='+str(pt1.y())+','+str(pt1.x())+'&heading='+str(int(angle)) +'&pitch=10&fov=250')
            rl.reset()
            rb.reset()           
            self.canvas.unsetMapTool(self)           
            
            # Remove streetview layer
            QgsProject.instance().removeMapLayers([x for x in QgsProject.instance().mapLayers() if 'StreetView' in x])
            self.canvas.refresh()
        def activate(self):
            pass
    
        def deactivate(self):
            pass
           
        def isZoomTool(self):
            return False
    
        def isTransient(self):
            return False
    
        def isEditTool(self):
            return True    