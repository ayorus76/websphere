# -*- coding: utf-8 -*-

#import javax.management as mgmt
#import os,time,re
#execfile('%s' % os.environ["PYTHON_LIBRARY"])

print  "START"

if (prm_mapLibsToWebModules == "true" && prm_WAS_VERSION == "6.0"):
	print("ERROR : Option %s not supported in version 6.0" % prm_mapLibsToWebModules)
	sys.exit(1)


#-----------
# Cell infos
#-----------

cell  = getCellId()
cellName = getCellName() 


#-----------
# EAR filter
#-----------

if prm_earFilter == "true":
	print("Filtering ear %s ...  with %s" % (prm_ear, prm_earFilterShell))
  	exec "%s %s" % (prm_earFilterShell, prm_ear)


#------------
# Check scope
#------------

if (prm_scope == "C" || prm_scope == "CH"):
	clusterId = AdminConfig.getid("/ServerCluster:%s/" % prm_clusterName)
  	if clusterId == "":
    		print("ERROR : cluster %s does not exist" % prm_clusterName)
    		sys.exit(1)
elif (prm_scope == "S" || prm_scope == "SH"):
	serverId = AdminConfig.getid("/Node:%s/Server:%s" % (prm_nodeName, prm_serverName))
  	if serverId == "":
    		print ("ERROR : server %s does not exist on node %s" % (prm_serverName, prm_nodeName))
    		sys.exit(1)


#-----------------
# Stop Web servers
#-----------------

