import sys
import os 
# sys.path.insert(0,r'C:\Python27\ArcGIS10.1\Lib\site-packages') # have to check python exe path and foler for sublime
import numpy as np
from gdalconst import *
import gdal, ogr, osr
import pyproj
from shapely.geometry import Polygon, Point
import subprocess
import csv 
import glob


def checkProj():
	"""chekc if the projection of 2 input dataset are consistent 
	"""
	pass
def merge():
	"""
	merege several states 
	"""
	pass

class RasterSum(object):

	def __init__(self, in_zoneVector, in_dataRaster, reprojected=True):
		if reprojected==False:	
			# eheck projection of each dataset by EPSG; convert if not matched
			# gdalwarp->vrt, vrt->tif to avoid inflation size
			# temVRT = in_dataRaster[:-4] + '.vrt'
			# in_dataRasterPro = in_dataRaster[:-4] + '_pro.tif'
			# reprojCom = ' '.join(['/usr/local/bin/gdalwarp',  \
			# 		'-t_srs EPSG:3310 -tap -tr 30 30 -of vrt', in_dataRaster, tmpVRT])
			# subprocess.Popen(reprojCom, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			# vrt2tifCom = ' '.join(['/usr/local/bin/gdal_translate',  \
			# 		'-co compress=LZW', tmpVRT, in_dataRasterPro])
			self.dataRaster = gdal.Open(in_dataRasterPro, GA_ReadOnly)
			self.zoneVector = ogr.Open(in_zoneVector, GA_ReadOnly)
		else:
			self.dataRaster = gdal.Open(in_dataRaster, GA_ReadOnly)
			self.zoneVector = ogr.Open(in_zoneVector, GA_ReadOnly)
		assert(self.dataRaster)
		assert(self.zoneVector)

	def feat_extent_raster(self, geotransform, ft_extent):
		# get the raster origins and pixel sizes
		r_originX = geotransform[0]
		r_originY = geotransform[3]
		pixel_x = geotransform[1]
		pixel_y = geotransform[5]

		# get the feature location offset on raster 
		x1 = int((ft_extent[0] - r_originX) / pixel_x)
		x2 = int((ft_extent[1] - r_originX) / pixel_x) + 1

		y1 = int((ft_extent[3] - r_originY) / pixel_y)
		y2 = int((ft_extent[2] - r_originY) / pixel_y) + 1

		xsize = x2-x1
		ysize = y2-y1
		return (x1, y1, xsize, ysize)

	
	def zoneValueCount(self, regionColumn, sumValue, statename=None):
		"""
		rater pixel dn/value represent categorical 
		data...extract certain value 
		"""

		# Get raster band
		band = self.dataRaster.GetRasterBand(1)
		geotransform = self.dataRaster.GetGeoTransform()

		# Get vector features
		lyr = self.zoneVector.GetLayer(0)
		lyr.ResetReading()
		spatialRef = lyr.GetSpatialRef()

		# input statename != None, use statname to subset shapfiel for 
		# extracting raster values ! 
		if statename:
			statename = '"' + statename + '"'
			lyr.SetAttributeFilter("=".join(['state', statename]))
			ft = lyr.GetNextFeature()			
		else:
			ft = lyr.GetNextFeature()

		ogr_Mem = ogr.GetDriverByName('Memory')
		gdal_Mem = gdal.GetDriverByName('MEM')
		
		valueCount = []
		while ft:
			regionName = ft.GetFieldAsString(regionColumn)
			print 'regionName', regionName

			src_offset = self.feat_extent_raster(geotransform, ft.geometry().GetEnvelope())
			print geotransform
			print ft.geometry().GetEnvelope()
			src_array = band.ReadAsArray(*src_offset)

			print src_offset 
			print src_array
			new_geotransform = (
            	(geotransform[0] + (src_offset[0] * geotransform[1])),
            	geotransform[1],
            	0.0,
            	(geotransform[3] + (src_offset[1] * geotransform[5])),
            	0.0,
            	geotransform[5]
            )

			# Create a temporary vector storing the feature in memory 
			m_ds = ogr_Mem.CreateDataSource('ftcopy')
			proj = osr.SpatialReference()  
			proj.SetWellKnownGeogCS( "EPSG:3310")  
			m_layer = m_ds.CreateLayer('ft_poly', proj, ogr.wkbPolygon)
			m_layer.CreateFeature(ft.Clone())

			# # Create a raster set in mem to store the rasterized feature  
			m_dsRaster = gdal_Mem.Create('', src_offset[2], src_offset[3], 1, gdal.GDT_Byte)
			m_dsRaster.SetGeoTransform(new_geotransform)
			gdal.RasterizeLayer(m_dsRaster, [1], m_layer, burn_values=[1], options =['ALL_TOUCHED=TRUE'])
			vecArray = m_dsRaster.ReadAsArray()	

			# Create a mask to cover those pixels within the polygon
			masked = np.ma.MaskedArray(
				src_array, 
				mask=np.logical_not(vecArray))
			
			# the returned "values" are instance of ma array  
			values, counts = np.unique(masked, return_counts=True)
			# print values.mask
			values = values.tolist(fill_value=None)
			# for i in range(len(values)):
				# print "values %s: counts %d" %(values[i], counts[i])			

			dictpre  = dict(zip(values, counts))
			dictout= dict((k, v) for k, v in dictpre.iteritems() if k != None)
			dictout['county'] = regionName
			valueCount.append(dictout)
			
			del dictpre
			del dictout
			m_ds = None
			m_layer = None
			ft = lyr.GetNextFeature()

		print '# of counties in this dataset: %d' % len(valueCount)
		print valueCount[0]

		with open(sumValue, 'a') as f:
			fieldnames = ['county'] + range(255)
			writer = csv.DictWriter(f, delimiter=',', fieldnames = fieldnames)
			writer.writerows(valueCount)                  

