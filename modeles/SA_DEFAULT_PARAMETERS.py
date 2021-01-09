# standard.py : default settings for some parameters


# WAS version
#prm_WAS_VI="8.5"
#prm_WAS_VI="7.0"
#prm_WAS_VERSION_NUM="85"
#prm_WAS_VERSION_NUM="70"
prm_WAS_EDITION="ND"
prm_JVM_BITNESS=64

prm_APP_ROOT_VAR_VALUE="/apps/wasapp"

# ******************** SYSTEM PARAMETERS (DO NOT MODIFY)
prm_startingPort="AUTO"
prm_portRangeWide=20 
prm_nodeTempDir="DEFAULT"
prm_checkPortConflict="true"

prm_listPortToModify="BOOTSTRAP_ADDRESS CSIV2_SSL_MUTUALAUTH_LISTENER_ADDRESS CSIV2_SSL_SERVERAUTH_LISTENER_ADDRESS DCS_UNICAST_ADDRESS IPC_CONNECTOR_ADDRESS DUMMY DUMMY SIP_DEFAULTHOST ORB_LISTENER_ADDRESS DUMMY SOAP_CONNECTOR_ADDRESS SIB_ENDPOINT_ADDRESS SIB_ENDPOINT_SECURE_ADDRESS SIB_MQ_ENDPOINT_ADDRESS SIB_MQ_ENDPOINT_SECURE_ADDRESS WC_defaulthost OVERLAY_TCP_LISTENER_ADDRESS OVERLAY_UDP_LISTENER_ADDRESS"

if prm_WAS_EDITION == "ND" :
     prm_listPortToDelete="WC_adminhost WC_adminhost_secure WC_defaulthost_secure SAS_SSL_SERVERAUTH_LISTENER_ADDRESS SIP_DEFAULTHOST_SECURE"
     prm_listTransportChainToDelete="WCInboundAdmin WCInboundAdminSecure WCInboundDefaultSecure SIPCInboundDefaultSecure HttpQueueInboundDefaultSecure"
else:
     prm_listPortToDelete="WC_defaulthost_secure SAS_SSL_SERVERAUTH_LISTENER_ADDRESS SIP_DEFAULTHOST_SECURE"
     prm_listTransportChainToDelete="WCInboundDefaultSecure SIPCInboundDefaultSecure HttpQueueInboundDefaultSecure"


#prm_nodeTempDir="/apps/WebSphere/profiles85/temp"
#prm_nodeTempDir="/apps/WebSphere/profiles7/temp"

# ******************** END OF SYSTEM PARAMETERS

# ******************** Appserver (CrAppServer, CrClone, ConfigServer)

# for CrAppServer : prm_serverType=S -> stand alone server (default), prm_serverType=C -> Cluster member
prm_serverType="S"

# processus settings
prm_processPriority=20
prm_umask=022
prm_workingDirectory="\${USER_INSTALL_ROOT}"

# jvm heapsize
prm_maximumHeapSize=128
prm_initialHeapSize=50

# jvm classpath
prm_classpath=""
prm_jvmClassLoader="false"
prm_jvmClassLoaderMode="PARENT_FIRST"
prm_jvmClassLoaderSharedLibrary=""

# jvm properties (custom properties)
prm_jvmprop=[[['name','java.awt.headless'],['value','true']],[['name','client.encoding.override'],['value','UTF-8']]]
#prm_jvmprop=[]
#prm_jvmprop.append([[name 'java.awt.headless'] [value 'true']])
#prm_jvmprop.append([[name 'client.encoding.override'] [value 'UTF-8']])
#prm_jvmprop.append([[name 'com.ibm.websphere.servlet.temp.dir'] [value 'chemin_a_definir']])
#prm_jvmprop.append([[name 'Log4j.OUTPUT_DIR'] [value 'chemin_a_definir']])
prm_jvmGenericArguments=""
prm_gcPolicy="gencon"


# orb client timeout : 30 seconds (instead of 3mn)
prm_orbReqTO=30
prm_orbLocReqTO=30

# web container properties
prm_wcprop=[['name','fileServingEnabled'],['value','true']]
#prm_wcprop=[]
#prm_wcprop.append([[name 'fileServingEnabled'] [value 'true']])
#prm_wcprop.append([[name 'serveServletsByClassnameEnabled'] [value 'false']])
#prm_wcprop.append([[name 'directoryBrowsingEnabled'] [value 'false']])
#prm_wcprop.append([[name 'com.ibm.ws.webcontainer.invokeFiltersCompatibility'] [value 'true']])