if (prm_scope == "CH" || prm_scope == "SH") && (prm_stopWEB == "true"):
	i = 0
  	while i < len(prm_webServerList):
		node = prm_webServerList["%s" % i][0]
    		server = prm_webServerList["%s" % i][1]
    		print  "Stopping WebServer $server on node %s" % node
	
    		# For Base Server
    		if prm_WAS_EDITION == "BASE":
			w = AdminControl.completeObjectName("WebSphere:type=WebServer,process=server1,cell=%s,*" % cellName)
		else:
			w = AdminControl.completeObjectName("WebSphere:type=WebServer,process=dmgr,cell=%s,*" % cellName)

		print  "---------------->> $w"
		
		# For Base Server
		if prm_WAS_EDITION == "BASE":
			print  "exec %s" % prm_stopWebServerShell
		
			# exec "$prm_stopWebServerShell"
      			if  [ catch { exec "$prm_stopWebServerShell" } { result } ]:
				print  "%s on node %s is not running" % (server, node)
			else:
				if { [ catch { $AdminControl invoke $w stop [subst { $cellName $node $server} ] } result ] } {
					print  "Error when stopping $server on node $node : $result"
		i = [expr $i + 1]


#-------------------------
# Stop application servers
#-------------------------

# arret des server was
if prm_stopWAS == "true":
	# For Base Server, do not stop Server now
	if prm_WAS_EDITION == "ND":
		listServers = ""
		if (prm_scope == "C" || $prm_scope == "CH"):
			print  "Stopping cluster %s..." % prm_clusterName
			clusterId = AdminConfig.getid("/ServerCluster:%s/" % prm_clusterName)
			clusterMembers = AdminConfig.list("ClusterMember,%s" % clusterId)
			clusterSize = len("%s" % clusterMembers)
			for {set i 0} {$i < $clusterSize} {incr i 1} {
				member = clusterMembers[i]
				serverName = AdminConfig.showAttribute("%s", memberName) % member
				nodeName = AdminConfig.showAttribute("%s", nodeName) % member
				listServers = append [list $nodeName $serverName]
		elif prm_scope == "S" || prm_scope == "SH":
			print  "Stopping server $prm_serverName..."
			listServers = [list $prm_nodeName $prm_serverName]
	stopAppServers $listServers $prm_stopWASTimeout


#--------------------------------------
# Application desinstallation if exists
#--------------------------------------

if prm_app == "":
	prm_app = getAppNameFromEar("%s" % prm_ear)
	print  "Application Name extracted from ear : '%s'" % prm_app
	
if prm_uninstallAllApp != "true":
	# recherche si l'appli est deja installee
	print  "search appli..."
	appList = AdminApp.list()
	print  "... %s" % appList

	foreach app $appList:
	if { [string compare $app $prm_app] == 0 } {
		appExist = app
		break

	print  "uninstall appli..."
	# desinstallation si deja installee
	if { [info exists appExist] }:
		$AdminApp uninstall $prm_app
		print  "Application uninstalled"

if prm_uninstallAllApp == "true":
	if (prm_scope == "C" || prm_scope == "CH"):
		print  "Uninstalling all applications targeted on cluster %s" % prm_clusterName
		uninstallAppOnCluster $prm_clusterName
	else:
		print  "Uninstalling all applications target on server %s / %s" % (prm_nodeName, prm_serverName)
		uninstallAppOnServer $prm_nodeName $prm_serverName


#----------------------------
# EJB deploy & JSP precompile
#----------------------------

# specific options processing

if prm_deployEJB == "true":
	if prm_deployEJBClasspath != "":
		optDeployEJB = "-deployejb -deployejb.classpath $prm_deployEJBClasspath"
	else:
		optDeployEJB = "-deployejb"
else:
	optDeployEJB = ""

print  "optDeployEJB=%s" % optDeployEJB


if prm_precompileJSPs == "true":
	optPrecompileJSPs = "-preCompileJSPs"
else:
	optPrecompileJSPs = ""


#-------------------------
# Application installation
#-------------------------
  
print  "installing appli..."

if prm_bnd != "":
	print  "\[DEPRECATED]\ The use of a binding file is deprecated for WAS7 and higher. Please use the new action 'Application Properties Configuration'"
	if prm_installDir == "DEFAULT":
		$AdminApp install $prm_ear [ subst {-usedefaultbindings -defaultbinding.strategy.file $prm_bnd -appname $prm_app $optDeployEJB $optPrecompileJSPs}]
	else:
		$AdminApp install $prm_ear [ subst {-usedefaultbindings -defaultbinding.strategy.file $prm_bnd -appname $prm_app -installed.ear.destination $prm_installDir $optDeployEJB $optPrecompileJSPs}]
else:
	if WAS_VI < 7:
		print  "\[ERROR]\ No binding file is provided"
		exit 1
	else:
		if prm_installDir == "DEFAULT":
			$AdminApp install $prm_ear [ subst {-usedefaultbindings -appname $prm_app $optDeployEJB $optPrecompileJSPs}]
		else:
			$AdminApp install $prm_ear [ subst {-usedefaultbindings -appname $prm_app -installed.ear.destination $prm_installDir $optDeployEJB $optPrecompileJSPs}]

# Mapping security roles

if prm_mapRolesToUsers != "":
	print  "Mapping security roles : $prm_mapRolesToUsers"
	$AdminApp edit $prm_app [subst {-MapRolesToUsers $prm_mapRolesToUsers}]

# Preparation du deploiement

if (prm_scope == "CH" || prm_scope == "C"):
	toStart = "WebSphere:cell=%s,cluster=%s" % (cellName, prm_clusterName)
else:
	toStart = "WebSphere:cell=%s,node=%s,server=%s" % (cellName, prm_nodeName, prm_serverName)

if (prm_scope == "CH" || prm_scope == "SH":
	set i 0
  
	while {$i < [llength $prm_webServerList]} {
		set node [lindex [lindex $prm_webServerList $i] 0]
		set server [lindex [lindex $prm_webServerList $i] 1]
		print  "==> $node + $server"
		set toStart $toStart+WebSphere:cell=$cellName,node=$node,server=$server
		set i [expr $i + 1]

print  "%s" % toStart
set mod [$AdminApp view $prm_app {-MapModulesToServers}]
set bindex [expr [string first "Module:  " $mod] + 9]
set eindex [expr [string first "\nURI:  " $mod] - 1]
set bi2 [expr $eindex + 8]
set ei2 [expr [string first "\nServer:  " $mod] -1]
while {$eindex >-1} {
  set warAppName [string range $mod $bindex $eindex]
  print  "-----> $warAppName"
  set warFileName [string range $mod $bi2 $ei2]
  print  "-----> $warFileName"
  set mod [string range $mod $eindex [expr [string length $mod] + 10]]
  set bindex [expr [string first "Module:  " $mod] + 9]
  set mod [string range $mod $bindex [expr [string length $mod] + 10]]
  set bindex 0
  set eindex [expr [string first "URI:  " $mod] - 1]
  set bi2 [expr $eindex + 7]
  set ei2 [expr [string first "\nServer:  " $mod] -1]
  print  ">> \"$warAppName\" \"$warFileName\" "
  $AdminApp edit $prm_app [ subst { -MapModulesToServers {{\"$warAppName\" \"$warFileName\" $toStart}} }]
}

setWarClassLoaderPolicy $prm_app $prm_warClassLoaderPolicy
setEarClassLoaderMode $prm_app $prm_earClassLoaderMode

if { $prm_wclmApplyToSelectedModules == "true" } {
  setWarClassLoaderModeSelected $prm_app $prm_warClassLoaderMode $prm_wclmSelectedModules
} else {
  setWarClassLoaderMode $prm_app $prm_warClassLoaderMode
}

if {$prm_appSharedLibrary != ""} {
  if {$prm_mapLibsToWebModules == "true"} {
    setAppSharedLibraryForModules $prm_app $prm_appSharedLibrary
  } else {
    setAppSharedLibrary $prm_app $prm_appSharedLibrary
  }
}

if {$prm_overrideSessionMgt == "true"} {
  overrideSessionMgtApp $prm_app $prm_sessionCookieName $prm_sessionCookieDomain $prm_sessionCookiePath $prm_sessionCookieTimeout $prm_sessionCookieMaximumAge $prm_sessionCookieSecure
}

if { [info exists prm_appPostInstallScript] && $prm_appPostInstallScript != "" } {
  print  "executing post-installation script : $prm_appPostInstallScript ..."
  source $prm_appPostInstallScript
}



# sauvegarde de la config
$AdminConfig save
print  "Application $prm_app installed with success in $prm_installDir"


if {$prm_scope == "SH" || $prm_scope == "CH"} {
# regeneration du plug-in ihs
print  "regenerate plugin..."
#set pluginGen [$AdminControl completeObjectName type=PluginCfgGenerator,process=dmgr,*]
# For Base Server
if { $prm_WAS_EDITION == "BASE" } {
  set pluginGen [$AdminControl completeObjectName type=PluginCfgGenerator,process=server1,*]
} else {
  set pluginGen [$AdminControl completeObjectName type=PluginCfgGenerator,process=dmgr,*]
}


set i 0
while {$i < [llength $prm_webServerList]} {
  set node [lindex [lindex $prm_webServerList $i] 0]
  set server [lindex [lindex $prm_webServerList $i] 1]
  $AdminControl invoke $pluginGen generate "$prm_dmgrInstallRoot/config $cellName $node $server true"
  set i [expr $i + 1]
}

print  "Plug-in configuration file generated"
}

if {$prm_disableSessionAffinity == "true"} {
  if {$prm_scope == "SH" || $prm_scope == "CH"} {
    set i 0
    while {$i < [llength $prm_webServerList]} {
       set node [lindex [lindex $prm_webServerList $i] 0]
       set server [lindex [lindex $prm_webServerList $i] 1]
       print  "Disabling session affinity for web server $node/$server"
       exec "$prm_disableSessionAffinityShell" "$node" "$server"
       set i [expr $i + 1]
    }
    # correctif par Sylvain Noyon le 10 Mars : comme on modifie le fichier de plugin directement dans le repertoire
    # on force un refreshRepositoryEpoch
    #set configRepos [$AdminControl queryNames type=ConfigRepository,process=dmgr,*]
    # For Base Server
    if { $prm_WAS_EDITION == "BASE" } {
      set configRepos [$AdminControl queryNames type=ConfigRepository,process=server1,*]
    } else {
      set configRepos [$AdminControl queryNames type=ConfigRepository,process=dmgr,*]
    }

    $AdminControl invoke $configRepos refreshRepositoryEpoch
  }

}


#---------------------
# Cell synchronization
#---------------------

# synchro de la cellule
foreach node_sync [$AdminControl queryNames type=NodeSync,process=nodeagent,*] {
  print  "Synchronization of node $node_sync"
  $AdminControl invoke $node_sync sync
}


#-------------------------
# Start application server
#-------------------------

if {$prm_startWAS == "true"} {
    print  "sleeping for $prm_sleepTimeBeforeStartWAS milliseconds before starting WAS"
    after $prm_sleepTimeBeforeStartWAS
    if {$prm_scope == "S" || $prm_scope == "SH"} {
      print  "Starting server $prm_serverName"
      # For Base Server
      if { $prm_WAS_EDITION == "BASE" } {
         print  "exec $prm_stopStartSvradmin stop"
         exec "$prm_stopStartSvradmin" "stop"
         print  "exec $prm_stopStartSvradmin start"
         exec "$prm_stopStartSvradmin" "start"
         # Wait a while
         print  "sleeping for $prm_sleepTimeBeforeStartWAS milliseconds after starting server"
         after $prm_sleepTimeBeforeStartWAS
      } else {
        $AdminControl startServer $prm_serverName $prm_nodeName
      }
    } else {
      set clusterId [$AdminConfig getid /ServerCluster:$prm_clusterName/]
      print  "clusterId : $clusterId"
      set cmembers [lindex [lindex [$AdminConfig show $clusterId {members}] 0] 1]


      # redemarrage du cluster
      print  "Starting cluster $prm_clusterName"
      foreach clusterMember $cmembers {
        set nodeName [$AdminConfig showAttribute $clusterMember nodeName]
        set memberName [$AdminConfig showAttribute $clusterMember memberName]
        set nodeId [$AdminControl queryNames type=Server,node=$nodeName,process=nodeagent,*]
        if {$nodeId == ""} {
          print  "WARNING : unable to start server $memberName on node $nodeName -> node agent not running"
        } else {
          $AdminControl startServer $memberName $nodeName
          print  "Instance $memberName started"
        }
      }
   }
}

#-----------------
# Start web server
#-----------------

if {$prm_scope == "SH" || $prm_scope == "CH"} {
    if {$prm_startWEB == "true"} {
        set i 0
	while {$i < [llength $prm_webServerList]} {
	  set node [lindex [lindex $prm_webServerList $i] 0]
	  set server [lindex [lindex $prm_webServerList $i] 1]
	  print  "Starting WebServer $server on node $node"

          # For Base Server
          if { $prm_WAS_EDITION == "BASE" } {
            print  "exec $prm_startWebServerShell"
            exec "$prm_startWebServerShell"
          } else {
	    if { [ catch { $AdminControl startServer $server $node } result ] } {
	      print  "Error when starting $server on node $node : $result"
	    }
          }
	  set i [expr $i + 1]
	}
    }
}
print  "DONE"
