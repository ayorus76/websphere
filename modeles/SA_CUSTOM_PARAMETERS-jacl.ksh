#!/bin/ksh

echo "set prm_WAS_VERSION \"${prm_WAS_VERSION}\""
echo "set prm_SA_NAME \"${SA_NAME}\""
echo "set prm_serverType \"APPLICATION_SERVER\""
echo "set prm_HOST \"${HOST}\""
#echo "set prm_NODE_NAME \"${SERVER_NODES}\""
#echo "set prm_scope \"${SCOPE}\""

if [[ ${prm_WAS_VERSION} -eq 85 ]] ; then
	echo "set prm_serverLogRoot \"${PAWAS_DIR}/logs/${CODE_AP}-${PENTAGRAM}-fr\""
	echo "set prm_APP_DIR \"${PAWAS_DIR}/${CODE_AP}-${PENTAGRAM}-fr/was/${SA_NAME}\""
	echo "set prm_APP_IHS_DIR \"${PAWAS_DIR}/${CODE_AP}-${PENTAGRAM}-fr/ihs/${SA_NAME}\""
	echo "set prm_LOGS_DIR \"${PAWAS_DIR}/logs/${CODE_AP}-${PENTAGRAM}-fr/was/${SA_NAME}\""
	echo "set prm_LOGS_IHS_DIR \"${PAWAS_DIR}/logs/${CODE_AP}-${PENTAGRAM}-fr/ihs/${SA_NAME}\""
	echo "set prm_installDir \"${PAWAS_DIR}/${CODE_AP}-${PENTAGRAM}-fr/was/${SA_NAME}/installedApps\""
	prm_Log4j_OUTPUT_DIR=${PAWAS_DIR}/logs/${CODE_AP}-${PENTAGRAM}-fr/was/${SA_NAME}
	echo "set prm_Log4j_OUTPUT_DIR \"${PAWAS_DIR}/logs/${CODE_AP}-${PENTAGRAM}-fr/was/${SA_NAME}\""
	prm_nodeTempDir=${PAWAS_DIR}/${CODE_AP}-${PENTAGRAM}-fr/was/${SA_NAME}/temp
	echo "set prm_nodeTempDir \"${PAWAS_DIR}/${CODE_AP}-${PENTAGRAM}-fr/was/${SA_NAME}/temp\""
	COULOIR=${SA_NAME#-[0-9][0-9]$}
	echo "set prm_INSTALLABLE_EAR_DIR \"${SAMPLE_DIR}/${GLOBAL_APP_NAME}/installableApps\""
	echo "set prm_IHS_NAME \"sw-${SA_NAME#sa-}\""
	IHS_NAME="sw-${SA_NAME#sa-}"
	echo "set prm_webServerList [subst {{\"${WEBSERVER_HOST}\" \"${IHS_NAME}\"}}]"
	echo "set prm_VH_NAME \"${SA_NAME#sa-}_vh\""

	# JDBCProvider attributes (ResourceType = \"JDBCProvider)
	SHARED_JDBC_DIR=${PAWAS_DIR}/${CODE_AP}-${PENTAGRAM}-fr/was/${SA_NAME}/jdbc/${TRIGRAM}_${MODULE_NAME}

	# Library Section (ResourceType = \"Library)
	SHARED_CLASSES_DIR=${PAWAS_DIR}/${CODE_AP}-${PENTAGRAM}-fr/was/${SA_NAME}/conf/${TRIGRAM}_${MODULE_NAME}
	SHARED_SECRETS_DIR=${PAWAS_DIR}/${CODE_AP}-${PENTAGRAM}-fr/was/${SA_NAME}/secrets/${TRIGRAM}_${MODULE_NAME}
	SHARED_LIB_DIR=${PAWAS_DIR}/${CODE_AP}-${PENTAGRAM}-fr/was/${SA_NAME}/lib/${TRIGRAM}_${MODULE_NAME}
elif [[ ${prm_WAS_VERSION} -eq 70 ]] ; then
	echo "set prm_serverLogRoot \"${PAWAS_DIR}/${GLOBAL_APP_NAME}/logs\""
	echo "set prm_APP_DIR \"${PAWAS_DIR}/${GLOBAL_APP_NAME}\""
	echo "set prm_LOGS_DIR \"${PAWAS_DIR}/${GLOBAL_APP_NAME}/logs\""
	echo "set prm_installDir \"${PAWAS_DIR}/${GLOBAL_APP_NAME}/installedApps\""
	echo "set prm_INSTALLABLE_EAR_DIR \"${SAMPLE_DIR}/${GLOBAL_APP_NAME}/installableApps\""
	prm_Log4j_OUTPUT_DIR=${PAWAS_DIR}/${GLOBAL_APP_NAME}/logs
	echo "set prm_Log4j_OUTPUT_DIR \"${PAWAS_DIR}/${GLOBAL_APP_NAME}/logs\""
	prm_nodeTempDir=${PAWAS_DIR}/${GLOBAL_APP_NAME}/temp
	echo "set prm_nodeTempDir \"${PAWAS_DIR}/${GLOBAL_APP_NAME}/temp\""
	IHS_NAME=https-${GLOBAL_APP_NAME}
	echo "set prm_webServerList [subst {{\"${WEBSERVER_HOST}\" \"${IHS_NAME}\"}}]"
	echo "set prm_IHS_NAME \"https-${GLOBAL_APP_NAME}\""
	echo "set prm_IHS_DIR \"${PAWAS_DIR}/${GLOBAL_APP_NAME}/${IHS_NAME}\""
	echo "set prm_IHS_LOGS_DIR_PRES \"${PAWAS_DIR}/${GLOBAL_APP_NAME}/logs/${IHS_NAME}\""
	echo "set prm_VH_NAME \"${GLOBAL_APP_NAME}_vh\""

	# JDBCProvider attributes (ResourceType = \"JDBCProvider)
	SHARED_JDBC_DIR=${PAWAS_DIR}/${GLOBAL_APP_NAME}/shared/jdbc

	# Library Section (ResourceType = \"Library)
	SHARED_CLASSES_DIR=${PAWAS_DIR}/${GLOBAL_APP_NAME}/shared/classes
	SHARED_SECRETS_DIR=${PAWAS_DIR}/${GLOBAL_APP_NAME}/shared/secrets
	SHARED_LIB_DIR=${PAWAS_DIR}/${GLOBAL_APP_NAME}/shared/lib
fi

echo "set prm_transactionLogDirectory \"${NODE_DIR}/tranlog/${DMGR_HOST}Network/${SERVER_NODES}/${SA_NAME}/transaction/tranlog\""

# Process definition (ResourceType = \"JavaProcessDef)
echo 'set prm_workingDirectory "\${USER_INSTALL_ROOT}"'

# Execution Environment (ResourceType = \"ProcessExecution)
echo "set prm_processPriority 20"
echo "set prm_umask \"022\""

# JVM (ResourceType = \"JavaVirtualMachine)
echo "set prm_initialHeapSize \"${MEMORY_MIN}\""
echo "set prm_maximumHeapSize \"${MEMORY_MAX}\""

echo "set prm_jvmClasspath \"${SHARED_CLASSES_DIR}/properties/log4j\""

if [[ -z ${CUSTOM_ARGUMENT} ]] ; then
	echo "set prm_genericJvmArguments \"-Xshareclasses:none  -Xgcpolicy:gencon\""
else
	echo "set prm_genericJvmArguments ${CUSTOM_ARGUMENT}"
fi

# JVM custom properties and environment entries
echo 'set prm_jvmprop {{{name "java.awt.headless"}{value "true"}}{{name "client.encoding.override"}{value "UTF-8"}}{{name "Log4j.OUTPUT_DIR"}{value "${prm_Log4j_OUTPUT_DIR}"}}{{name "com.ibm.websphere.servlet.temp.dir"}{value "${prm_nodeTempDir"}}}}'

echo 'set prm_processEnv {{{name "IBM_HEAPDUMP_OUTOFMEMORY"}{value "false"}}{{name "IBM_JAVACORE_OUTOFMEMORY"}{value "false"}}{{name "IBM_JAVADUMP_OUTOFMEMORY"}{value "false"}}{{name "IBM_HEAPDUMPDIR"}{value "\${SERVER_LOG_ROOT}"}}{{name IBM_JAVACOREDIR}{value "\${SERVER_LOG_ROOT}"}}}'

# TraceLog Section (ResourceType = \"TraceLog)
echo "set prm_maxNumberOfBackupFiles 5"
echo "set prm_rolloverSize 20"

# Thread pools (ResourceType = \"ThreadPool)
echo "set prm_tpminimumSize 10"
echo "set prm_tpinactivityTimeout 3500"
echo "set prm_tpmaximumSize 50"
echo "set prm_tpisGrowable \"false\""

# Thread pools ORB
echo "set prm_tporbminimumSize 10"
echo "set prm_tporbinactivityTimeout 3500"
echo "set prm_tporbmaximumSize 50"
echo "set prm_tporbisGrowable \"false\""

# Session Manager (ResourceType = \"SessionManager)
echo "set prm_sessionPersistenceMode \"NONE\""

# Web Container properties
#echo "prm_wcprop = \"['name','fileServingEnabled'],['value','true'],['name','serveServletsByClassnameEnabled'],['value','false'],['name','directoryBrowsingEnabled'],['value','false'],['name','com.ibm.ws.webcontainer.invokeFiltersCompatibility'],['value','true']\""
#echo "prm_wcprop = [['name','fileServingEnabled'],['value','true']]"
echo "set prm_wcprop {{{name fileServingEnabled}{value true}}{{name serveServletsByClassnameEnabled}{value false}}{{name directoryBrowsingEnabled}{value false}}{{name com.ibm.ws.webcontainer.invokeFiltersCompatibility}{value true}}}"

# WebserverPluginSettings (ResourceType = \"WebserverPluginSettings)
echo "set prm_pluginConnectTimeout 15"

# TransactionService (ResourceType = \"TransactionService)
echo "set prm_totalTranLifetimeTimeout 1200"
echo "set prm_clientInactivityTimeout 60"

# HAManagerService Section (ResourceType = \"HAManagerService)
echo "set prm_enableHAManagerService \"false\""
echo "set prm_enableJavaAttachAPI \"false\""

# JDBCProvider attributes (ResourceType = \"JDBCProvider)
echo "set prm_SHARED_JDBC_DIR \"${SHARED_JDBC_DIR}\""
echo "set prm_classpath \"${SHARED_JDBC_DIR}/ojdbc6.jar\""

# Library Section (ResourceType = \"Library)
echo "set prm_libclassPath \"${SHARED_LIB_DIR};${SHARED_CLASSES_DIR};${SHARED_SECRETS_DIR}\""

# Ports Section (ResourceType = \"Server)

# Virtual host

# Web Server
echo "set prm_webInstallRoot \"${prm_WEB_SERVER_DIR}\""
echo "set prm_pluginInstallRoot \"${prm_PLUGIN_DIR}\""
echo "set prm_webserverHost \"${WEBSERVER_HOST}\""
echo "set prm_webserverPort \"${WEBSERVER_PORT}\""
echo "set prm_webserverPortSSL \"${WEBSERVER_PORT_SSL}\""

# Classloading
#echo "set prm_earClassLoaderMode \"${EAR_CLASSLOADER_MODE}\""
#echo "set prm_warClassLoaderMode \"${WAR_CLASSLOADER_MODE}\""
#echo "set prm_warClassLoaderPolicy \"${WAR_CLASSLOADER_POLICY}\""

