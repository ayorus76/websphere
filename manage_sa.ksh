#!/bin/ksh

#----------
# Variables
#----------

export SCRIPT_VERSION="2.6"	# Script version

export USER=`whoami`	# Connected user

# Date and time
export DATE=$(date +"%d%m%y")
export HEURE=$(date +"%H%M%S")

# Root script & logs folders
export SCRIPT_ROOT_DIR=$(cd -P $(dirname $0); pwd)
export SCRIPT_LOGS=${SCRIPT_ROOT_DIR}/logs                                                                                

export CONFIG_DIR=${SCRIPT_ROOT_DIR}/config
export MODELES_DIR=${SCRIPT_ROOT_DIR}/modeles

# Python libraries & functions
export PYTHON_DIR=${SCRIPT_ROOT_DIR}/python
export PYTHON_LIBRARY=${PYTHON_DIR}/functions.py
export SA_DEFAULT_PARAMETERS=${MODELES_DIR}/SA_DEFAULT_PARAMETERS.py

# Props files folder
export LIVRAISONS_DIR=${SCRIPT_ROOT_DIR}/livraisons

# SA variables, environment profile
# jython
export SA_CUSTOM_PARAMETERS_JYTHON=${MODELES_DIR}/SA_CUSTOM_PARAMETERS-jython.ksh		# Application server custom configuration
export APP_CUSTOM_PARAMETERS_JYTHON=${MODELES_DIR}/APP_CUSTOM_PARAMETERS-jython.ksh		# Application custom configuration

# jacl
export SA_CUSTOM_PARAMETERS_JACL=${MODELES_DIR}/SA_CUSTOM_PARAMETERS-jacl.ksh
export APP_CUSTOM_PARAMETERS_JACL=${MODELES_DIR}/APP_CUSTOM_PARAMETERS-jacl.ksh

export COMMON_JACL=${MODELES_DIR}/common.jacl

SCRIPT_DEPLOY=""


#------------------------------------
# User profile & environment settings
#------------------------------------

case "${USER}" in
	was7*)		. ${CONFIG_DIR}/userProfiles/was7Profile 2> /dev/null
			;;
	was85*)		. ${CONFIG_DIR}/userProfiles/was85Profile 2> /dev/null
			;;
	was)		. ${CONFIG_DIR}/userProfiles/wasProfile 2> /dev/null
			;;
	*)		echo "Please connect with a WebSphere user. This script must be run on WebSphere 7 version or higher."	
			exit 1
			;;	
esac

chmod -R 755 ${SCRIPT_ROOT_DIR}


#-------------
# Prerequisite
#-------------

f_Usage()
{
        echo "This script needs an argument (props file id) : $0 12345"
        echo ""
        echo "Version script : ${SCRIPT_VERSION}"
	exit 2
}

