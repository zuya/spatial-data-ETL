import pandas as pd
import psycopg2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import scipy.stats as stats
plt.style.use('ggplot')

def getdif(cdlSum, cdlAtt, dbConn, queryStr):
	
	# get nass data for the targeted crop
	conn = psycopg2.connect(dbConn)
	cursor = conn.cursor()
	cursor.execute(queryStr)
	nassData = cursor.fetchall()
	if conn:
		conn.close()

	nass = []
	keys=['state','county','fips','acre']
	for x in nassData:
		nass.append(dict(zip(keys, x)))

	nass = pd.DataFrame(nass)
	cdl = pd.read_csv(cdlSum)[cdlAtt]
	cdl['county'] = cdl['county'].astype(str)
	nass['acre'] = nass['acre'].astype(np.float64)

	cdl = cdl.merge(pd.DataFrame(nass), how='inner', left_on='county', right_on='fips')
	print type(cdl['1'][0])
	print type(cdl['acre'][0])

	# get the difference between nass and cdl acerage
	dif = cdl['1']-cdl['acre']
	dif = dif.fillna(0)
	dif = dif[dif > np.percentile(dif, 10)]

	## plot histogram
	# hist, bins = np.histogram(np.array(dif), bins=50)
	# width = 0.7 * (bins[1] - bins[0])
	# center = (bins[:-1] + bins[1:]) / 2
	# plt.bar(center, hist, align='center', width=width)
	# print hist
	# print bins

	## qqplot
	stats.probplot(np.array(dif), dist="norm", plot=plt)
	plt.show()

if __name__ == "name":
	cdlSum= r'~/sumValue.csv'
	cdlAtt = ['county', '1']
	dbConn = ""
	print "Connecting to database -> %s" % (dbConn)
	queryStr = "SELECT * FROM ca_pest.nass2012corn"

	getdif(cdlSum, cdlAtt, dbConn, queryStr)