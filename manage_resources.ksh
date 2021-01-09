#!/bin/ksh

#set -x

#----------
# Variables
#----------

if [[ $# -ne 1 ]] ; then
	echo "Please specify a props file. USAGE : $0 props_file_id"
	CREATION_RESOURCES_RESULT=5
	echo ""
	echo "-------------------------------------------------"
	print "code retour ${CREATION_RESOURCES_RESULT} : Missing props file id."
	echo "-------------------------------------------------"
	exit ${CREATION_RESOURCES_RESULT}
fi

if [[ -z ${DMGR_DIR} ]] ; then
	export USER=`whoami`    # Connected user
	case "${USER}" in
        	was7*)          . ${CONFIG_DIR}/userProfiles/was7Profile 2> /dev/null
                        	;;
        	was85*)         . ${CONFIG_DIR}/userProfiles/was85Profile 2> /dev/null
                        	;;
        	was)            . ${CONFIG_DIR}/userProfiles/wasProfile 2> /dev/null
                        	;;
        	*)              echo "Please connect with a WebSphere user. This script must be run on WebSphere 7 version or higher."
                	        exit 1
                        	;;
	esac
fi

if [[ -z "${PYTHON_DIR}" ]] ; then
	export SCRIPT_ROOT_DIR=$(cd -P $(dirname $0); pwd)
	export SCRIPT_LOGS=${SCRIPT_ROOT_DIR}/logs
	export PYTHON_DIR=${SCRIPT_ROOT_DIR}/python
	export PYTHON_LIBRARY=${PYTHON_DIR}/functions.py
	export LIVRAISONS_DIR=${SCRIPT_ROOT_DIR}/livraisons
fi

propsFile=$1

if [[ ${propsFile%${propsFile#?}} != "/" ]] ; then
	propsFile=${LIVRAISONS_DIR}/$1.props
fi

${DMGR_DIR}/bin/wsadmin.sh -lang jython -f ${PYTHON_DIR}/analyseProps.py ${propsFile}                 # Resources management (creation/update/deletion)
CREATION_RESOURCES_RESULT="$?"

case "${CREATION_RESOURCES_RESULT}" in
	0)      echo ""
                echo "-----------------------------------------------------------------------------"
                echo "End of creation of resources : code retour ${CREATION_RESOURCES_RESULT} : OK"
                echo "-----------------------------------------------------------------------------"
                ;;
        2)      echo ""
                echo "---------------------------------------------"
                print "code retour {CREATION_RESOURCES_RESULT} : SA does not exist."
                echo "---------------------------------------------"
                exit 2
                ;;
        3)      echo ""
                echo "-------------------------------------------------------------------------"
                print "code retour ${CREATION_RESOURCES_RESULT} : Problem with on the resources."
                echo "-------------------------------------------------------------------------"
                exit 3
                ;;
        10)     echo ""
                echo "-------------------------------------------------------------------------"
                print "code retour ${CREATION_RESOURCES_RESULT} : Problem during node synchronization."
                echo "-------------------------------------------------------------------------"
                exit 10
                ;;
        *)      echo ""
                echo "-------------------------------------------------"
                print "code retour ${CREATION_RESOURCES_RESULT} : Other problem."
                echo "-------------------------------------------------"
                exit 105
                ;;
esac