# Check if an argument (props id) is provided
if [ $# -ne 1 ] ; then f_Usage ; fi	# No argument 

# Check if props name is provided and exists
if [ -f "${LIVRAISONS_DIR}/$1.props" ] ; then
        export LOG=${SCRIPT_LOGS}/$(basename $0)-$1.log
else
        echo "Props file does not exist."
	exit 6
fi

# Check if DMGR is installed on current server
if [ ! -d ${DMGR_DIR} ] ; then echo "This script must be executed from WebSphere manager server (DMGR)!" ; exit 8 ; fi


#------------
# Logs & lock
#------------

echo "log file : ${LOG}"

echo "" > ${LOG}
if (( $? != 0 )); then
	echo "Unable to write into ${LOG}"
	exit 9
else
	exec 1> ${LOG}	
	echo "Script version : ${SCRIPT_VERSION}"
	echo ""
fi

${CONFIG_DIR}/lock.sh $$
if (( $? != 0 )); then
	echo "Unable to get lock " >> ${LOG}
	exit 10
fi


#-------------------------------
# Props file ID check & analysis
#-------------------------------

export propsFile=${LIVRAISONS_DIR}/$1.props

CREATION_SA_RESULT=0
export CREATE_SA=$(grep '^CREATE_SA' ${propsFile} | awk -F '=' '{ print $2 }')	# SA creation ?
MANAGE_RESOURCES=$(grep '^MANAGE_RESOURCES' ${propsFile} | awk -F '=' '{ print $2 }')  # Application resources creation/update ?

if [ -z "${CREATE_SA}" ] ; then echo "Variable CREATE_SA must be specified." ; missingVariable=110 ; exit 110 ; fi 
if [ -z "${MANAGE_RESOURCES}" ] ; then echo "Variable MANAGE_RESOURCES must be specified." ; missingVariable=110 ; exit 110 ; fi 


#----------------------------------------------
# SA : name, code AP, pentagram, scripts folder
#----------------------------------------------

export SA_NAME=$(awk -F'=' '/SA_TRIG_NAME_TYPE=/ { print $2 }' ${propsFile})
export CODE_AP=$(awk -F'=' '/CODE_AP=/ { print $2 }' ${propsFile}) 
export PENTAGRAM=$(awk -F'=' '/PENTAGRAM=/ { print $2 }' ${propsFile}) 
export TRIGRAM=$(awk -F'=' '/TRIGRAM=/ { print $2 }' ${propsFile}) 
export MODULE_NAME=$(awk -F'=' '/MODULE_NAME=/ { print $2 }' ${propsFile}) 
export CUSTOM_ARGUMENT=$(awk -F'=' '/GENERIC_ARGUMENT=/ { print $2 }' ${propsFile}) 
export EAR_NAME=$(awk -F'=' '/EAR_NAME=/ { print $2 }' ${propsFile})
export DMGR_HOST=$(hostname)

if echo ${SA_NAME} | grep '^sa-' > /dev/null
then
	export COULOIR=$(echo ${SA_NAME#sa-} | awk -F'-' '{ print $NF }')
	GLOBAL_APP_NAME=${TRIGRAM}_${MODULE_NAME}-${COULOIR}
	SHARED_NAME=$(echo ${SA_NAME#sa-}) 
elif echo ${SA_NAME} | grep '^SA_' > /dev/null
then
	GLOBAL_APP_NAME=$(echo ${SA_NAME#SA_} | sed 's/_.*//')
	SHARED_NAME=$(echo ${SA_NAME#SA_} | sed 's/_.*//')
fi

export GLOBAL_APP_NAME
export SHARED_NAME


#-------------------------------------------------------------
# New SA creation process : variables collect & initialization
#-------------------------------------------------------------

if [ ${CREATE_SA} == "yes" ] ; then
	echo "==> Initialization of application server parameters before creation (EAR_NAME, MODULE_NAME, MEMORY etc...)"

	# Check ear name
	if [[ -z ${EAR_NAME} ]] ; then
		echo "Please specify ear name (example : BPC_CIJ_DM_PRES_EAR or BPC_CTS_GESTION_CLIENTS_INT_EAR)"
		exit 110
	fi

	# Set applicative module
	MODULE_NAME=$(awk -F'=' '/MODULE_NAME=/ { print $2 }' ${propsFile})
	if [[ -z ${MODULE_NAME} ]] ; then 
		echo "Please specify applicative module (example : gestionclientsint)"
		missingVariable=110
		exit 110
	fi

	# Set shared libs name
	SHARED_LIB_NAME=${SHARED_NAME}_shared ; export SHARED_LIB_NAME

	# Set jvm min/max memory
	MEMORY_MAX=$(awk -F'=' '/MEMORY_MAX=/ { print $2 }' ${propsFile})
	if [[ -z ${MEMORY_MAX} ]] ; then MEMORY_MAX=128 ; fi
	export MEMORY_MAX
	
	MEMORY_MIN=$(awk -F'=' '/MEMORY_MIN=/ { print $2 }' ${propsFile})
	if [[ -z ${MEMORY_MIN} ]] ; then MEMORY_MIN=64 ; fi
	export MEMORY_MIN

	# Set node server
	SERVER_NODES=$(awk -F'=' '/SERVER_NODES=/ { print $2 }' ${propsFile})
	if [ -z ${SERVER_NODES} ] ; then
		echo "Please specify the node (server) on which to install the application"
		missingVariable=110
		exit 110
	else
		export SERVER_NODES
	fi

	# Set server type ("ST_PREZ" or "ST_BIZ")
	export SERVER_TYPE=$(awk -F'=' '/SERVER_TYPE=/ { print $2 }' ${propsFile})
	if [ ${SERVER_TYPE} == "ST_BIZ" ]
	then 
		export HOST=${DMGR_HOST}
		export SCRIPT_DEPLOY="DeployApp.ksh"
	elif [ ${SERVER_TYPE} == "ST_PREZ" ]
	then
		export HOST="${SERVER_NODES}"
		export SCRIPT_DEPLOY="DeployPres.ksh"
	elif [ "${SERVER_TYPE}" == "" ] ; then
		echo "The type of the server is not specified."
		missingVariable=110
		exit 110
	fi

	# Set classloading
	EAR_CLASSLOADER_MODE=$(awk -F'=' '/CLASSLOADER_EAR.EAR=/ { print $2 }' ${propsFile})
	if [ "${EAR_CLASSLOADER_MODE}" == "" ] ; then  EAR_CLASSLOADER_MODE="PARENT_LAST" ; fi

	WAR_CLASSLOADER_MODE=$(awk -F'=' '/CLASSLOADER_WAR.WAR1=/ { print $2 }' ${propsFile})
	if [ "${WAR_CLASSLOADER_MODE}" == "" ] ; then WAR_CLASSLOADER_MODE="PARENT_FIRST" ; fi

	#WAR_CLASSLOADER_POLICY=$(awk -F'=' '/WAR_CLASSLOADER_POLICY=/ { print $2 }' ${propsFile})
	export WAR_CLASSLOADER_POLICY="SINGLE"

	export EAR_CLASSLOADER_MODE
	export WAR_CLASSLOADER_MODE

	# Set scope deployment (SH etc)
	SCOPE=$(awk -F'=' '/SCOPE=/ { print $2 }' ${propsFile})
	if [[ -z ${SCOPE} ]] ; then export SCOPE=SH ; fi

	# Application directories & deploy script set on the manager server
	echo ""
	echo "==> Creation of application tree"
	if [ ! -d "${SAMPLE_DIR}/${GLOBAL_APP_NAME}" ] 
	then
		# Creation of applicative deployment tree (alias "sam")
		mkdir -m 775 "${SAMPLE_DIR}/${GLOBAL_APP_NAME}"
		mkdir -p "${SAMPLE_DIR}/${GLOBAL_APP_NAME}/jython"
		mkdir -p "${SAMPLE_DIR}/${GLOBAL_APP_NAME}/jacl"
		mkdir -p "${SAMPLE_DIR}/${GLOBAL_APP_NAME}/tmp"
		mkdir -p "${SAMPLE_DIR}/${GLOBAL_APP_NAME}/installableApps/archives"
	else
		echo "WARNING : le dossier \"${SAMPLE_DIR}/${GLOBAL_APP_NAME}\" existe deja."
	fi

	# Copy of deployment script set (DeployPres.ksh or DeployApp.ksh)
	echo ""
	echo "==> Copy of scripts set"
	cp -p ${MODELES_DIR}/Deploy.ksh ${SAMPLE_DIR}/${GLOBAL_APP_NAME}/${SCRIPT_DEPLOY}

	# Copy of application & SA environment variables configuration files (jacl & jython)
	cp -p ${MODELES_DIR}/Deploy.py ${SAMPLE_DIR}/${GLOBAL_APP_NAME}/jython
	cp -p ${MODELES_DIR}/Deploy.jacl ${SAMPLE_DIR}/${GLOBAL_APP_NAME}/jacl
	#cp -p ${COMMON_JACL} ${SAMPLE_DIR}/${GLOBAL_APP_NAME}/jacl
fi


#--------------------------
# Web Server initialization
#--------------------------

# Set web server (ip/urls & ports)
export CREATE_WEB_SERVER=$(awk -F'=' '/CREATE_WEB_SERVER=/ { print $2 }' ${propsFile})
if [[ ${CREATE_WEB_SERVER} == "yes" ]]
then
	export SCOPE=SH

	WEBSERVER_HOST=$(awk -F'=' '/WEBSERVER_HOST=/ { print $2 }' ${propsFile})
	if [[ -z ${WEBSERVER_HOST} ]] ; then
		echo "Please specify the name of the host (or alias url)."
		missingVariable=110
		exit 110
	else
		export WEBSERVER_HOST
	fi

	WEBSERVER_PORT=$(awk -F'=' '/WEBSERVER_PORT=/ { print $2 }' ${propsFile})
	if [[ -z ${WEBSERVER_PORT} ]] ; then
		export WEBSERVER_PORT=8081
	else
		export WEBSERVER_PORT
	fi

	WEBSERVER_PORT_SSL=$(awk -F'=' '/WEBSERVER_PORT_SSL=/ { print $2 }' ${propsFile})
	if [[ -z ${WEBSERVER_PORT_SSL} ]] ; then
		export WEBSERVER_PORT_SSL=9443
	else
		export WEBSERVER_PORT_SSL
	fi
fi


#------------------------------------------------
# Shared librairies & Virtual Host initialization
#------------------------------------------------

# Set shared libraries & virtual host
export CREATE_SHARED_LIBRARIES=$(awk -F'=' '/CREATE_SHARED_LIBRARIES=/ { print $2 }' ${propsFile})
export CREATE_VH=$(awk -F'=' '/CREATE_VH=/ { print $2 }' ${propsFile})


#--------------------------
# Set environment variables 
#--------------------------

echo ""
echo "==> Copy of jython/jacl librairies and variables"
# jython
${SA_CUSTOM_PARAMETERS_JYTHON} > "${SAMPLE_DIR}/${GLOBAL_APP_NAME}/jython/$(basename ${SCRIPT_DEPLOY} .ksh)-variables.py"
${APP_CUSTOM_PARAMETERS_JYTHON} >> "${SAMPLE_DIR}/${GLOBAL_APP_NAME}/jython/$(basename ${SCRIPT_DEPLOY} .ksh)-variables.py"

# jacl
${SA_CUSTOM_PARAMETERS_JACL} > "${SAMPLE_DIR}/${GLOBAL_APP_NAME}/jacl/$(basename ${SCRIPT_DEPLOY} .ksh)-variables.jacl"
${APP_CUSTOM_PARAMETERS_JACL} >> "${SAMPLE_DIR}/${GLOBAL_APP_NAME}/jacl/$(basename ${SCRIPT_DEPLOY} .ksh)-variables.jacl"

#------------------------------
# Creation SA & resources start
#------------------------------

# Init SA creation, connection to the manager
echo ""
echo "==> Try to contact manager, please wait ..."
${DMGR_DIR}/bin/wsadmin.sh -lang jython -profile ${SA_DEFAULT_PARAMETERS} -profile "${SAMPLE_DIR}/${GLOBAL_APP_NAME}/jython/$(basename ${SCRIPT_DEPLOY} .ksh)-variables.py" -f "${PYTHON_DIR}/managesa.py" ${propsFile}
CREATION_SA_RESULT=$?
if [[ ${CREATION_SA_RESULT} -ne 0 ]] ; then
	echo "Problem encountered during Application Server creation !!!"
	echo "End of the script : status ${CREATION_SA_RESULT}"
	${CONFIG_DIR}/unlock.sh
	exit ${CREATION_SA_RESULT}
fi
	
# Resources application management
if [[ ${MANAGE_RESOURCES} == "yes" ]] ; then
	echo ""
	echo "==> Application resources management start..."
	echo ""
	${SCRIPT_ROOT_DIR}/manage_resources.ksh ${propsFile}
	CREATION_SA_RESULT=$?
fi

${CONFIG_DIR}/unlock.sh
	
echo ""
echo "End of the script : status ${CREATION_SA_RESULT}"

