#-------------------------
# Librairies de fonctions
#------------------------

import javax.management as mgmt									
import os,re,time
execfile('%s' % os.environ["PYTHON_LIBRARY"])

#--------------------
# PROGRAMME PRINCIPAL
#--------------------

SA_NAME = sys.argv[0]										# SA name provided : SA_nrj-itest3_app

cellule  = getCellId()										# Cell ID : parva2406514Network(cells/parva2406514Network|cell.xml#Cell_1)
cellName = getCellName()									# Cell name : parva2406514Network
nodes = getObjectsOfType('Node', cellule)							# Cell's nodes

recherche = 'UNKNOWN'

appServers = getObjectsOfType('Server')								# Node's applications
for server in appServers:
        servers = getObjectAttribute(server,"name")
        if SA_NAME == servers:
                SAid = server                                                                   # SA ID
                posStringNode = SAid.find("nodes")
		posFin = SAid.find("/",posStringNode + 6)
		nodeName = SAid[posStringNode+6:posFin]						# Node's SA
                recherche = 'FOUND'
		serverName = SA_NAME

if (recherche == "FOUND"):
	apps = listAppOfSA(cellName,nodeName,SA_NAME)						# Applications of the SA
	nbApps = int(len(apps))

	if (nbApps > 0):
		compteur = 1
		for appli in apps:
			if appli != "ibmasyncrsp":
				print "Application : ",appli
				print ""
				idJVM = AdminConfig.list('JavaVirtualMachine', SAid)            # JVM ID

				getDbList2(SAid,appli)
				getUrlList2(SAid,appli)
				getEnvList2(SAid,appli)

				compteur = compteur + 1						# Incrementation du nb d applications
	else:
		print 'WARNING : No application installed !'
		#getDbList2(SAid)
		#getUrlList2(SAid)
		#getEnvList2(SAid)
		sys.exit(8)
else :
	print '\nERROR : This application server \"' + SA_NAME + '\" has not been found. Please check the name given.'
	sys.exit(2)
