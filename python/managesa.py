# -*- coding: utf-8 -*

import os

execfile('%s' % os.environ["PYTHON_LIBRARY"])		# Libraires Python ("MyFunction.py"...)

propsFile = sys.argv[0]

# Fonction creation SA
# On determine le port pour le SA
def findMaxPort(serverEntries,myServerName):
	global AdminConfig
  	mxPort=0
  	print "Find starting port for new SA %s" % myServerName
  	for serverEntry in serverEntries:
    		sName=AdminConfig.showAttribute(serverEntry,'serverName')
    		sType=AdminConfig.showAttribute(serverEntry ,'serverType')
    		if sType != "WEB_SERVER" and sName != myServerName: 
      			specialEndPoints=_splitlist(AdminConfig.showAttribute(serverEntry, 'specialEndpoints'))[0]
      			if specialEndPoints != "" and specialEndPoints != None: 
        			specialEndPoint=[specialEndPoints][0]
        			endPointNm=AdminConfig.showAttribute(specialEndPoint,'endPointName') 
        			ePoint=AdminConfig.showAttribute(specialEndPoint,'endPoint')
        			port=AdminConfig.showAttribute(ePoint,'port')
				#print("SA : %s, BOOTSTRAP_ADDRESS port : %s" % (sName, port))
        			if mxPort < port :
        				mxPort=port
  	return mxPort


def checkPort(sName, serverEntry, startingPort):
	global AdminConfig
	specialEndPoints=[_splitlist(AdminConfig.showAttribute(serverEntry, 'specialEndpoints'))[0]]
	for specialEndPoint in specialEndPoints :
		endPointNm = AdminConfig.showAttribute(specialEndPoint,'endPointName')
		ePoint=AdminConfig.showAttribute(specialEndPoint,'endPoint')
		port=AdminConfig.showAttribute(ePoint,'port')
		#print("SA : %s, BOOTSTRAP_ADDRESS port : %s, port : %s" % (sName, endPointNm, port))
		if startingPort == port or eval('startingPort + 10') == port:
			print "ERROR: port range %s already in use by server %s by %s : %s" % (AdminConfig.showAttribute(serverEntry,'serverName'),startingPort, endPointNm, port)
			sys.exit(1)


def setPort(serverEntry, prm_startingPort, prm_listPortToDelete): 
	global AdminConfig
	print ""
	specialEndPoints=_splitlines(_splitlist(AdminConfig.showAttribute(serverEntry, 'specialEndpoints')))[0]
	prm_listPortToDelete = "[" + prm_listPortToDelete + "]"
	listPortToDelete = _splitlist(prm_listPortToDelete)
	#Configure les ports
	for specialEndPoint in specialEndPoints:
		endPointNm=AdminConfig.showAttribute(specialEndPoint,'endPointName')
		ePoint=AdminConfig.showAttribute(specialEndPoint,'endPoint')
		myhost=AdminConfig.showAttribute(ePoint,'host')
		if endPointNm in listPortToDelete:
			print("Remove EndPoint : %s (%s)" % (endPointNm, specialEndPoint))
			AdminConfig.remove(specialEndPoint)


def setServerPorts(serverId,serverEntries):
	global prm_listPortToModify, prm_listPortToDelete, prm_startingPort, prm_checkPortConflict
  	global prm_listTransportChainToDelete, prm_portRangeWide

	myServerName=AdminConfig.showAttribute(serverId,'name')
	print "myServerName : %s" % myServerName
	startingPort=prm_startingPort
	print("Port parameter setting : %s" % startingPort)
	if startingPort == "AUTO":
    		mPort=findMaxPort(serverEntries,myServerName)
		print "Maximum port found : %s" % mPort
		print "Port range : %s" % prm_portRangeWide
    		startingPort = int(mPort) + int(prm_portRangeWide)
		print "New port starting at : %s" % startingPort

  	#print "prm_checkPortConflict=%s" % prm_checkPortConflict
  	if prm_checkPortConflict  == "true" :
    		print "Verifying possible port conflict..."
    		for serverEntry in serverEntries :
          		sName=AdminConfig.showAttribute(serverEntry,'serverName')
			#print("sName : %s" % sName)
          		if sName != myServerName :
                		#Configure les ports
                		#print "Checking ports..."
 	               		checkPort(sName,serverEntry,startingPort)

	#Parcours les serveurs pour trouver notre serveur
	print "Setting TCP ports..."
	for serverEntry in serverEntries:
		sName = AdminConfig.showAttribute(serverEntry,'serverName')
		if sName == myServerName:
			#Configure les ports
			print("===> Setting ports (deleting some useless ports : %s) ..." % prm_listPortToDelete)
			setPort(serverEntry, prm_startingPort, prm_listPortToDelete)

	if prm_listTransportChainToDelete != "":
		print ""
		print("Removing transport chain %s..." % prm_listTransportChainToDelete)
		prm_listTransportChainToDelete = "[" + prm_listTransportChainToDelete + "]"
		listTransportChainToDelete = _splitlist(prm_listTransportChainToDelete)
		tpservs = AdminConfig.list('Chain',serverId).split('\n')
		for tpserv in tpservs:
			tpservName = AdminConfig.showAttribute(tpserv, 'name')
			if tpservName in listTransportChainToDelete:
				print("Remove %s (%s)" % (tpservName, tpserv))
				AdminConfig.remove(tpserv)

