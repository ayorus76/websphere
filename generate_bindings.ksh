#!/bin/ksh

#----------
# Variables
#----------

export USER=`whoami`	# Connected user

# Root script & logs folders
export SCRIPT_ROOT_DIR=$(cd -P $(dirname $0); pwd)
export SCRIPT_LOGS=${SCRIPT_ROOT_DIR}/logs                                                                                

export CONFIG_DIR=${SCRIPT_ROOT_DIR}/config
export MODELES_DIR=${SCRIPT_ROOT_DIR}/modeles

# Python libraries & functions
export PYTHON_DIR=${SCRIPT_ROOT_DIR}/python
export PYTHON_LIBRARY=${PYTHON_DIR}/functions.py

export LIVRAISONS_DIR=${SCRIPT_ROOT_DIR}/livraisons	# Props files folder


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

#chmod -R 755 ${SCRIPT_ROOT_DIR}


#-------------
# Prerequisite
#-------------

f_Usage()
{
        echo "This script needs an argument (props file id) : $0 12345"
        echo ""
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


#--------------------
# Props file ID check
#--------------------

export propsFile=${LIVRAISONS_DIR}/$1.props


#----------------------------------------------
# SA : name, code AP, pentagram, scripts folder
#----------------------------------------------

export SA_NAME=$(awk -F'=' '/SA_TRIG_NAME_TYPE=/ { print $2 }' ${propsFile})
export DMGR_HOST=$(hostname)
export BINDINGS=${SCRIPT_ROOT_DIR}/${SA_NAME}-bindings.txt
export BINDINGS_TMP=${SCRIPT_ROOT_DIR}/${SA_NAME}-bindings-tmp.txt


#-------------------------
# Check resources bindings
#-------------------------

# Init SA resources collect, connection to the manager
echo ""
echo "==> Try to contact manager, please wait ..."
${DMGR_DIR}/bin/wsadmin.sh -lang jython -f "${PYTHON_DIR}/bindings.py" ${SA_NAME} > ${BINDINGS_TMP}
CREATION_SA_RESULT=$?
if [[ ${CREATION_SA_RESULT} -ne 0 ]] ; then
	echo "Problem encountered during resources binding check !!!"
	echo "End of the script : status ${CREATION_SA_RESULT}"
	${CONFIG_DIR}/unlock.sh
	exit ${CREATION_SA_RESULT}
fi

grep -v '^WAS' ${BINDINGS_TMP} > ${BINDINGS}	
rm "${BINDINGS_TMP}"

${CONFIG_DIR}/unlock.sh
	
echo ""
echo "End of the script : status ${CREATION_SA_RESULT}"
if [ -s ${BINDINGS} ] 
then
	echo "Generation of resources bindings file : ${BINDINGS}"
else
	echo "ERROR : bindings file not generated !!!"
fi

