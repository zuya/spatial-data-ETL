import psycopg2
import numpy as np
import re


def getdif(dbConn, schema, yearCounty):
	
	#use ST_MakeValid to fix the ring self intersect; 
	#other solution: http://gis.stackexchange.com/questions/157091/cleaning-geometries-in-postgis

	outTable=schema+'.intersect_pur_dwr'+yearCounty
	q0 = "UPDATE "+schema+".dwr"+yearCounty+" SET geom = ST_MakeValid(geom) WHERE ST_IsValid(geom) = 'F';"
	q1 = 'DROP TABLE IF EXISTS '+outTable+';'
	q2 ='CREATE TABLE '+ outTable + '(egid integer NOT NULL,\
		  co_mtrs character varying(11) NOT NULL,\
		  comtrs_percent double precision,\
		  comtrs_acres numeric,\
		  multiuse character varying(1),\
		  class1 character varying(2),\
		  subclass1 character varying(2),\
		  specond1 character varying(1),\
		  pcnt1 character varying(2),\
		  class2 character varying(2),\
		  subclass2 character varying(2),\
		  specond2 character varying(1),\
		  pcnt2 character varying(2),\
		  class3 character varying(2),\
		  subclass3 character varying(2),\
		  specond3 character varying(1),\
		  pcnt3 character varying(2),\
		  irr_typ1pa character varying(1),\
		  irr_typ1pb character varying(1));' 

	q3 = ' '.join(['INSERT INTO '+outTable+'(SELECT e.gid AS egid, p.co_mtrs,\
		 (st_area(st_intersection(e.geom, p.geom))/st_area(p.geom)) AS comtrs_percent, \
		 st_area(p.geom)*0.000247105 AS comtrs_acres,\
		 e.multiuse, e.class1, e.subclass1, e.specond1, e.pcnt1, \
		 e.class2, e.subclass2, e.specond2, e.pcnt2,\
		 e.class3, e.subclass3, e.specond3, e.pcnt3,\
		 e.irr_typ1pa, e.irr_typ1pb \
		 FROM '+schema+'.dwr'+yearCounty+' e, '+schema+'.plsnet_'+ yearCounty[2:4]+' p',
		 'WHERE st_intersects(e.geom, p.geom)',
		 'ORDER BY e.gid, p.co_mtrs);'])

	# check if not s 
	print 'q0',q0
	print 'q1',q1
	print 'q2',q2
	print 'q3',q3
	#get nass data for the targeted crop
	conn = psycopg2.connect(dbConn)
	cursor = conn.cursor()
	cursor.execute(q0)
	cursor.execute(q1)
	cursor.execute(q2)
	cursor.execute(q3)

	conn.commit()
	# nassData = cursor.fetchall()
	cursor.close()
	if conn:
		conn.close()

if __name__== "__main__":
	dbConn = "host='**' dbname='**' user='**' password='##'"
	print "Connecting to database -> %s" % (dbConn)
	schema = 'ca_pest'
	yearCounty = ['97im','97mo','97mt', '04bu','04ss','04su','05yu','06kn','07tu','08yo','09fr','11ma']
	for yc in yearCounty: # ['04bu']:
		print 'year-county %s' % yc
		getdif(dbConn, schema, yc)


# for f in *.shp; do shp2pgsql -d -I -s 2913 $f rlis.`basename $f.shp` > `basename $f.shp`.sql; done
# for f in *.sql; do psql -d portland -f $f; done