if __name__ == "__main__":

	# in_zoneVector= '/Users/zuya/Desktop/images/cnty24k09_1_multipart.shp'
	# in_dataRaster = '/Users/zuya/Desktop/images/CDL_2012_3310.tif'
	# # in_zoneVector = r"G:\database\pur\PURGIS\shapefiles\cnty24k09_1_multipart.shp"
	# a = RasterSum(in_zoneVector, in_dataRaster)
	# a.zoneValueCount('FIPS', sumValue)




	# reproject the rater files to match the shapfile file geoference 
	# rasters = glob.glob("/Users/zuya/Downloads/2012_cdls/*/*.tif")
	# for i in range(len(rasters)):
	# 	print rasters[i]
	# 	print alphaCode[i]
	# 	com = " ".join(["gdalwarp", "-t_srs EPSG:3310", rasters[i], rasters[i][:-11]+"_3310.tif"])
	# 	subprocess.Popen(com, shell=True)
	# 	print com 

	alphaCode = [os.path.basename(x) for x in glob.glob("/Users/zuya/Downloads/2012_cdls/*")] 
	rasters = glob.glob("/Users/zuya/Downloads/2012_cdls/*/*3310.tif")

	# alphaCode = [os.path.basename(x) for x in glob.glob("H:/abound_bk/cdl/gislayers/cdl2012us/*")]
	# rasters = glob.glob("H:/abound_bk/cdl/gislayers/cdl2012us/*/*3310.tif")

	# create a csv file to hold the output data (append to the file) 
	sumValue = r'/Users/zuya/Dropbox/program/sumValue.csv'
	# with open(sumValue, 'w') as f:
	# 	fieldnames = ['county'] + range(255)
	# 	writer = csv.DictWriter(f, delimiter=',', fieldnames=fieldnames)
	# 	writer.writeheader()
	# print rasters 
	# print alphaCode
	
	# in_zoneVector = r'H:\abound_bk\cdl\gislayers\counties.shp'
	in_zoneVector = '/Users/zuya/Dropbox/program/us_counties3310.shp'

	for i in range(44, len(rasters)):
		print alphaCode[i], rasters[i]
		RasterSum(in_zoneVector, rasters[i]).zoneValueCount('FIPS', sumValue, alphaCode[i])