def setLogs(prm_nodeName, prm_serverName, prm_serverLogRoot): 
	global AdminConfig
	global prm_logType
	print "Valeur de logType : %s" % prm_logType

	varmap=AdminConfig.getid('/Node:%s/Server:%s/VariableMap:/' % (prm_nodeName, prm_serverName))
	vslist=_splitlist(AdminConfig.showAttribute(varmap, 'entries'))
	for vs in vslist: 
		sName=AdminConfig.showAttribute(vs, 'symbolicName')
		if sName == "SERVER_LOG_ROOT" : 
				print "replacing %s by %s" % (sName, prm_serverLogRoot)
				AdminConfig.modify(vs,[['value', prm_serverLogRoot]])

def setJVM1(serverId,prm_initialHeapSize,prm_maximumHeapSize,prm_jvmprop,prm_classPath,prm_genericJvmArguments):
	global AdminConfig
	jvm = AdminConfig.list('JavaVirtualMachine', serverId)
	# taille memoire JVM
	AdminConfig.modify(jvm,[['initialHeapSize', prm_initialHeapSize],['maximumHeapSize', prm_maximumHeapSize]])
	print "Setting memory heap size to : %s/%s Mo (Initial / Max)" % (prm_initialHeapSize,prm_maximumHeapSize)

	# arguments generiques JVM
	if prm_genericJvmArguments == "": 
		AdminConfig.modify(jvm,[['genericJvmArguments', '']])
	else:
		AdminConfig.modify(jvm,[['genericJvmArguments', prm_genericJvmArguments]])
		print "Setting generic arguments to : %s" % prm_genericJvmArguments

	# classpath
	if prm_jvmClasspath == "": 
		AdminConfig.modify(jvm,[['classpath', ""]])
	else:
		AdminConfig.modify(jvm,[['classpath', prm_jvmClasspath]])
		print "Setting classpath to : %s" % prm_jvmClasspath

def setORB(serverId,prm_orbReqTO,prm_orbLocReqTO,was_version): 
	global AdminConfig
	orb = AdminConfig.list('ObjectRequestBroker', serverId)
	AdminConfig.modify(orb, [['requestTimeout', prm_orbReqTO], ['locateRequestTimeout', prm_orbLocReqTO]])
	print "- Request timeout to : %s" % prm_orbReqTO
	print "- Locate request timeout to : %s" % prm_orbLocReqTO
	if was_version != "6.0": 
		AdminConfig.modify(orb, [['useServerThreadPool', 'true']])

#JVM properties creation
#def setSystemProperty(serverId, prm_nodeTempDir):
def setSystemProperty(serverId):
	global AdminConfig
	jvm = AdminConfig.list('JavaVirtualMachine',serverId)
	print "Proprietes pour la JVM : %s" % prm_jvmprop
	#AdminConfig.create('Property', jvm, [])
	#AdminConfig.create('Property', jvm, prm_jvmprop)
	#AdminConfig.modify('systemProperties', jvm, [['name',"com.ibm.websphere.servlet.temp.dir"],['value', prm_nodeTempDir],['required','false']])
	#AdminConfig.modify('systemProperties', jvm, [['name',"com.ibm.websphere.servlet.temp.dir"],['value', prm_nodeTempDir],['name',"client.encoding.override"],['value',"UTF-8"]])
	#AdminConfig.modify('systemProperties', jvm, [])
	#AdminConfig.modify('systemProperties', jvm, prm_jvmprop)
	AdminConfig.modify(jvm, [['systemProperties', ""]])
	AdminConfig.modify(jvm, [['systemProperties', prm_jvmprop]])

