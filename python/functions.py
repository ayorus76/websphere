#-------------------
# Import des modules
#-------------------

#execfile('wsadminlib.py')

_modules = [
            'sys',
            'time',
            're',
            'glob',
            'os',
            'getopt',
            'traceback',
            'javax.management',
           ]

for module in _modules:
  if module == "javax.management":
	import javax.management as mgmt
  else:
  	try:
    		locals()[module] = __import__(module, {}, {}, [])
  	except ImportError:
    		print 'Error importing %s.' % module

#--------------------
# Variables globales
#--------------------

#-----------------------
# Methodes de wsadminlib
#-----------------------
try:
    AdminConfig = sys._getframe(1).f_locals['AdminConfig']
    AdminApp = sys._getframe(1).f_locals['AdminApp']
    AdminControl = sys._getframe(1).f_locals['AdminControl']
    AdminTask = sys._getframe(1).f_locals['AdminTask']
except:
    print "Warning: Caught exception accessing Admin objects. Continuing."

#-------------------------------------------------------------------------------
# Conversion chaine de caracteres en crochets en une liste (separateur : espace)
#-------------------------------------------------------------------------------
def _splitlist(s):
    if s[0] != '[' or s[-1] != ']':
        raise "Invalid string: %s" % s
    return s[1:-1].split(' ')

#---------------------------------
# Decoupage de lignes en une liste
#---------------------------------
def _splitlines(s):
  rv = [s]
  if '\r' in s:
    rv = s.split('\r\n')
  elif '\n' in s:
    rv = s.split('\n')
  if rv[-1] == '':
    rv = rv[:-1]
  return rv

#--------------------------------------
# Suppression caractere de fin de ligne
#--------------------------------------
def _noendcar(s):
	if '\n' in s:
		rv = s.replace('\n',"")
	else:
		rv = s
	return rv

#-------------------------------------------------------------------------
# Conversion d une liste en une chaine de caracteres (separateur : espace)
#-------------------------------------------------------------------------
def listToString(s):
	s = "".join(s)
	return s

#-------------------------------------------------------
# Verification de l existence et de l acces à un fichier
#-------------------------------------------------------

def checkFic(fic):
        try:
                #obFic = open(fic,"r", encoding = "Latin-1")
                obFic = open(fic,"r")
                obFic.close()
                return 1
        except:
                print("Probleme lors de l ouverture du fichier ",fic)
                sys.exit(10)

#--------------------------------
# Valeur de l attribut d un objet
#--------------------------------
def getObjectAttribute(objectid, attributename):
	attributename = "\'"+attributename+"\'"
	result = AdminConfig.showAttribute(objectid,attributename)
	if result != None and result.startswith("[") and result.endswith("]"):
        	result = _splitlist(result)
    	return result

#---------------------------------------------------------------
# Liste des ID d objets definis dans une portee (fournie ou non)
#---------------------------------------------------------------
def getObjectsOfType(typename, scope = None):
	m = "getObjectsOfType:"
	if scope:
		return AdminConfig.list(typename, scope).splitlines()
	else:
		return AdminConfig.list(typename).splitlines()

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ID d un objet fourni
# exemple : getCfgItemId("server",currentNode,serverName,"JDBCProvider:/DataSource")
#	    DefaultEJBTimerDataSource(cells/parva2406514Network/nodes/parva2406514/servers/SA_cij-archetypejsf_app|resources.xml#DataSource_1000001)
#	    cij-archetypejsf_ds_helloworld(cells/parva2406514Network/nodes/parva2406514/servers/SA_cij-archetypejsf_app|resources.xml#DataSource_1375360536809)
# autre exemple : print getCfgItemId("server",currentNode,serverName,"JDBCProvider:/DataSource","cij-archetypejsf_ds_helloworld")
#		  cij-archetypejsf_ds_helloworld(cells/parva2406514Network/nodes/parva2406514/servers/SA_cij-archetypejsf_app|resources.xml#DataSource_1375360536809)	  
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

def getCfgItemId(scope, nodeName, serverName, objectType="", item="/"):	# Si item non fourni, par défaut, affichage de tous les objets
    if (scope == "cell"):
        cellName = getCellName()
        cfgItemId = AdminConfig.getid("/Cell:"+cellName+"/"+objectType+":"+item)
    elif (scope == "node"):
        cfgItemId = AdminConfig.getid("/Node:"+nodeName+"/"+objectType+":"+item)
    elif (scope == "server"):
        cfgItemId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/"+objectType+":"+item)
    elif (scope == "None"):
	cfgItemId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
    return cfgItemId

#------------------------
# Nom et ID d une cellule
#------------------------
def getCellName():
    cellname = AdminControl.getCell()
    return cellname

def getCellId(cellname = None):
    if cellname == None:
        cellname = getCellName()
    return AdminConfig.getid( '/Cell:%s/' % cellname )

#--------------
# ID d un noeud
#--------------
def getNodeId( nodename ):
    return AdminConfig.getid( '/Cell:%s/Node:%s/' % ( getCellName(), nodename ) )

#----------------------------------------------------------------------------
# Recuperation d'objets cibles
# exemple : getObjectByNodeAndName('parva2406515','Node','ApplicationServer')
#----------------------------------------------------------------------------

def getObjectByNodeAndName( nodename, typename, objectname ):
    node_id = getNodeId(nodename)
    all = _splitlines(AdminConfig.list( typename, node_id ))
    result = None
    for obj in all:
        name = AdminConfig.showAttribute( obj, 'name' )
        if name == objectname:
            if result != None:
                raise "FOUND more than one %s with name %s" % ( typename, objectname )
            result = obj
    return result

#-------------------------------
# ID d un serveur d applications
#-------------------------------

def getServerId(nodename,servername):
    id = getObjectByNodeAndName(nodename, "Server", servername) # app server
    if id == None:
        id = getObjectByNodeAndName(nodename, "ProxyServer", servername)
    return id

#------------------------------------------------
# Liste des applications que renferme un SA donne
#------------------------------------------------

def listAppOfSA(cellName,nodeName,serverName):
	apps = _splitlines(AdminApp.list("Websphere:cell=" + cellName + ",node=" + nodeName + ",server=" + serverName))
	return apps

#-----------------------------------
# Ressources JNDI a partir nom appli
#-----------------------------------

def getListJndiByAppli(appName):
	appMgmt = mgmt.ObjectName(AdminControl.completeObjectName("WebSphere:*,type=AppManagement"))
	appInfo = AdminControl.invoke_jmx(appMgmt, "getApplicationInfo", [appName, java.util.Hashtable(), None], ["java.lang.String", "java.util.Hashtable", "java.lang.String"])
	return appInfo

#-------------------------------------
# Recuperation url a partir datasource
#-------------------------------------

def getUrlByDs(ds):
	DS_customProp = AdminConfig.showAttribute(ds, 'propertySet')
	DS_ressourceProp = AdminConfig.showAttribute(DS_customProp, 'resourceProperties')
	rpsarray = DS_ressourceProp[1:len(DS_ressourceProp)-1].split(' ')
	for rp in rpsarray:
		name = AdminConfig.showAttribute(rp, 'name')
		if name == 'URL':
			urlDs = AdminConfig.showAttribute(rp, 'value')
			return urlDs

#-----------------------------------------
# Ressources JNDI pour les ressources JDBC 
#-----------------------------------------