# web plugin properties

# connect timeout -> 15 seconds
prm_pluginConnectTimeout=15


# process environment variables (LIBPATH for example)

#prm_processEnv="[['IBM_HEAPDUMP_OUTOFMEMORY','false'],['IBM_JAVACORE_OUTOFMEMORY','false'],['IBM_JAVADUMP_OUTOFMEMORY','false'],['IBM_HEAPDUMPDIR','${SERVER_LOG_ROOT}'],['IBM_JAVACOREDIR','${SERVER_LOG_ROOT}']]" 
prm_processEnv=[['name','IBM_HEAPDUMP_OUTOFMEMORY'],['value','false']]

# number of archived log files for SystemOut and SystemErr
prm_nbBackupLog=10

# size in Mo of logs files for SystemOut and SystemErr
prm_rolloverSize=1

# web container thread pool settings
prm_tpwebMaximumSize=50
prm_tpwebMinimumSize=10
prm_tpwebInactivityTimeout=3500
prm_tpwebIsGrowable="false"
prm_webBindingAddress="*"

# HTTP Session persistence : none
prm_sessionPersistenceMode="N"

# orb thread pool settings
prm_tporbMaximumSize=50
prm_tporbMinimumSize=10
prm_tporbInactivityTimeout=3500
prm_tporbIsGrowable="false"

prm_clientInactivityTimeout=60
prm_totalTranLifetimeTimeout=120
prm_transactionLogDirectory="DEFAULT"

# v4.1 (July 2010) -> HAMAnager Service disabled by default 
# HAManagerService disabled by default
# enable it if the following services are used : Memory-to-memory replication, Singleton failover, WLM (EJB,JMS)

prm_enableHAManagerService="false"

# Java Attach Api disabled by default (CPU consumption problem with WAS 7)
prm_enableJavaAttachAPI="false"

# shared classes settings : D=Default, N=None, C=Custom
prm_shared_classes="N"

# shared classes option (-Xshareclasses:${prm_shared_classes_options}), only if prm_shared_classes=C
prm_shared_classes_options="name=webspherev70_%g,groupAccess,nonFatal"

# shared classes size in Mo (-Xscmx${prm_shared_classes_size}M), only if prm_shared_classes=C
prm_shared_classes_size=50

prm_instrumentationType="N"

# ******************* WebServer  (CrWebServer)
#prm_pluginInstallRoot="/apps/WebSphere/WebPlugins7"
#prm_webInstallRoot="/apps/IBMHTTPServer/WebServer7"
#prm_pluginInstallRoot="/apps/WebSphere/WebPlugins85"
#prm_webInstallRoot="/apps/IBMHTTPServer/WebServer85"

# load balancing alogorithm : possible values : ROUND_ROBIN or RANDOM
prm_pluginLoadBalance="ROUND_ROBIN" 
prm_pluginLogLevel="ERROR"
# reload frequency for plugin-cfg.xml file -> 1H
prm_pluginRefreshInterval=3600
# retry frequency for a clone marked down -> 10 mn
prm_pluginRetryInterval=600 

# ServerIOTimeout -> 20 mn
prm_pluginProperties="[['name','ServerIOTimeout'],['value',1200]]"

# For Base Server only
prm_stopWebServerShell="$prm_webInstallRoot/https-server1/stop"
prm_startWebServerShell="$prm_webInstallRoot/https-server1/start"

# ******************* Application Deployment

prm_earFilter="true"
prm_earFilterShell="${prm_dmgrInstallRoot}/adminweb/tools/earFilter.sh"

# if set to true -> session affinity will be disabled (CloneID removed from plugin cfg file) 
prm_disableSessionAffinity="false"
prm_disableSessionAffinityShell="${prm_dmgrInstallRoot}/adminweb/tools/removeCloneID.sh"


# example : set prm_mapRolesToUser {{"monitor" Yes Yes "" ""}}
prm_mapRolesToUsers=""

# possible values for prm_warClassLoaderPolicy : MULTIPLE or SINGLE
#   MULTIPLE = one class loader by module, SINGLE = a single class loader for the entire application
prm_warClassLoaderPolicy="MULTIPLE"