def setBckup(serverId, prm_nbBackupLog, rolloverSize):
	global AdminConfig
	global prm_logType
	if prm_logType == "B":
		outputStream = AdminConfig.showAttribute(serverId, 'outputStreamRedirect')
		AdminConfig.modify(outputStream, [['maxNumberOfBackupFiles', prm_nbBackupLog],['rolloverSize', rolloverSize]])
		errorStream = AdminConfig.showAttribute(serverId, 'errorStreamRedirect')
		AdminConfig.modify(errorStream, [['maxNumberOfBackupFiles', prm_nbBackupLog],['rolloverSize',rolloverSize]])

#Web Container properties creation
def setWebContainerProps(serverId, prm_wcprop):
	global AdminConfig
	print "Proprietes pour le Web Container : %s" % prm_wcprop
	wc = AdminConfig.list('WebContainer', serverId)
	AdminConfig.modify(wc, [['properties', ""]]) 
	AdminConfig.modify(wc, [['properties', prm_wcprop]])
	#AdminConfig.create('Property', wc, prm_wcprop)

# JVM processes definiton creation
def setEnv(serverId, prm_processEnv):
	global AdminConfig
	processDef = AdminConfig.list('ProcessDef', serverId)
	AdminConfig.modify(processDef, [['environment',""]])
	AdminConfig.modify(processDef, [['environment', prm_processEnv]])


# JVM processes execution creation
def setProcessExecution( serverId ):
	global AdminConfig
	global prm_processPriority,prm_umask
	processDef = AdminConfig.list('ProcessDef', serverId)
	processExec = AdminConfig.showAttribute(processDef, 'execution')
	AdminConfig.modify(processExec, [['processPriority',prm_processPriority],['umask',prm_umask]])


def setThreadPoolProperties(tp,inactivityTimeout,isGrowable,maximumSize,minimumSize):
	global AdminConfig
	AdminConfig.modify(tp, [['inactivityTimeout',inactivityTimeout],['isGrowable',isGrowable],['maximumSize',maximumSize],['minimumSize',minimumSize]])


def setJVMCustomProperty(serverId, propName, propValue):
	global AdminConfig
	serverName = AdminConfig.showAttribute(serverId, 'name')
	attrs = [['name',propName],['value',propValue]]
	findProp = "false"
	jvm = AdminConfig.list('JavaVirtualMachine', serverId)
	for propid in _splitlines(AdminConfig.list('Property', jvm)):
		tmpName = AdminConfig.showAttribute(propid, 'name')
		if tmpName == propName:
			findProp = "true"
			tmpValue = AdminConfig.showAttribute(propid, 'value')
			if tmpValue == propValue:
				print "Property \"%s\" already set to \"%s\" for server %s" % (propName,propValue,AdminConfig.showAttribute(serverId,'name'))
			else:
				print "Setting property \"%s\" to \"%s\" for server %s" % (propName,propValue,AdminConfig.showAttribute(serverId,'name'))
				AdminConfig.modify(propid, attrs)
	#  la propriete n'est pas definie -> on l'ajoute
	if findProp == "false":
		print "Adding property \"%s\" set to \"%s\" for server %s" % (propName,propValue,AdminConfig.showAttribute(serverId,'name'))
		AdminConfig.create('Property', jvm, attrs)


def setAttachAPI(serverId, flag):
	global AdminConfig
	propName = "com.ibm.tools.attach.enable"
	if flag ==  "true":
		propValue = "yes"
	else:
		propValue = "no"
	setJVMCustomProperty(serverId, propName, propValue)


def configJVMClassLoader(serverId, jvmClassLoader, jvmClassLoaderMode, jvmClassLoaderSharedLibrary):
	global AdminConfig
	for cl in AdminConfig.list('Classloader',serverId):
		AdminConfig.remove(cl)
	appServerId = AdminConfig.list('ApplicationServer', serverId)
	clId = AdminConfig.create('Classloader', appServerId,[['mode',jvmClassLoaderMode]])
	for lib in prm_jvmClassLoaderSharedLibrary:
		AdminConfig.create('LibraryRef', clId, [['libraryName',lib],['sharedClassloader','true']])