def JndiNameRelation_ds_url(application,findAuth="Auth"):
	listAppinfo = getListJndiByAppli(application)
	for task in listAppinfo :
		if (task.getName() == "MapResRefToEJB") :
			dico = {}
			resRefs = task.getTaskData()
			
			if resRefs is not None:
				champResAppli = 5
				champResWeb = 8
				for i in range(1,len(resRefs)):
					cle=resRefs[i][champResWeb]
					valeur=resRefs[i][champResAppli]
					dico[cle] = valeur	
	return dico

#----------------------------------------
# Ressources JNDI pour les ressources ENV
#----------------------------------------

def JndiNameRelation_env(application,findAuth="Auth"):
        listAppinfo = getListJndiByAppli(application)
        for task in listAppinfo :
                if (task.getName() == "MapResEnvRefToRes") :
                	dico = {}
                        resRefs = task.getTaskData()
                        if resRefs != None:
                        	champResAppli = 3
                        	champResWeb = 5
                        	for i in range(1,len(resRefs)):
                                	cle=resRefs[i][champResWeb]
                                	valeur=resRefs[i][champResAppli]
                                	dico[cle] = valeur
	return dico

#-----------------------------------------------------------------
# Recherche de la ressource JNDI Web fourni dans le fichier .props
# Fait elle partie des ressources actuelles dans l'application ? 
# Pour les ressources URL et DS
#-----------------------------------------------------------------

def retrieveJNDI(application,jndiName,findAuth="Auth"):
	listAppinfo = getListJndiByAppli(application)
	for task in listAppinfo :
		if (task.getName() == "MapResRefToEJB") :
			resRefs = task.getTaskData()
			dico = {}
			champResAppli = 5
			champResWeb = 8
			for i in range(1,len(resRefs)):
				dico[resRefs[i][champResAppli]] = resRefs[i][champResWeb] 
	try:
		if dico[jndiName] != None:
			return dico[jndiName]
	except:
		dico = None
		return dico

#-----------------------------------------------------------------
# Recherche de la ressource JNDI Web fourni dans le fichier .props
# Fait elle partie des ressources actuelles dans l'application ?
# Pour les ressources ENV
#-----------------------------------------------------------------

def retrieveJNDI_env(application,jndiName,findAuth="Auth"):
        listAppinfo = getListJndiByAppli(application)
	for task in listAppinfo :
		if (task.getName() == "MapResEnvRefToRes") :
			resRefs = task.getTaskData()
			if resRefs != None:
				dico = {}
				champResAppli = 3
				champResWeb = 5
				for i in range(1,len(resRefs)):
					dico[resRefs[i][champResAppli]] = resRefs[i][champResWeb]
	try :
		if dico[jndiName] != None:
			return dico[jndiName]
	except:
		dico = None
		return dico

#-------------------------------
# ID du container de deploiement 
#-------------------------------

def configureFederation(appName):
	appDeploymentContainment = '/Deployment:%s/ApplicationDeployment:/' % (appName)
	appDeployment = AdminConfig.getid(appDeploymentContainment)
	return appDeployment

#-------------------------------------------------------------------------
# Chemin des log4j, des shared libs et des shared classes pour un SA donne
#-------------------------------------------------------------------------

def getLibrairies():
        libraryId = getCfgItemId("server",nodeName,serverName,"Library")
        print '- Chemin des log4j,des shared libs et des shared classes : '
        if libraryId:
                librairies = AdminConfig.showAttribute(libraryId,'classPath').split(";")
                for i in librairies:
                	print i
        else:
                print "Non defini"
                print '\n'

#----------------------------------------------------------------------
# Conversion du fichier de configuration xml d'un SA en un fichier plat
#----------------------------------------------------------------------

def extractConfigProperties( nodename, servername, propsfilename, ):
	m = "extractConfigProperties:"
	arglist = ['-propertiesFileName',propsfilename,'-configData','Server=%s' % ( servername )]
	sop(m,"Calling AdminTask.extractConfigProperties() with arglist=%s" % ( arglist ))
	return AdminTask.extractConfigProperties( arglist )

#----------------------------------------------------------------
# Methode permettant de formater l affichage de certaines valeurs
# appelees avec certaines methodes AdminApp.view par exemple
#----------------------------------------------------------------

def getAdminAppViewValue(appname, keyname, parsename):
	m = "getAdminAppViewValue:"
	sop(m,"Entry. appname=%s keyname=%s parsename=%s" % ( appname, keyname, parsename ))
	verboseString = AdminApp.view(appname, [keyname])
	sop(m,"verboseString=%s" % ( verboseString ))
	verboseStringList = _splitlines(verboseString)
	for str in verboseStringList:
		if str.startswith(parsename):
			resultString = str[len(parsename):].strip()
			sop(m,"Exit. Found value. Returning >>>%s<<<" % ( resultString ))
			return resultString
	sop(m,"Exit. Did not find value. Returning None.")
	return None

#-----------------------------------
# Caracteristiques d un Virtual Host
#-----------------------------------

def getApplicationVirtualHost(appname):
	return getAdminAppViewValue(appname, "-MapWebModToVH", "Virtual host:")

#----------------------------------
# Modification d une ressource JDBC
#----------------------------------

def changeURLDatasource(ds,url):
        DS_customProp = AdminConfig.showAttribute(ds, 'propertySet')
        # ressource properties
        DS_ressourceProp = AdminConfig.showAttribute(DS_customProp, 'resourceProperties')
        # recherche de la valeur de url datasource
        rpsarray = DS_ressourceProp[1:len(DS_ressourceProp)-1].split(' ')
        for rp in rpsarray:
                name = AdminConfig.showAttribute(rp, 'name')
                if name == 'URL':
                        urlDs = AdminConfig.showAttribute(rp, 'value')
			print "Mise à jour de la datasource avec la valeur suivante : %s" % url
                        AdminConfig.modify(rp, [["name", "URL"],["value", url]])

#------------------------------------------------------------------------------------
# Modification des parametres de connexion à une base de donnees (Alias, user / pass)
#------------------------------------------------------------------------------------

def changeAlias(ds,userName,passValue):
	AuthName = AdminConfig.showAttribute(ds, 'authDataAlias')

	authList = AdminConfig.list('JAASAuthData').split("\n")
	for authAlias in authList:
		theAlias = AdminConfig.showAttribute(authAlias, 'alias')
		if theAlias == AuthName :
			currentAlias = AdminConfig.showAttribute(authAlias, 'alias')
			currentUser = AdminConfig.showAttribute(authAlias, 'userId')
			currentPwd = AdminConfig.showAttribute(authAlias, 'password')
			print("Informations actuelles du schema (login - mdp) : %s/%s (alias : %s)" % (currentUser,currentPwd,currentAlias))
			userid = ['userId', userName]
			password = ['password', passValue]
			print "Mise à jour du schema %s avec les valeurs suivantes : %s - %s" % (AuthName,userName,passValue) 
			AdminConfig.modify(authAlias, [['userId', userName],['password', passValue]])
	
#---------------------------------
# Modification d une ressource ENV
#---------------------------------

