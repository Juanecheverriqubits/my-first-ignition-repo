def read_csv_to_pydataset():
	import csv
	
	path = system.file.openFile("csv")
	file = open(path)
	
	csvData =csv.reader(file)
	
	header = next(csvData)
	data = []
	for row in csvData:
		data.append(row)
	ds = system.dataset.toDataSet(header, data)
	
	pds = system.dataset.toPyDataSet(ds)
	
	file.close()
	return pds
	
def populate_dbtable_from_pydataset(pds, dbTable, dbConn, maxRecs):
	cols = pds.getColumnCount()
	rows = pds.getRowCount()
	
	# clear DB table each time
	queryStr = "TRUNCATE TABLE {:s}".format(dbTable)
	system.db.runUpdateQuery(queryStr, dbConn)
	
	# no inserts if no data
	if rows > 0:
	
		# set up insert query string
		pholders = "({:s})".format(",".join("?"*cols))
		queryStr = "INSERT INTO {:s} VALUES {:s}".format(dbTable, "{pholders}")
		
		# indices for first N records
		minIdx = 0
		maxIdx = maxRecs
		
		# DB inserts in batches of N
		while (maxIdx < rows):
			queryArgs = []
			queryData = []
			for row in pds[minIdx:maxIdx]:
			    queryData.extend(row)
			    queryArgs.append(pholders)
			    
			queryStr1 = queryStr.format(pholders=",".join(queryArgs))
			
			# insert N rows into DB
			system.db.runPrepUpdate(queryStr1, queryData, dbConn)
			
			# advance indices for next N records
			minIdx = maxIdx
			maxIdx += maxRecs
			
		# handle any leftover records
		maxIdx = rows
		queryArgs = []
		queryData = []
		for row in pds[minIdx:maxIdx]:
		    queryData.extend(row)
		    queryArgs.append(pholders)
		
		queryStr2 = queryStr.format(pholders=",".join(queryArgs))
		
		# insert remaining rows into DB
		system.db.runPrepUpdate(queryStr2, queryData, dbConn)
		    