def setServerConfig( serverId ):
	global AdminConfig
	global prm_initialHeapSize,prm_maximumHeapSize,prm_jvmprop,prm_classpath,prm_genericJvmArguments
	global prm_orbReqTO,prm_orbLocReqTO
	global prm_nbBackupLog,prm_rolloverSize
	global prm_wcprop,prm_processEnv,prm_gcPolicy
	global prm_processPriority,prm_umask,prm_workingDirectory
	global prm_tporbInactivityTimeout,prm_tporbIsGrowable,prm_tporbMaximumSize,prm_tporbMinimumSize
	global prm_tpwebInactivityTimeout,prm_tpwebIsGrowable,prm_tpwebMaximumSize,prm_tpwebMinimumSize
	global prm_WAS_VERSION,prm_nodeTempDir,prm_pluginConnectTimeout
	global prm_clientInactivityTimeout,prm_totalTranLifetimeTimeout,prm_transactionLogDirectory,prm_enableHAManagerService,prm_enableJavaAttachAPI
	global prm_sessionPersistenceMode,prm_sessionPersistenceDataSource,prm_sessionPersistenceUser,prm_sessionPersistencePassword
	global prm_jvmClassLoader,prm_jvmClassLoaderMode,prm_jvmClassLoaderSharedLibrary
	
	#checkJVMGenericArguments( prm_genericJvmArguments )
	
	print "Setting JVM parameters..."
	setJVM1(serverId,prm_initialHeapSize,prm_maximumHeapSize,prm_jvmprop,prm_classpath,prm_genericJvmArguments)

	print "Setting ORB properties"
	setORB(serverId,prm_orbReqTO,prm_orbLocReqTO,prm_WAS_VERSION)

	# Change WAS temporary directory
	#if prm_nodeTempDir != "DEFAULT":
		#print "Setting WAS temporary directory..."
		#setSystemProperty(serverId,prm_nodeTempDir)
	print "Setting JVM properties..."
	setSystemProperty(serverId)

	print "Setting nb backup logs..."
	setBckup(serverId,prm_nbBackupLog,prm_rolloverSize)

	if prm_wcprop != "":
		print "Setting webContainer properties : "
		setWebContainerProps(serverId,prm_wcprop)

	print "Setting web server plugin properties..."
	webPlugin = AdminConfig.list('WebserverPluginSettings',serverId)
	AdminConfig.modify(webPlugin,[['ConnectTimeout',prm_pluginConnectTimeout]])
	
	if prm_processEnv != "":
		print "Setting process Environement : %s" % prm_processEnv
		setEnv(serverId,prm_processEnv)
	print "Setting process Execution properties"
	setProcessExecution(serverId)

	for tp in _splitlines(AdminConfig.list('ThreadPool',serverId)):
		name = AdminConfig.showAttribute(tp, 'name')
		if name == "ORB.thread.pool":
			#print "Setting %s properties" % name 
			setThreadPoolProperties(tp,prm_tporbInactivityTimeout,prm_tporbIsGrowable,prm_tporbMaximumSize,prm_tporbMinimumSize)
		if name == "WebContainer" :
			print "Setting WebContainer thread pool properties"
			setThreadPoolProperties(tp,prm_tpwebInactivityTimeout,prm_tpwebIsGrowable,prm_tpwebMaximumSize,prm_tpwebMinimumSize)

	print "Setting transaction service properties : inactivity timeout = %s, transaction timeout = %s" % (prm_clientInactivityTimeout,prm_totalTranLifetimeTimeout)
	tranId = AdminConfig.list('TransactionService',serverId)
	tranattrs = [['clientInactivityTimeout',prm_clientInactivityTimeout],['totalTranLifetimeTimeout',prm_totalTranLifetimeTimeout]]
	if prm_transactionLogDirectory != "DEFAULT":
		print "Setting tranlog directory : %s" % prm_transactionLogDirectory
		tranattrs.append(['transactionLogDirectory',prm_transactionLogDirectory])
	AdminConfig.modify(tranId,tranattrs)

	if prm_enableHAManagerService == "false":
		print "Disabling HAManager Service"
	else:
		print "Enabling HAManager Service"
	hmgrId = AdminConfig.list('HAManagerService',serverId)
	AdminConfig.modify(hmgrId,[['enable',prm_enableHAManagerService]])

	if prm_WAS_VERSION >= 70:
		setAttachAPI(serverId,prm_enableJavaAttachAPI)

	#if prm_WAS_VERSION >= 61:
		#enableCustomPMI( serverId )
    		#instrument( serverId )
    		#applySharedClassesSettings( serverId )
    		#setGcPolicy(serverId, prm_gcPolicy)
    		#removeRMIConnector( serverId )

	# positionne le repertoire de travail
	processDef = AdminConfig.list('ProcessDef', serverId)
	print "Setting working directory to '%s'" % prm_workingDirectory
	AdminConfig.modify(processDef, [['workingDirectory',prm_workingDirectory]])

	# session persistence