def changeREEpropriety(idRess,jndiAppli,nomRess,allProperties,node,sa):
	print ""
	PropertyCouple = {}
	PropertyNames = []
	for cle, valeur in allProperties.items():
		nomProperty = PropertyNames.append(valeur[0])
		PropertyCouple[valeur[0]] = valeur[1]
	#print("PropertyNames : %s" % PropertyNames)

	nbProps = len(allProperties)

	idSA = getServerId(node,sa)
	cellname = getCellName()
	ressProviderIds = getObjectsOfType('ResourceEnvironmentProvider','%s' % idSA)

	currentProperties = []
	for ressProviderId in ressProviderIds:
		reeProviderName = getObjectAttribute(ressProviderId, 'name')
		reeEntryIds = _splitlines(AdminConfig.getid('/Cell:' + cellname + '/Node:' + node + '/Server:' +  sa + '/ResourceEnvironmentProvider:' + reeProviderName + '/ResourceEnvEntry:/'))
	
		for reeEntry in reeEntryIds:
			if reeEntry == idRess:
				reeName = getObjectAttribute(reeEntry, 'name')
				reeJndiNameWeb = getObjectAttribute(reeEntry, 'jndiName')
				reepropertySetId = getObjectAttribute(reeEntry, 'propertySet')
				J2EEResourcePropertyIds = _splitlines(AdminConfig.list('J2EEResourceProperty',reepropertySetId))
				#print("J2EEResourcePropertyIds : %s" % J2EEResourcePropertyIds)
				
				for J2EEResourceProperty in J2EEResourcePropertyIds:
					J2EEResourcePropertyName = getObjectAttribute(J2EEResourceProperty, 'name')
					#print("J2EEResourcePropertyName : %s" % J2EEResourcePropertyName)
					J2EEResourcePropertyValue = getObjectAttribute(J2EEResourceProperty, 'value')
					currentProperties.append(J2EEResourcePropertyName)
					if J2EEResourcePropertyName in PropertyNames:
						# Existence de la propriete
						# La propriete existe deja, il s agit donc d une simple modification
						print "Modification, pour la ressource env (%s), de la propriete : %s, nouvelle valeur : %s" % (jndiAppli,J2EEResourcePropertyName,PropertyCouple[J2EEResourcePropertyName])
						AdminConfig.modify(J2EEResourceProperty,[['name',J2EEResourcePropertyName],['value',PropertyCouple[J2EEResourcePropertyName]]])
					else:
						# La propriete n existe pas, il s agit de la supprimer pour etre conforme avec la FMOE 
						# puis re creation de la propriete
						print "Suppression, pour la ressource env (%s), de la propriete (%s), dont la valeur est : %s" % (jndiAppli,J2EEResourcePropertyName,J2EEResourcePropertyValue)
						AdminConfig.remove(J2EEResourceProperty)
	#print("currentProperties : %s" % currentProperties)
	for newProperty in PropertyNames:
		if newProperty not in currentProperties:
			print "Creation, pour la ressource env (%s), d une nouvelle propriete (%s), dont la valeur est : %s" % (jndiAppli,newProperty,PropertyCouple[newProperty])
			AdminConfig.create('J2EEResourceProperty', reepropertySetId, [['name',newProperty],['value',PropertyCouple[newProperty]]])

#-------------------------------------
# Status d un serveur d applications
# True : SA demarre, False : SA stoppe
#-------------------------------------

def isServerRunning(nodename,servername):
    mbean = AdminControl.queryNames('type=Server,node=%s,name=%s,*' % (nodename,servername))
    return mbean

#---------------------------
# Synchronisation d un noeud
#---------------------------

def SyncNode(nodename):
	Sync1 = AdminControl.completeObjectName('type=NodeSync,node=' + nodename + ',*')
	return AdminControl.invoke(Sync1, 'sync')

#-----------------------------------
# Demarrage et arret d un web server
#-----------------------------------

def startWebServer( nodename, servername):
    m = "startWebServer: "
    sop(m,"Entry.")
    sop(m,"Got arguments: nodename=%s, servername=%s" % (nodename,servername))
    mbean = AdminControl.queryNames('WebSphere:type=WebServer,*')
    sop(m,mbean)
    cell = AdminControl.getCell()
    sop(m,cell)
    webServerUp = AdminControl.invoke(mbean,'start','[%s %s %s]' % (cell,nodename,servername),'[java.lang.String java.lang.String java.lang.String]')
    sop(m,webServerUp)

def stopWebServer( nodename, servername):
    m = "stopWebServer: "
    sop(m,"Entry.")
    sop(m,"Got arguments: nodename=%s, servername=%s" % (nodename,servername))
    mbean = AdminControl.queryNames('WebSphere:type=WebServer,*')
    sop(m,mbean)
    cell = AdminControl.getCell()
    sop(m,cell)
    webServerDown = AdminControl.invoke(mbean,'stop','[%s %s %s]' % (cell,nodename,servername),'[java.lang.String java.lang.String java.lang.String]')
    sop(m,webServerDown)

#----------------------------------------
# Variables definissant le tmps d attente 
# avant demarrage d un SA
#----------------------------------------

# Global variable defines extra time to wait for a server to start, in seconds.
waitForServerStartSecs = 300

def setWaitForServerStartSecs(val):
    """Sets global variable used to wait for servers to start, in seconds."""
    global waitForServerStartSecs
    waitForServerStartSecs = val

def getWaitForServerStartSecs():
    """Returns the global variable used to wait for servers to start, in seconds."""
    global waitForServerStartSecs
    return waitForServerStartSecs

#----------------------------------
# Arret d un serveur d applications
#----------------------------------

def stopServer(nodename,servername):
	print "\n------------------------"
	print "STOP SERVER APPLICATION "
	print "------------------------"

	if isServerRunning(nodename,servername):
        	serverStatus=AdminControl.queryNames('WebSphere:*,type=Server,node=%s,process=%s' % (nodename, servername))
        	AdminControl.invoke(AdminControl.queryNames('WebSphere:*,type=Server,node=%s,process=%s' % (nodename, servername)), 'stop')
		
		while isServerRunning(nodename,servername):
        		print "Serveur toujours present ...."
        		time.sleep( 10 )
		print "Serveur arrete"
	else:
		print "Le serveur semble deja arrete."

#--------------------------------------
# Demarrage d un serveur d applications
#--------------------------------------

def startServer(nodename,servername):
	m = "startServer:"
	if isServerRunning(nodename,servername):
		sop(m,"Le serveur %s,%s est deja demarre" % (nodename,servername))
	else:
		print "\n-------------------------"
		print "START SERVER APPLICATION"
		print "-------------------------"
		sop(m,"Demarrage du serveur %s,%s" % (nodename,servername))
		try:
			sop(m,"startServer(%s,%s)" % (servername,nodename))
			AdminControl.startServer(servername,nodename,240)
			
			global waitForServerStartSecs
			waitRetries = waitForServerStartSecs / 15
			if waitRetries < 1:
				waitRetries = 1
			retries = 0
			while not isServerRunning(nodename,servername) and retries < waitRetries:
				sop(m,"Le serveur %s,%s est toujours en cours de demarrage, merci de patienter encore 15 secs" % (nodename,servername))
				time.sleep(15)  # seconds
				retries += 1
			if not isServerRunning(nodename,servername) :
				sop(m,"server %s,%s STILL not running, giving up" % (nodename,servername))
				raise Exception("SERVER FAILED TO START %s,%s" % (nodename,servername))
			else:
				print "Le serveur est à present demarre."
				print ""
		
		except:
			( exception, parms, tback ) = sys.exc_info()
			if -1 != repr( parms ).find( "already running" ):
				return
			sop(m,"EXCEPTION STARTING SERVER %s" % servername)
			sop(m,"Exception=%s\nPARMS=%s" % ( str( exception ), repr( parms ) ))
			raise Exception("EXCEPTION STARTING SERVER %s: %s %s" % (servername, str(exception),str(parms)))

#----------------
# Divers methodes 
#----------------

def getSopTimestamp():
    formatting_string = "[" + "%" + "Y-" + "%" + "m" + "%" + "d-" + "%" + "H" + "%" + "M-" + "%" + "S00]"
    return time.strftime(formatting_string)

DEBUG_SOP=0