# possible values for prm_xxxClassLoaderMode = PARENT_FIRST or PARENT_LAST
prm_earClassLoaderMode="PARENT_FIRST"
prm_warClassLoaderMode="PARENT_FIRST"

# if set to true prm_warClassLoaderMode applies to the list of modules specified in prm_wclmSelectedModules
# if set to false prm_warClassLoaderMode applies to all web modules
prm_wclmApplyToSelectedModules="false"

# if prm_uninstallApp is set to true, all applications deployed on target (server or cluster) will be uninstalled first
prm_uninstallAllApp="false"

prm_stopWEB="true"
prm_stopWAS="true"
# maximum delay in seconds to wait until the servers are stopped. Application servers not stopped after expiration of this delay are terminated (killed).
prm_stopWASTimeout=60
prm_startWEB="true"
prm_startWAS="true"
prm_deployEJB="false"
# deploy EJB classpath : only if prm_deployEJB=true
prm_deployEJBClasspath=""
prm_precompileJSPs="false"
prm_appSharedLibrary=""
# if set to true shared librairies are mapped to web modules
prm_mapLibsToWebModules="false"

# sleep duration (1 mn) before restarting was server if prm_startWAS = true
# workaround to prevent app server server starting before complete synchronization
prm_sleepTimeBeforeStartWAS=60000

prm_overrideSessionMgt="false"
prm_sessionCookieName="JSESSIONID"
prm_sessionCookiePath="/"
prm_sessionCookieDomain=""
prm_sessionCookieTimeout=15
prm_sessionCookieMaximumAge=-1
prm_sessionCookieSecure="false"

# optional script to execute after installing the application
prm_appPostInstallScript=""


# ********************* jdbc and MQ
prm_description=""
prm_category=""

# ******************** variable
prm_varDesc=""

# ********************* shared library
prm_libNativePath=""
# isolated class loader : >= WAS 7.0 only
prm_libIsolatedClassLoader="false"

# ******************* jdbc datasource settings 
prm_statement_cache_size=60
prm_connection_timeout=60
prm_max_connections=20
prm_min_connections=0
# purge policy : true -> entire pool, false -> failing connection only
prm_purgeEntirePool="true"
prm_reap_time=180
prm_unused_timeout=1800
prm_aged_timeout=0
# par defaut : data source non xa
prm_xaEnabled="false" 
# prm_oracle_version : 9 or 10
prm_oracle_version=9
# prm_sybase_version : 2 (jconn2) or 3 (jconn3) jconn3 is supported only for WAS 6.1
prm_sybase_driverVersion="2"
# isolation level of transaction datasource properties value "DEFAULT" let websphere set his default = 4 (TRANSACTION_REPEATABLE_READ)
prm_defaultIsolationLevel="DEFAULT" 
# JAAS alias not set by default -> preferred way : set during deployment
prm_auth_alias_name=""

# ****************** URL
prm_defaultURLProvider="Default URL Provider"


# ******************* MQ settings
# possible values for prm_mq_transportType : B or C
#   B = Bindings (Server mode), C = Client (in this case a channel must be specified)
prm_mq_transportType="B"
prm_mq_xaEnabled="false"
prm_mq_CCSID=""
prm_mq_targetClient="JMS"
# possible values for prm_mq_persistence : APPLICATION_DEFINED, PERSISTENT, QUEUE_DEFINED, NONPERSISTENT
prm_mq_persistence="APPLICATION_DEFINED"

# *** MQ connection pool
prm_mq_con_connection_timeout=60
prm_mq_con_max_connections=20
prm_mq_con_min_connections=0
prm_mq_con_reap_time=180
prm_mq_con_unused_timeout=1800
prm_mq_con_aged_timeout=0

# ** MQ session pool
prm_mq_ses_connection_timeout=60
prm_mq_ses_max_connections=20
prm_mq_ses_min_connections=0
prm_mq_ses_reap_time=180
prm_mq_ses_unused_timeout=1800
prm_mq_ses_aged_timeout=0

# ** Listener port
prm_lp_maxRetries=0
prm_lp_maxSessions=1
prm_lp_maxMessages=1


# ** possible values for prm_lp_initialState : START or STOP

prm_lp_initialState="START"

prm_logType="B"
prm_javacoredir="/apps/core/javacore"