#	sm = AdminConfig.list('SessionManager', serverId)
#	if prm_sessionPersistenceMode == "N":
#		print "Disabling session persistence"
#		AdminConfig.modify(sm, [['sessionPersistenceMode',"NONE"]])
#	elif prm_sessionPersistenceMode == "DB":
#		print "Enable session persistence to Database"
#		AdminConfig.modify(sm, [['sessionPersistenceMode','DATABASE']])
#		sesdb = AdminConfig.list('SessionDatabasePersistence', sm)
#		AdminConfig.modify(sesdb,[['userId', prm_sessionPersistenceUser],['password', prm_sessionPersistencePassword],['tableSpaceName', ""],['datasourceJNDIName', prm_sessionPersistenceDataSource]])
#
#	if prm_WAS_VERSION >= 61:
#		configJVMClassLoader(serverId, prm_jvmClassLoader, prm_jvmClassLoaderMode, prm_jvmClassLoaderSharedLibrary)


def configExistingServer(nodeName, serverName, serverLogRoot) :
	global AdminConfig, prm_WAS_VERSION, prm_webBindingAddress
  	serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (nodeName, serverName))
  	setServerConfig(serverId)

  	if serverLogRoot != "DEFAULT" :
     		print "Setting logs root..."
     		setLogs(nodeName, serverName, serverLogRoot)

  	if prm_WAS_VERSION >= 61 :
    		global AdminTask
    		print "Setting WC_defaulthost host to %s..." % prm_webBindingAddress
		AdminTask.modifyServerPort(serverName,['-nodeName', nodeName, '-endPointName', 'WC_defaulthost', '-host', prm_webBindingAddress, '-modifyShared', 'true'])

def createVirtualHost(prm_SA_NAME):
	global AdminConfig, prm_webserverHost, prm_webserverPort, prm_webserverPortSSL 
	print ""
	print "VIRTUAL HOST creation..."
	corps_appli = re.sub(r"(SA_)?(sa-)?(_app)?(_pres)?",r"",prm_SA_NAME)
	prm_vhName = corps_appli + "_vh"
	print "Nom du VH : %s" % prm_vhName
	print "Valeurs par defaut :"
	print("%s / %s" % (prm_webserverHost, prm_webserverPort))
	print("%s / %s" % (prm_webserverHost, prm_webserverPortSSL))
	prm_vhAliases = "[['hostname' %s],['port' %s]] [['hostname' %s],['port' %s]]" % (prm_webserverHost, prm_webserverPort,prm_webserverHost,prm_webserverPortSSL)

	print "START"
	vhAlreadyExists = 0
	virtualhosts = _splitlines(AdminConfig.list('VirtualHost'))
	for vh in virtualhosts :
		vhName = AdminConfig.showAttribute(vh,'name')
		if vhName == prm_vhName:
			vhAlreadyExists = 1

	if vhAlreadyExists == 1:
			print("Similar virtual host already exists")
			print("NOT DONE")
	else:
		cell = AdminConfig.list('Cell')
		vhost = AdminConfig.create('VirtualHost', cell,[['name', prm_vhName]])
		AdminConfig.modify(vhost,[['aliases', prm_vhAliases]])
		AdminConfig.save()
		print "DONE"
	print ""