def enableDebugMessages():
    global DEBUG_SOP
    DEBUG_SOP=1
    sop('enableDebugMessages', 'Verbose trace messages are now enabled; future debug messages will now be printed.')

def disableDebugMessages():
    global DEBUG_SOP
    sop('enableDebugMessages', 'Verbose trace messages are now disabled; future debug messages will not be printed.')
    DEBUG_SOP=0

#-------------------------
# Formatage de l affichage
#-------------------------

def sop(methodname,message):
    global DEBUG_SOP
    if(DEBUG_SOP):
        timestamp = getSopTimestamp()
        print "%s %s %s" % (timestamp, methodname, message)

def emptyString(strng):
    if None == strng or "" == strng:
        return True
    return False

#-----------------------------------
# Visualisation d une ressource jdbc
#-----------------------------------

def viewDbRessProperties(idRess):
	dsJndiNameWeb = getObjectAttribute(idRess, 'jndiName')
	alias = getObjectAttribute(idRess, 'authDataAlias')
	
	dsUrl = getUrlByDs(idRess)
        authList = AdminConfig.list('JAASAuthData').split("\n")
	for authAlias in authList:
		theAlias = getObjectAttribute(authAlias, 'alias')
                if alias == theAlias:
			dsAlias = alias
                        dsLogin = getObjectAttribute(authAlias, 'userId')
                        dsPasswd = getObjectAttribute(authAlias, 'password')
	print "Nom JNDI defini dans WebSphere : %s" % dsJndiNameWeb
	print "Alias du schema : %s" % dsAlias
        print "Login du schema : %s" % dsLogin
        print "Instance : %s" % dsUrl

#--------------------------------------------
# Visualisation d une ressource environnement
#--------------------------------------------

def viewReeProperties(idRess):
	providerId = getObjectAttribute(idRess,'provider')
	print "Provider : %s" % getObjectAttribute(providerId,'name')
	print "Nom JNDI de l entree dans WAS : %s" % getObjectAttribute(idRess,'jndiName')
	referenceableId = getObjectAttribute(idRess,'referenceable')
	print "Fabrique : %s" % getObjectAttribute(referenceableId,'factoryClassname')
	print "Classe : %s" % getObjectAttribute(referenceableId,'classname')
	propertySetId = getObjectAttribute(idRess,'propertySet')
	resourcePropertiesIds = _splitlines(AdminConfig.list('J2EEResourceProperty',propertySetId))
	print "Valeurs de l entree : "
	for resourceProperty in resourcePropertiesIds:
		entryPropertyName = AdminConfig.showAttribute(resourceProperty,'name')
		entryPropertyValue = AdminConfig.showAttribute(resourceProperty,'value')
		print "Nom : ",entryPropertyName,", Valeur : ",entryPropertyValue
	
#---------------------------
# Creation d un SA generique
#---------------------------

def CreateNewSA(node,sa):
	rechSA=AdminConfig.list('Server',"*%s*" % sa)
	if rechSA is None or rechSA == "":
		idNewSA = AdminServerManagement.createApplicationServer(node,sa,"default")
		AdminConfig.save()
		print "Server %s created" % sa
		return idNewSA
	else:
		print "Server %s already exists" % sa
		return rechSA

#-----------------------------------------
# Verification existence SA et application
#-----------------------------------------

def checkIfSAexists(sa):
	cellule  = getCellId()
	cellName = getCellName()
	nodes = getObjectsOfType('Node', cellule)

	SAid = None
	nodeName = None
	appliName = None

	recherche = 'non trouve'
	appServers = getObjectsOfType('Server')	
	for server in appServers:
		servers = getObjectAttribute(server,"name")
		if sa == servers:
			SAid = server 
			posStringNode = SAid.find("nodes")
			posFin = SAid.find("/",posStringNode + 6)
			nodeName = SAid[posStringNode+6:posFin]
			#posNodeName = posStringNode + 6
			#nodeName = SAid[posNodeName:(posNodeName + 12)]
			recherche = 'trouve'

	if (recherche == "trouve"):
		apps = listAppOfSA(cellName,nodeName,sa)
		nbApps = int(len(apps))

		if (nbApps > 0):
			for appli in apps:
				if appli != "ibmasyncrsp":
					idJVM = AdminConfig.list('JavaVirtualMachine', SAid) 
					appliName = appli
	return SAid,nodeName,appliName

#-------------------------------------------
# Liste des ressources JDBC pour un SA donne
#-------------------------------------------

def getDbList(scope,application):
	idDatasources = getObjectsOfType('DataSource',scope)

	nbDatasources = int(len(idDatasources))
	if len(idDatasources) != 0:
		dico = JndiNameRelation_ds_url(application)
		if dico is not None:
			compteur=1
			for datasource in idDatasources:
				dsName = getObjectAttribute(datasource, 'name')
				if ((dsName != "DefaultEJBTimerDataSource") and (dsName != "Oracle JDBC Driver XA DataSource")):
					print "Ressource JDBC n°%s" % compteur,":"
					print "ds%s.ID=%s" % (str(compteur),datasource)
					dsJndiNameWeb = getObjectAttribute(datasource, 'jndiName')
					for k in dico.keys():
						if k == dsJndiNameWeb:
							dsJndiNameApp = dico[dsJndiNameWeb]
							dsUrl = getUrlByDs(datasource)

							print "ds%s" % str(compteur)+".JDBC_JNDI_WEB=%s" % dsJndiNameWeb,"(%s)" % dsName
                                                        print "ds%s" % str(compteur)+".JDBC_JNDI_APPLI=%s" % dsJndiNameApp

                                                        alias = getObjectAttribute(datasource, 'authDataAlias')
                                                        authList = AdminConfig.list('JAASAuthData').split("\n")
                                                        for authAlias in authList:
                                                                theAlias = getObjectAttribute(authAlias, 'alias')
                                                                if alias == theAlias:
                                                                        dsAlias = alias
                                                                        dsLogin = getObjectAttribute(authAlias, 'userId')
                                                                        dsPasswd = getObjectAttribute(authAlias, 'password')
                                                        print "ds%s" % str(compteur)+".JDBC_ALIAS=%s" % dsAlias
                                                        print "ds%s" % str(compteur)+".JDBC_ALIAS_USER=%s" % dsLogin
                                                        print "ds%s" % str(compteur)+".JDBC_ALIAS_PASS=%s" % dsPasswd
                                                        print "ds%s" % str(compteur)+".JDBC_URL=%s" % dsUrl
                                                        print "\n"
                                                        compteur = compteur + 1
		else:
			print "Erreur rencontrée lors de la recuperation de la configuration des ressources dans le bindings."
	else:
		print "Aucune base de donnees n est definie pour cette application."
		print ""

