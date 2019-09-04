'''
Created on 29 Jan 2019

@author: thomasgumbricht
'''

import os
import sys
from gdalconst import *
from osgeo import gdal, ogr, osr

class RasterLayer:
    def __init__(self):
        """The constructoris just an empty container.""" 
        
    def SetDS(self,DS): 
        self.datasource =  DS.datasource
        
    def GetLayer(self,bandnr):
        self.layer = self.datasource.GetRasterBand(bandnr)
        
    def GetSpatialRef(self): 
        self.spatialRef = self.proj_cs = self.datasource.GetProjection()
        self.gt = self.datasource.GetGeoTransform()
        
        #self.spatialRef = self.proj_cs = self.layer.GetSpatialRef() 
    def SetSpatialRef(self, tarProj):
        self.spatialRef = tarProj.proj_cs
        self.gt = tarProj.gt
        
    def GetGeometry(self): 
        #Get the necessary band information
        self.lins = self.datasource.RasterYSize
        self.cols = self.datasource.RasterXSize
        self.cellnull = self.layer.GetNoDataValue()
        self.celltype = gdal.GetDataTypeName(self.layer.DataType)
        self.projection = self.datasource.GetProjection()
        self.geotrans = self.datasource.GetGeoTransform()

        #Get the extent of the image
        self.ext=[]
        xarr=[0,self.cols]
        yarr=[0,self.lins]
        for px in xarr:
            for py in yarr:
                x=self.gt[0]+(px*self.gt[1])+(py*self.gt[2])
                y=self.gt[3]+(px*self.gt[4])+(py*self.gt[5])
                self.ext.append([x,y])
            yarr.reverse()
        self.bounds = (self.ext[0][0], self.ext[2][1], self.ext[2][0],self.ext[0][1])
        #Get the spatial resolution
        cellsize = [(self.ext[2][0]-self.ext[0][0])/self.cols, (self.ext[0][1]-self.ext[2][1])/self.lins] 
        if cellsize[0] != cellsize[1]:
            pass
        self.cellsize = cellsize[0]
         
    def CloseLayer(self):
        #close the layer
        self.layer = None
        
class RasterDataSource: 
    def __init__(self):
        """The constructoris just an empty container.""" 
        
    def OpenGDALRead(self,FPN): 
        self.rasterFPN = FPN
        if os.path.exists(self.rasterFPN):
            self.datasource = gdal.Open(FPN, GA_ReadOnly)
            if self.datasource is None:
                exitstr = 'Exiting - Failed to open raster file %s' %(self.rasterFPN)
                sys.exit(exitstr)
        else:
            exitstr = 'Raster datasource %s does not exist' %(self.rasterFPN)
            sys.exit(exitstr)
                                                                                      
    def CloseDS(self):
        #close the datasource
        self.datasource = None

class ExtractRaster: 
    def __init__(self, gt, bbox, lins, cols):
        originX = gt[0]
        originY = gt[3]
        pixel_width = gt[1]
        pixel_height = gt[5]
        #get the cell region to sample
        x1 = int((bbox[0] - originX) / pixel_width)
        x2 = int((bbox[1] - originX) / pixel_width)
        y1 = int((bbox[3] - originY) / pixel_height)
        y2 = int((bbox[2] - originY) / pixel_height)
        xsize = x2 - x1
        ysize = y2 - y1 
        if x1 < 0:
            x1 = 0
        if x1+xsize > cols:
            xsize = cols-x1
        if y1 < 0:
            y1 = 0
        if y1+ysize > lins:
            ysize = lins-y1
        return (x1, y1, xsize+1, ysize+1)
                   
            
    def _ExtractRasterLayer(self,layer,bbox):
        '''
        '''
        #print (layer.gt, bbox, layer.lins, layer.cols)
        src_offset = self._BoundingBox(layer.gt, bbox, layer.lins, layer.cols)
        aVal = layer.layer.ReadAsArray(*src_offset)
        return aVal,src_offset
            
    def _ExtractPoint(self,samplePt):
        x,y = samplePt
        bbox = [ x, x, y, y ]

        rasterLayer = layerinD[band]
        aVal = ExtractRasterLayer(rasterLayer,bbox)[0]
            
    def CloseDS(self):
        #close the datasource
        self.datasource = None
        
def BoundingBox(gt, bbox, lins,cols):
    originX = gt[0]
    originY = gt[3]
    pixel_width = gt[1]
    pixel_height = gt[5]
    #get the cell region to sample
    x1 = int((bbox[0] - originX) / pixel_width)
    x2 = int((bbox[1] - originX) / pixel_width)
    y1 = int((bbox[3] - originY) / pixel_height)
    y2 = int((bbox[2] - originY) / pixel_height)
    xsize = x2 - x1
    ysize = y2 - y1 
    if x1 < 0:
        x1 = 0
    if x1+xsize > cols:
        xsize = cols-x1
    if y1 < 0:
        y1 = 0
    if y1+ysize > lins:
        ysize = lins-y1
    return (x1, y1, xsize+1, ysize+1)
        
def RasterOpenGetFirstLayer(srcRastFPN):
    '''Opens a standard GDAL Raster datasource and gets the first layer
    '''
    #Create an instance of datasource for the source data
    srcDS = RasterDataSource()
    #open the source data for reading    

    srcDS.OpenGDALRead(srcRastFPN)
    #create a layer instance
    srcLayer = RasterLayer()
    #set the datasource of the layer
    srcLayer.SetDS(srcDS)
    
    srcLayer.GetLayer(1)
    #get the spatialref
    srcLayer.GetSpatialRef()
    srcLayer.GetGeometry()
    return srcDS,srcLayer

def ExtractRasterLayer(layer,bbox):
    print (layer.gt, bbox, layer.lins, layer.cols)
    src_offset = BoundingBox(layer.gt, bbox, layer.lins, layer.cols)
    aVal = layer.layer.ReadAsArray(*src_offset)
    return aVal,src_offset

if __name__ == "__main__":
    srcRastFPN ='/Volumes/karttur3tb/ancillary/TRMM/region/rainfall/trmm/199801/rainfall_3b43_trmm_199801_v7-f-m.tif'
    x = 30
    y = 0
    srcDS,srcLayer = RasterOpenGetFirstLayer(srcRastFPN)
    bbox = [ x, x, y, y ]
    aVal,src_offset = ExtractRasterLayer(srcLayer,bbox)
    srcDS.CloseDS()
    print (aVal)