def createSharedLibs(prm_nodeName, prm_serverName):
	global prm_description,prm_libclassPath,prm_libNativePath,prm_libIsolatedClassLoader

	objId=""
	libId=""
	corps_appli = re.sub(r"(SA_)?(sa-)?(_app)?(_pres)?",r"",prm_serverName)
	prm_libName = corps_appli + "_shared" 
	prm_description = prm_libName + " shared Librairies"
	
	print "SHARED LIBRARY creation ..."
	print "Creation of the library,\"%s\",pour %s/%s" % (prm_libName,prm_nodeName,prm_serverName)
	objId = AdminConfig.getid('/Node:%s/Server:%s' % (prm_nodeName,prm_serverName))
	libId = AdminConfig.getid('/Node:%s/Server:%s/Library:%s' % (prm_nodeName,prm_serverName,prm_libName))

	if objId == "":
  		print "Portee invalide : nom ou noeud inconnu !"
  		sys.exit(1)

	name = ['name',prm_libName]
	description = ['description', prm_description]
	classpath = ['classPath',  prm_libclassPath]
	nativepath = ['nativePath', prm_libNativePath]

	icl = ['isolatedClassLoader', prm_libIsolatedClassLoader]
  	parameters = [name, description, classpath, nativepath, icl]

	serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (prm_nodeName, prm_serverName)) 
	if serverId == "":
		print "Cannot create shared librairies because application server does not exist."
		print "NOT DONE"
	else:
		if libId != "":
			print "Shared library \"%s\" already exists !" % prm_libName
			print "NOT DONE"
		else:
			AdminConfig.create('Library', objId, parameters)
			AdminConfig.save()
			print "DONE"
	print ""

def setWebServerConfig(wServerId,wServerParent):
	global AdminConfig
	global prm_pluginlogFilename,prm_pluginInstallRoot,prm_pluginRefreshInterval,prm_pluginLogLevel
	global prm_pluginProperties,prm_pluginLoadBalance,prm_pluginRetryInterval
	global prm_webConfigurationFilename

	prm_pluginlogFilename = "%s/logs/%s/http-plugin.log" % (prm_webInstallRoot,  prm_webserverName)
	
	pgin = AdminConfig.list('PluginProperties', wServerId)

	AdminConfig.modify(pgin,[['LogFilename', prm_pluginlogFilename]])
	AdminConfig.modify(pgin,[['PluginInstallRoot', prm_pluginInstallRoot]])
	AdminConfig.modify(pgin,[['RefreshInterval', prm_pluginRefreshInterval]])
	AdminConfig.modify(pgin,[['LogLevel', prm_pluginLogLevel]])
	AdminConfig.modify(pgin,[['PluginGeneration', 'MANUAL']])
	AdminConfig.modify(pgin,[['PluginPropagation', 'MANUAL']])

	AdminConfig.modify(pgin, [['properties', []]])
	if prm_pluginProperties != "":
		AdminConfig.modify(pgin, [['properties', prm_pluginProperties]])

	pscp = AdminConfig.list('PluginServerClusterProperties', pgin)
	AdminConfig.modify(pscp, [['LoadBalance', prm_pluginLoadBalance]])
	AdminConfig.modify(pscp, [['RetryInterval', prm_pluginRetryInterval]])

	processDef = AdminConfig.list('ProcessDef', wServerParent)
	AdminConfig.modify(processDef, [['startCommandArgs', ""]])
	AdminConfig.modify(processDef, [['stopCommandArgs', ""]])
	startCmd = "-k start -f %s" % prm_webConfigurationFilename
	stopCmd = "-k stop -f %s" % prm_webConfigurationFilename
	AdminConfig.modify(processDef, [['startCommandArgs', [startCmd]]])
	AdminConfig.modify(processDef, [['stopCommandArgs', [stopCmd]]])

def setHost(serverEntry,hostName):
	global AdminConfig
	specialEndPoints=_splitlines(_splitlist(AdminConfig.showAttribute(serverEntry, 'specialEndpoints')))[0]
	for specialEndPoint in specialEndPoints:
		ePoint = AdminConfig.showAttribute(specialEndPoint, 'endPoint')
		AdminConfig.modify(ePoint,[['host', hostName]])
		value = AdminConfig.show(ePoint)
	AdminConfig.save()