def getDbList2(scope,application=None):
        idDatasources = getObjectsOfType('DataSource',scope)

	nbDatasources = int(len(idDatasources))
	if len(idDatasources) != 0:
                dico = JndiNameRelation_ds_url(application)
                if dico is not None:
                        compteur=1
                        for datasource in idDatasources:
                                dsName = getObjectAttribute(datasource, 'name')
                                if ((dsName != "DefaultEJBTimerDataSource") and (dsName != "Oracle JDBC Driver XA DataSource")):
                                        dsJndiNameWeb = getObjectAttribute(datasource, 'jndiName')
                                        for k in dico.keys():
                                                if k == dsJndiNameWeb:
                                                        dsJndiNameApp = dico[dsJndiNameWeb]
                                                        dsUrl = getUrlByDs(datasource)

                                                        #print "ds%s" % str(compteur)+".JDBC_TYPE_ACTION=update"
                                                        print "ds%s" % str(compteur)+".JDBC_JNDI_WEB=%s" % dsJndiNameWeb
                                                        print "ds%s" % str(compteur)+".JDBC_JNDI_APPLI=%s" % dsJndiNameApp

                                                        #alias = getObjectAttribute(datasource, 'authDataAlias')
                                                        #authList = AdminConfig.list('JAASAuthData').split("\n")
                                                        #for authAlias in authList:
                                                                #theAlias = getObjectAttribute(authAlias, 'alias')
                                                                #if alias == theAlias:
                                                                        #dsAlias = alias
                                                                        #dsLogin = getObjectAttribute(authAlias, 'userId')
                                                                        #dsPasswd = getObjectAttribute(authAlias, 'password')
                                                        #print "ds%s" % str(compteur)+".JDBC_ALIAS=%s" % dsAlias
                                                        #print "ds%s" % str(compteur)+".JDBC_ALIAS_USER=%s" % dsLogin
                                                        #print "ds%s" % str(compteur)+".JDBC_ALIAS_PASS=%s" % dsPasswd
                                                        #print "ds%s" % str(compteur)+".JDBC_URL=%s" % dsUrl
                                                        print "\n"
                                                        compteur = compteur + 1

#------------------------------------------
# Liste des ressources URL pour un SA donne
#------------------------------------------

def getUrlList(scope,application):
        urlsId = getObjectsOfType('URL',scope)
	
	nbUrls = int(len(urlsId))
	if len(urlsId) != 0 :
		dico = JndiNameRelation_ds_url(application)
		compteur=1
        	for url in urlsId:
                        print "Ressource URL n°%s" % compteur,":"
                        print "url%s.ID=%s" % (str(compteur),url)
               		urlName = getObjectAttribute(url, 'name')
                       	urlJndiNameWeb = getObjectAttribute(url, 'jndiName')
			for k in dico.keys():
				if k == urlJndiNameWeb:
					urlJndiNameApp = dico[urlJndiNameWeb]
                       			urlSpec = getObjectAttribute(url, 'spec')
                        		
					print "url%s" % str(compteur)+".URL_JNDI_WEB=%s" % urlJndiNameWeb,"(%s)" % urlName
                        		print "url%s" % str(compteur)+".URL_JNDI_APPLI=%s" % urlJndiNameApp
                        		print "url%s" % str(compteur)+".URL_SPEC=%s" % urlSpec
                        		print "\n"
                        		compteur = compteur + 1
	else:
		print "Aucune ressource url n est definie pour cette application."
		print ""

def getUrlList2(scope,application=None):
        urlsId = getObjectsOfType('URL',scope)

	nbUrls = int(len(urlsId))
	if len(urlsId) != 0:
                dico = JndiNameRelation_ds_url(application)
                compteur=1
                for url in urlsId:
                        #print "URL resource n°%s" % compteur,":"
                        urlName = getObjectAttribute(url, 'name')
                        urlJndiNameWeb = getObjectAttribute(url, 'jndiName')
                        for k in dico.keys():
                                if k == urlJndiNameWeb:
                                        urlJndiNameApp = dico[urlJndiNameWeb]
                                        urlSpec = getObjectAttribute(url, 'spec')

                                        #print "url%s" % str(compteur)+".URL_TYPE_ACTION=update"
                                        print "url%s" % str(compteur)+".URL_JNDI_WEB=%s" % urlJndiNameWeb
                                        print "url%s" % str(compteur)+".URL_JNDI_APPLI=%s" % urlJndiNameApp
                                        #print "url%s" % str(compteur)+".URL_SPEC=%s" % urlSpec
                                        print "\n"
                                        compteur = compteur + 1

#------------------------------------------
# Liste des ressources ENV pour un SA donne
#------------------------------------------