def createWebServer(prm_nodeName,prm_serverName,prm_webserverHost,prm_webserverPort,prm_WAS_VERSION):
	global prm_webConfigurationFilename,prm_webLogFilenameError,prm_webLogFilenameAccess, prm_webserverName

	corps_appli = re.sub(r"(^SA_)?(^sa-)?(_app)?(_pres)?",r"",prm_serverName)

	prm_WAS_VERSION = int(prm_WAS_VERSION)

	if prm_WAS_VERSION >= 85:
		prm_webserverName = "sw-" + corps_appli
	else:
		prm_webserverName = "https-" + corps_appli

	if prm_nodeName is None or prm_nodeName == "": 
		print "ERROR : Missing argument %s" % prm_nodeName
		sys.exit(1)

	if prm_webserverHost is None or prm_webserverHost == "":
		print "ERROR : Missing argument %s" % prm_webserverHost
		sys.exit(1)

	if prm_webserverPort is None or prm_webserverPort == "":
		print "ERROR : Missing argument %s" % prm_webserverPort
		sys.exit(1)

	nodeId = AdminConfig.getid('/Node:%s/' % prm_nodeName)
	if nodeId == "":
		print "Specified node not correct"
		sys.exit(1)

	if AdminConfig.getid('/Node:%s/Server:%s/' % (prm_nodeName, prm_webserverName)) != "":
		print("Server Web /Node:%s/Server:%s/ already exists" % (prm_nodeName, prm_webserverName))
		print("NOT DONE")
	else:
		prm_webConfigurationFilename="%s/%s/conf/httpd.conf" % (prm_webInstallRoot,prm_webserverName)
		prm_webLogFilenameError="%s/logs/%s/error_log" % (prm_webInstallRoot,prm_webserverName)
		prm_webLogFilenameAccess="%s/logs/%s/access_log" % (prm_webInstallRoot,prm_webserverName)

		print "WEB SERVER creation from template IHS"
		print("Nom : %s" % prm_webserverName)
		wServerParent = AdminTask.createWebServer(prm_nodeName,['-name',prm_webserverName,'-templateName','IHS','-serverConfig',[[prm_webserverPort,prm_webInstallRoot,prm_pluginInstallRoot,prm_webConfigurationFilename,"",prm_webLogFilenameError,prm_webLogFilenameAccess,'HTTP']]])

		wServerId = AdminConfig.list('WebServer', wServerParent)
		if wServerId == "":
			print "Erreur inattendue, impossible de creer le web server!"
			sys.exit(1)

		AdminConfig.save()

		setWebServerConfig(wServerId,wServerParent)

		# modification de l'adresse d'ecoute
		serverEntries = _splitlines(AdminConfig.list('ServerEntry', nodeId))
		for serverEntry in serverEntries:
			sName = AdminConfig.showAttribute(serverEntry,'serverName')
			if sName == prm_webserverName:
				setHost(serverEntry, prm_webserverHost)

		print "Serveur Web %s initialized" % prm_webserverName
		AdminConfig.save()
		print "DONE"
		print ""
	


def createNewApplicationServer(nodeName,serverName):
	global prm_WAS_VERSION,prm_serverLogRoot

	print ''
	print '==> Start creation of sa "%s" on node "%s" from template "default"' % (serverName,nodeName)
	idNewSA = CreateNewSA(nodeName,serverName)   

	nodeId = AdminConfig.getid('/Node:%s/' % nodeName)
	serverId = AdminConfig.getid('/Node:%s/Server:%s/' % (nodeName, serverName))
	print "Server %s initialized" % serverName

	serverEntries = _splitlines(AdminConfig.list('ServerEntry','%s' % nodeId))
	setServerPorts(serverId, serverEntries)
	AdminConfig.save()
	configExistingServer(nodeName, serverName, prm_serverLogRoot)
	AdminConfig.save()


#--------------------
# Programme Principal
#--------------------

# Application server creation & configuration
if os.environ["CREATE_SA"] == "yes":
	createNewApplicationServer(prm_nodeName,prm_SA_NAME)
	
# Virtual Host creation
if os.environ["CREATE_VH"] == "yes":
	createVirtualHost(prm_SA_NAME)
	AdminConfig.save()

# Shared libraries creation
if os.environ["CREATE_SHARED_LIBRARIES"] == "yes":
	createSharedLibs(prm_nodeName, prm_SA_NAME)
	AdminConfig.save()

# Web server creation
if os.environ["CREATE_WEB_SERVER"] == "yes":
	createWebServer(prm_nodeName, prm_SA_NAME, prm_webserverHost, prm_webserverPort, prm_WAS_VERSION)
	AdminConfig.save()