def getEnvList2(scope,application=None):
        ressProviderIds = getObjectsOfType('ResourceEnvironmentProvider',scope)

	nbressProviders = int(len(ressProviderIds))
	if len(ressProviderIds) != 0:
                if application is not None:
                        dico = JndiNameRelation_env(application)

                        if nbressProviders > 0:
                                listProviders = []
                                reeRefIds = {}
                                reeEntryIds = {}

                                for provider in ressProviderIds:
					compteur_entree=1
                                        reeProviderName = getObjectAttribute(provider, 'name')
					#print "Provider : %s" % reeProviderName

                                        reeRefIds = _splitlines(AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' +  serverName + '/ResourceEnvironmentProvider:' + reeProviderName + '/Referenceable:/'))
                                        reeEntryIds = _splitlines(AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' +  serverName + '/ResourceEnvironmentProvider:' + reeProviderName + '/ResourceEnvEntry:/'))

                                        listReferenceables = {}
                                        for referenceable in reeRefIds:
                                                nomFabrique = getObjectAttribute(referenceable, 'factoryClassname')
                                                nomClasse = getObjectAttribute(referenceable, 'classname')
                                                listReferenceables[nomFabrique] = nomClasse

                                        #for fabrique, classe in listReferenceables.items():
                                        #                print("\t\t%s, %s" % (fabrique, classe))

                                        if reeEntryIds != [] :

                                                listEntries = []
                                                for reeEntry in reeEntryIds:
							#print "ree%s" % str(compteur_entree)+".REE_TYPE_ACTION=update"
                                                        entryName = getObjectAttribute(reeEntry, 'name')
                                                        entryJndiWeb = getObjectAttribute(reeEntry, 'jndiName')

                                                        if dico != {}:
                                                                for k in dico.keys():
                                                                        if k == entryJndiWeb:
                                                                                reeJndiNameApp = dico[entryJndiWeb]
										print "ree%s" % str(compteur_entree)+".REE_ENTRY_JNDI_WEB=%s" % entryJndiWeb
										print "ree%s" % str(compteur_entree)+".REE_ENTRY_JNDI_APPLI=%s" % reeJndiNameApp

										#referenceableId = getObjectAttribute(reeEntry, 'referenceable')
										#referenceableName = getObjectAttribute(referenceableId, 'factoryClassname')
										#print "ree%s" % str(compteur_entree)+".REE_FACTORY_NAME=%s" % referenceableName
										#referenceableClass = getObjectAttribute(referenceableId, 'classname')
										#print "ree%s" % str(compteur_entree)+".REE_CLASS_NAME=%s" % referenceableClass

                                                                                #reepropertySetIds = getObjectAttribute(reeEntry, 'propertySet')
                                                                                #J2EEResourcePropertyIds = _splitlines(AdminConfig.list('J2EEResourceProperty',reepropertySetIds))
                                                                                #listProperties = {}
										#compteur_propriete=1
                                                                                #for property in J2EEResourcePropertyIds:
                                                                                        #J2EEResourcePropertyName = getObjectAttribute(property, 'name')
											#print "ree%s" % str(compteur_entree)+".REE_ENTRY_PROP_NAME%s" % str(compteur_propriete)+"=%s" % J2EEResourcePropertyName
                                                                                        #J2EEResourcePropertyValue = getObjectAttribute(property, 'value')
											#print "ree%s" % str(compteur_entree)+".REE_ENTRY_PROP_VALUE%s" % str(compteur_propriete)+"=%s" % J2EEResourcePropertyValue
                                                                                        #listProperties[J2EEResourcePropertyName] = J2EEResourcePropertyValue
											#compteur_propriete = compteur_propriete + 1
								print ""
							compteur_entree = compteur_entree + 1
                                        else:
                                                print "\t\tNo entry defined on this provider."
	else:
		print "Aucun provider de ressources d environnement n est defini pour cette application."

#------------------------------------------------------------------------------------------
# Liste des ressources URL pour un SA et recuperation de l id pour une ressource specifique
#------------------------------------------------------------------------------------------

def getUrlRessId(scope,jndiNameAppli,realNameAppli=None,module_appli=None,appli=None):
	urlJndiNameWeb,idRessUrl = None,None								
	
        urlsId = getObjectsOfType('URL',scope)								# Ressources URL existantes dans le SA

	if urlsId or urlsId != "":
		if appli: # Application installee
        		urlJndiNameWeb = retrieveJNDI(appli,jndiNameAppli,findAuth="Auth")	# URL mappee dans l application ?
			if urlJndiNameWeb:								# Oui, presente dans le bindings
				for url in urlsId:
					urlJndi = getObjectAttribute(url, 'jndiName')
					if urlJndiNameWeb == urlJndi:
						idRessUrl = url
		elif module_appli is None and realNameAppli:							# Application non installee 
			URLName = re.sub(r"^.*/",r"",jndiNameAppli)
			ressName = realNameAppli + "_" + URLName + "_url"
			URLJndiWeb = "url/" + realNameAppli + "_" + URLName
			for url in urlsId:
				urlJndi = getObjectAttribute(url, 'jndiName')
				if urlJndi == URLJndiWeb or urlJndi == jndiNameAppli:
					print ""
					print "WARNING : La ressource url %s existe mais actuellement non rattachee a l application car celle ci non installee." % urlJndi
					idRessUrl = url
	return urlJndiNameWeb,idRessUrl
	

#------------------------------------------------------------------------------------------------------------
# Liste des ressources JDBC pour un SA donne (version2) et recuperation de l id pour une ressource specifique
#------------------------------------------------------------------------------------------------------------

def getDbRessId(scope,jndiNameAppli,realNameAppli=None,module_appli=None,appli=None):
	dsJndiNameWeb,idRessDs = None,None

        idDatasources = getObjectsOfType('DataSource',scope)

	if idDatasources:
		if appli:
			dsJndiNameWeb = retrieveJNDI(appli,jndiNameAppli,findAuth="Auth")
			if dsJndiNameWeb is not None:
				for datasource in idDatasources:
					dsJndi = getObjectAttribute(datasource, 'jndiName')
					if dsJndiNameWeb == dsJndi:
						idRessDs = datasource
		elif module_appli is None and realNameAppli is not None:
			for datasource in idDatasources:
				dsJndi = getObjectAttribute(datasource, 'jndiName')

				dbcRessName = realNameAppli + "_ds_" + re.sub(r"^.*/",r"",jndiNameAppli)
				jdbcAliasAuth = realNameAppli + "_alias_" + re.sub(r"^.*/",r"",jndiNameAppli)
				JDBCJndiWeb = "jdbc/" + realNameAppli + "_" + re.sub(r"^.*/",r"",jndiNameAppli)

				if dsJndi == jndiNameAppli or dsJndi == JDBCJndiWeb:
					print ""
					print "WARNING : la ressource jdbc %s existe mais n est pour le moment pas rattachee a l application car celle ci n est pas installee." % dsJndi
					idRessDs = datasource
					dsJndiNameWeb = jndiNameAppli
	return dsJndiNameWeb,idRessDs

#----------------------------------------------------
# Liste des ressources ENV pour un SA donne (version2
#----------------------------------------------------

def getReeRessId(scope,jndiNameAppli,realNameAppli=None,module_appli=None,appli=None):
	reeJndiNameWeb,idRessReeEntry = None, None

	idReeEntries = getObjectsOfType('ResourceEnvEntry',scope)

	if idReeEntries or idReeEntries != "":
		if appli:
			reeJndiNameWeb = retrieveJNDI_env(appli,jndiNameAppli,findAuth="Auth")
			# Binding exists
			if reeJndiNameWeb:
				for reeEntry in idReeEntries:
					reeJndi = getObjectAttribute(reeEntry, 'jndiName')
					if reeJndi == reeJndiNameWeb:
						idRessReeEntry = reeEntry
		elif module_appli is None and realNameAppli:
			reeRessName = realNameAppli + "_" + re.sub(r"^.*/",r"",jndiNameAppli) + "_ENV"
			#reeJndiWeb = "env/" + realNameAppli + "_" + re.sub(r"^.*/",r"",jndiNameAppli) + "_ENV"
			reeJndiNameWeb = "env/" + realNameAppli + "_" + re.sub(r"^.*/",r"",jndiNameAppli) + "_ENV"
			for reeEntry in idReeEntries:
				reeJndi = getObjectAttribute(reeEntry, 'jndiName')
				#if (reeJndi == reeJndiWeb or reeJndi == jndiNameAppli) :
				#	idRessReeEntry = reeEntry
				if (reeJndi == reeJndiNameWeb or reeJndi == jndiNameAppli):
					print ""
					print "WARNING : la ressource d environnement %s existe mais n est pour le moment pas rattachee a l application car celle ci n est pas installee." % reeJndi
					idRessReeEntry = reeEntry
	return reeJndiNameWeb,idRessReeEntry

#---------------
# Actions : view
#---------------

def viewAction(typeRess,idRess):
	if typeRess == "url":
		print "Nom JNDI dans WebSphere : %s" % getObjectAttribute(idRess,'jndiName')
		print "Valeur : %s" % getObjectAttribute(idRess,'spec')

	if typeRess == "ds":
		viewDbRessProperties(idRess)

	if typeRess == "ree":
		viewReeProperties(idRess)	

#-----------------
# Actions : update
#-----------------

def updateUrlAction(idRess, nomRess, t_Ress):
        for key,value in t_Ress.items():
                if nomRess == key:
			print "Nouvelle valeur : %s" % t_Ress[key]['URL_SPEC']
                        AdminConfig.modify(idRess, [['spec', t_Ress[key]['URL_SPEC']]])

def updateDsAction(idRess, nomRess, t_Ress):
	global flagErreur
        for key,value in t_Ress.items():
                if nomRess == key:
			if t_Ress[nomRess]['JDBC_URL'] != "":
				changeURLDatasource(idRess,t_Ress[nomRess]['JDBC_URL'])
				flagErreur = 0
				changeAlias(idRess,t_Ress[nomRess]['JDBC_ALIAS_USER'],t_Ress[nomRess]['JDBC_ALIAS_PASS'])
			else:
				print("ERREUR(8) : La valeur de l instance de la ressource DS n a pas ete specifiee\n")
				flagErreur = 1

def updateReeAction(idRess,jndiAppli,nomRess,allProperties,node,sa):
        changeREEpropriety(idRess,jndiAppli,nomRess,allProperties,node,sa)

#-----------------
# Actions : create
#-----------------

#-----------------------
# Creation ressource URL
#-----------------------

def createUrl(node,sa,urlJndi,nomRess,t_Ress,appli):
	global flagErreur
        URLProviderName = "Default URL Provider"
        URLStreamHandlerClass = "unused"
        URLProtocol = "unused"
        URLName = re.sub(r"^.*/",r"",urlJndi)
        ressName = appli + "_" + URLName + "_url"
        URLJndiWeb = "url/" + appli + "_" + URLName
        try: 
                idRessUrlcreated = AdminResources.createURL(node,sa,URLProviderName,ressName,URLJndiWeb,t_Ress[nomRess]['URL_SPEC'])
                print "Ressource URL creee (ID = %s)" % idRessUrlcreated
		flagErreur = 0
        except:
		if t_Ress[nomRess]['URL_SPEC'] == "":
			print("ERREUR(8) : La valeur de la ressource URL n a pas ete specifiee\n")
			flagErreur = 1
                elif getCfgItemId("server",node,sa,"URLProvider:/URL", "%s" % ressName) != None:
                        print "WARNING : Cette ressource URL existe deja. Elle a ete mise a jour."
                        print "Nom JNDI : %s" % AdminConfig.showAttribute(getCfgItemId("server",node,sa,"URLProvider:/URL", "%s" % ressName),'jndiName')
                        print "Ancienne valeur : %s" % AdminConfig.showAttribute(getCfgItemId("server",node,sa,"URLProvider:/URL", "%s" % ressName),'spec')
			idRess = getCfgItemId("server",node,sa,"URLProvider:/URL", "%s" % ressName)
			updateUrlAction(idRess, nomRess, t_Ress)
                else:
                        print "ERREUR(10) : la ressource URL n a pas pu etre creee.No Save"
                        print ""
			flagErreur = 1

#------------------------
# Creation ressource JDBC
#------------------------

def createDs(node,sa,jdbcJndi,nomRess,t_Ress,appli):
	global flagErreur
	userOracle = t_Ress[nomRess]['JDBC_ALIAS_USER']
	passOracle = t_Ress[nomRess]['JDBC_ALIAS_PASS']
	urlOracle = t_Ress[nomRess]['JDBC_URL']

	# formatage du nom de la ressource jdbc
	jdbcRessName = appli + "_ds_" + re.sub(r"^.*/",r"",jdbcJndi)

	# formatage du nom de l alias
	jdbcAliasAuth = appli + "_alias_" + re.sub(r"^.*/",r"",jdbcJndi)

	# formatage nom JNDI JDBC sous Websphere
	jndiWebName = "jdbc/" + appli + "_" + re.sub(r"^.*/",r"",jdbcJndi)

	# initialisation variables testant l existence ou non d un provider,d un alias, ou d une datasource
	existence_provider = 0
	existence_alias = 0

	# chemin vers le fichier du driver
	classpath = "${ORACLE_JDBC_DRIVER_PATH}/ojdbc6.jar"
	#classpath = "${ORACLE_JDBC_DRIVER_PATH}/ojdbc14.jar"
	
	# Verification de l existence du provider pour l application mentionnee
	jdbcProviderName = "Oracle JDBC Driver"		
	jdbcProviderType = "Oracle JDBC Driver"
	listProviders = _splitlines(getCfgItemId("server",node,sa,"JDBCProvider:"))
	if listProviders != "None":
		print "Providers actuels :"
		for provider in listProviders:
			name_provider = AdminConfig.showAttribute(provider, 'name')
			type = AdminConfig.showAttribute(provider, 'providerType')
			print name_provider
			if name_provider == jdbcProviderName and (type == jdbcProviderType or type == None):
				print "Le provider \"%s\" existe deja." % jdbcProviderName
				print ""
				existence_provider = 1
	else:
		print "Aucun provider n est reference pour cette application."

	if existence_provider == 0:
		# creation du provider jdbc

		description = "Oracle JDBC Driver"							# Description du fournisseur
		jdbcProviderType = "Oracle JDBC Driver"
		label = "Oracle JDBC Driver"								# Nom du fournisseur
		implClassName = "oracle.jdbc.pool.OracleConnectionPoolDataSource"			# Type de connexion
		otherAttrsList = [["classpath", classpath], ["description", description], ["providerType", jdbcProviderType]]
		print ""
		print "Node :",node
		print "SA :",sa
		print "JDBC name :",jdbcRessName
		print "JNDI dans WAS:",jndiWebName
		print "URL datasource :",urlOracle
		print "Alias du compte :",jdbcAliasAuth
		idJdbcProviderCreated = AdminJDBC.createJDBCProvider(node, sa, label, implClassName, otherAttrsList)
		print "idJdbcProviderCreated : ",idJdbcProviderCreated
		print ""

	# Creation de l alias de connexion à affecter à la datasource
	authList = AdminConfig.list('JAASAuthData').split("\n")
	for authAlias in authList:
		name_alias = AdminConfig.showAttribute(authAlias, 'alias')
		if name_alias == jdbcAliasAuth:
			print "WARNING : L alias \"%s\" existe deja." % jdbcAliasAuth
			print ""
			existence_alias = 1
	
	if existence_alias == 0:
		# Creation de l alias de connexion à affecter à la datasource
		print "Alias :",jdbcAliasAuth
		print "Login :",userOracle
		print "Mot de passe :",passOracle
		descriptionAlias = "%s" % jdbcAliasAuth
		try :
			idAliasCreated = AdminResources.createJAASAuthenticationAlias(jdbcAliasAuth,userOracle,passOracle,descriptionAlias)
			print ""
			print("L alias de connexion a la datasource a ete cree (ID alias : %s).") % idAliasCreated
			print ""
		except :
			if userOracle == "":
				print "WARNING : le nom du schema n a pas ete fourni."
			if passOracle == "":
				print "WARNING : le mot de passe du schema n a pas ete fourni."

	# Creation de la datasource	
	properties = [[["name", "URL"], ["type", "java.lang.String"], ["value", urlOracle]]]
	mappingConfigAlias = "DefaultPrincipalMapping"
	otherAttrsList = [['mapping',[['authDataAlias',jdbcAliasAuth],['mappingConfigAlias',mappingConfigAlias]]],['description', jdbcRessName], ['jndiName', jndiWebName], ['authDataAlias',jdbcAliasAuth],['datasourceHelperClassname', "com.ibm.websphere.rsadapter.Oracle11gDataStoreHelper"], ['providerType', jdbcProviderType],['propertySet', [["resourceProperties", properties]]]]
	try :
		idRessJdbcCreated = AdminJDBC.createDataSource(node, sa, jdbcProviderName, jdbcRessName, otherAttrsList)
		print "Ressource JDBC creee (ID = %s)" % idRessJdbcCreated
	except:
		if urlOracle == "":
			print "ERROR : la valeur de l instance de la ressource n est pas specifiee !"
			flagErreur = 1
		if getCfgItemId("server",node,sa,"JDBCProvider:/DataSource", "%s" % jdbcRessName) != None:
			idRess = getCfgItemId("server",node,sa,"JDBCProvider:/DataSource", "%s" % jdbcRessName)
			print "WARNING : Cette ressource JDBC existe deja."
			print "Ancienne valeur : %s"  % getUrlByDs(idRess)
			changeURLDatasource(idRess,urlOracle)
			print ""


#-------------------------------------------------------------------
# Creation uniquement d un fournisseur d environnement de ressources
#-------------------------------------------------------------------

def createReeProvider(node,sa,corps_appli):
        defaultResourceEnvProviderName = corps_appli + "_ENV"

        providerAlreadyExists = "False"

        listProviders = _splitlines(AdminConfig.list('ResourceEnvironmentProvider'))
        for provider in listProviders:
                name = AdminConfig.showAttribute(provider,'name')
                if name == defaultResourceEnvProviderName:
                        print "Le provider existe deja."
                        #providerMustToBeCreated = "True"
			providerAlreadyExists = "True"

        if providerAlreadyExists == "False":
                print "Creation du fournisseur de ressources : "
                idReeProviderCreated = AdminResources.createResourceEnvProvider(node,sa,defaultResourceEnvProviderName)
                print "idReeProviderCreated : ",idReeProviderCreated
                print "Un nouveau fournisseur de ressources a été crée : %s" % defaultResourceEnvProviderName
                print ""

#--------------------------------------------------------------
# Creation d un fournisseur d environnement + fabrique + classe
#--------------------------------------------------------------

def createReeProviderRef(node,sa,defaultResourceEnvProviderName,factoryClass,className):
	print "Creation pour le fournisseur en question d une fabrique de classes : "
	idReeProviderReferenceablesCreated = AdminResources.createResourceEnvProviderRef(node,sa,defaultResourceEnvProviderName,factoryClass,className)
	print "idReeProviderReferenceablesCreated : ",idReeProviderReferenceablesCreated
	print ""
	return idReeProviderReferenceablesCreated

#-----------------------------------------
# Creation d une ressource d environnement 	
#-----------------------------------------

def createRee(node,sa,factoryClass,className,entryJndiName,cle,allProperties,appli):
	global flagErreur
	#print("allProperties : %s" % allProperties)
	i = 0
	props = []

	for key, val in allProperties.items():
		p = props.append(val)

	nbProps = len(props)

	idServer = getServerId(node,sa)

	# Formatage du nom du fournisseur
	corps_appli = re.sub(r"(SA_)?(sa-)?(_app)?(_pres)?",r"",sa)
	defaultResourceEnvProviderName = corps_appli + "_ENV"
	#print("defaultResourceEnvProviderName : %s" % defaultResourceEnvProviderName)

        # Normally, as a first creation, any provider should not exist for application, but in case
        listResourceEnvProviders = getObjectsOfType("ResourceEnvironmentProvider",idServer)
        nbResourceEnvProviders = int(len(listResourceEnvProviders))

        # Creation du fournisseur d environnement 
	if nbResourceEnvProviders == 0:	
		createReeProvider(node,sa,corps_appli)

	# Creation de la fabrique et de la classe de fabriques
	# List all factories, check if already exists
	factoryToCreate = "yes"
	factoriesId = getObjectsOfType('Referenceable','%s' % idServer)
	#print("factoriesId : %s" % factoriesId)
	if factoriesId:
		for factory in factoriesId:
			classname = AdminConfig.showAttribute(factory, 'classname')
			factoryClassname = AdminConfig.showAttribute(factory, 'factoryClassname')
			#print("classname : %s, factoryClassname : %s" % (classname,factoryClassname))
			if((classname == className) and (factoryClassname == factoryClass)):
				rf = factory
				factoryToCreate = "no" 
	if factoryToCreate == "yes":		
        	rf = createReeProviderRef(node,sa,defaultResourceEnvProviderName,factoryClass,className)

	# Formatage du nom de la ressource d environnement
	resourceEnvEntryName = re.sub(r"^.*/",r"",entryJndiName)
	#EntryName = "env_" + corps_appli + "_" + resourceEnvEntryName + "_ENV"
	EntryName = corps_appli + "_" + resourceEnvEntryName + "_ENV"

	# Formatage du nom JNDI de l entree
	EntryJndi = "env/" + appli + "_" + resourceEnvEntryName + "_ENV"

	# Creation de l entree
	try :
		#attrEntry = [['name',EntryName],['jndiName',entryJndiName],['referenceable','%s' % rf]]
		attrEntry = [['name',EntryName],['jndiName',EntryJndi],['referenceable','%s' % rf]]
		#idReeEntry = AdminResources.createResourceEnvEntriesAtScope("/Node:%s/Server:%s/" % (node,sa),defaultResourceEnvProviderName,EntryName,entryJndiName,attrEntry)
		idReeEntry = AdminResources.createResourceEnvEntriesAtScope("/Node:%s/Server:%s/" % (node,sa),defaultResourceEnvProviderName,EntryName,EntryJndi,attrEntry)
		print "L entree suivante a ete creee pour cette ressource d environnement : %s" % EntryName
		#idReeEntry = AdminResources.createResourceEnvEntries(node,sa,defaultResourceEnvProviderName,EntryName,entryJndiName)
		#idReeEntry = AdminConfig.create('ResourceEnvEntry',defaultResourceEnvProviderName,attrEntry)
		#print "idReeEntry : ",idReeEntry

		#print ""
		print "Initialisation des valeurs de l entree en question : "

		ResourceReeEntriesIds = getObjectsOfType('ResourceEnvEntry', idServer)
		for ResourceReeEntryId in ResourceReeEntriesIds:
			ResourceReeEntryName = getObjectAttribute(ResourceReeEntryId, 'name')
			if ResourceReeEntryName == EntryName:
				ResourceReeEntryJndiName = getObjectAttribute(ResourceReeEntryId,'jndiName')
				ResourceReeEntryPropertySetId = getObjectAttribute(ResourceReeEntryId, 'propertySet')

				# Creation du Set de proprietes
				if ResourceReeEntryPropertySetId == None:
					ResourceReeEntryPropertySetId = AdminConfig.create('J2EEResourcePropertySet',ResourceReeEntryId,[])
					#print ""
					#print "ResourceReeEntryPropertySetId : %s" % ResourceReeEntryPropertySetId
					#print ""

				# Recuperation et creation des valeurs renseignees pour la ressource d environnement
				while i < nbProps:
					propName = props[i][0]
					propValue = props[i][1]
					print("Couple de valeurs : %s - %s" % (propName,propValue))

					name = ['name',propName]
					value = ['value',propValue]
					rpAttrs = [name,value]

					idReePropertyCreated = AdminConfig.create('J2EEResourceProperty', ResourceReeEntryPropertySetId, rpAttrs)
					#print("idReePropertyCreated = %s" % idReePropertyCreated)
					i += 1
	except:
		if getCfgItemId("server",node,sa,"ResourceEnvironmentProvider:/ResourceEnvEntry") != None:
			print "WARNING : L entree existe deja. Une mise a jour a ete apportee au niveau de ses proprietes."
			idEntry = getCfgItemId("server",node,sa,"ResourceEnvironmentProvider:/ResourceEnvEntry")
			jndiEntry = AdminConfig.showAttribute(idEntry, 'jndiName')
			#print "jndiEntry : %s" % jndiEntry
			nameEntry = AdminConfig.showAttribute(idEntry, 'name')
			PropertySetEntryId = getObjectAttribute(idEntry, 'propertySet')
			#print "PropertySetEntryId : %s" % PropertySetEntryId
			resourcePropertySetEntryIds = _splitlines(AdminConfig.list('J2EEResourceProperty',PropertySetEntryId))
			print "Anciennes valeurs de l entree : "
			for resourceProperty in resourcePropertySetEntryIds:
				entryPropertyName = AdminConfig.showAttribute(resourceProperty,'name')
				entryPropertyValue = AdminConfig.showAttribute(resourceProperty,'value')
				print "Nom : ",entryPropertyName,", Valeur : ",entryPropertyValue
			updateReeAction(idEntry,jndiEntry,nameEntry,allProperties,node,sa)
			print "Nouvelles valeurs de l entree : "
			for resourceProperty in resourcePropertySetEntryIds:
				entryPropertyName = AdminConfig.showAttribute(resourceProperty,'name')
				entryPropertyValue = AdminConfig.showAttribute(resourceProperty,'value')
				print "Nom : ",entryPropertyName,", Valeur : ",entryPropertyValue

#-----------------
# Actions : delete
#-----------------

def deleteAction(typeRess,idRess):
	if typeRess == "url":
		print "Suppression ressource %s : %s" % (typeRess,idRess)
		AdminConfig.remove(idRess)
	elif typeRess == "ds":
		print "Suppression ressource %s : %s" % (typeRess,idRess)
		AdminConfig.remove(idRess)
	elif typeRess == "ree":
		print "Suppression ressource %s : %s" % (typeRess,idRess)
		AdminConfig.remove(idRess)
