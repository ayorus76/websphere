#!/bin/ksh

# Root script & logs folders
export SCRIPT_ROOT_DIR=$(cd -P $(dirname $0); pwd)
export SCRIPT_LOGS=${SCRIPT_ROOT_DIR}/logs

export CONFIG_DIR=${SCRIPT_ROOT_DIR}/config
export MODELES_DIR=${SCRIPT_ROOT_DIR}/modeles
export LIVRAISONS_DIR="${SCRIPT_ROOT_DIR}/livraisons"	# Props files folder
if [ ! -d ${LIVRAISONS_DIR} ] ; then mkdir -m755 "${SCRIPT_ROOT_DIR}/livraisons" ; fi

# Python libraries & functions
export PYTHON_DIR=${SCRIPT_ROOT_DIR}/python
export PYTHON_LIBRARY=${PYTHON_DIR}/functions.py

#------------------------------------
# User profile & environment settings
#------------------------------------

export USER=`whoami`

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

#----------------------------------
# Generation of a figure (5 digits)
#----------------------------------

ECHELLE=99999
PLANCHER=11111
NOMBRE=0   
while [ "${NOMBRE}" -le ${PLANCHER} ]
do
  NOMBRE=$RANDOM
  let "NOMBRE %= ${ECHELLE}"  
done

export propsFile="${LIVRAISONS_DIR}/${NOMBRE}.props"

#--------------
# Props content
#--------------

echo "SA name (example : sa_scn-servtransint_biz-01) ? : " ; read SA_NAME

exec 3> ${propsFile} # Data written in new props file
print -u3 "APPLICATION="
print -u3 "APPLICATION_SERVER="
print -u3 "CLASSLOADER_EAR.EAR="
print -u3 "CLASSLOADER_WAR.WAR1="
print -u3 "CODE_AP="
print -u3 "CONF_KEY="
print -u3 "CONF_NAME="
print -u3 "CREATE_SA=no"
print -u3 "CREATE_WEB_SERVER=no"
print -u3 "CREATE_SHARED_LIBRARIES=no"
print -u3 "CREATE_VH=no"
print -u3 "CUSTOM_PROPERTY_WAS_CONTAINER.conteneur="
print -u3 "CUSTOM_PROPERTY_WAS_JVM.jvm="
print -u3 "DELIVERY_AUTHOR_UID="
print -u3 "DELIVERY_DATE="
print -u3 "DELIVERY_DEMAND="
print -u3 "DMGR_HOST="
print -u3 "EAR_NAME="
print -u3 "EDITO=false"
print -u3 "ENVIRONMENT="
print -u3 "GENERIC_ARGUMENT="
print -u3 "HTTPS=false"
print -u3 "MANAGE_RESOURCES=yes"
print -u3 "MEMORY_MAX="
print -u3 "MEMORY_MIN="
print -u3 "MODULE_NAME="
print -u3 "PENTAGRAM="
print -u3 "REDIRECTION_HTTPS="
print -u3 "SA_TRIG_NAME_TYPE=${SA_NAME}"
print -u3 "SERVER="
print -u3 "SERVER_NODES="
print -u3 "SERVER_TYPE="
print -u3 "TEST_LOGIN="
print -u3 "TEST_PWD="
print -u3 "TEST_URL="
print -u3 "TRIGRAM="
print -u3 "WEBSERVER_HOST="
print -u3 "WEBSERVER_PORT="
print -u3 "WEBSERVER_PORT_SSL="
print -u3 "WIS_AUTHOR_UID="
print -u3 "WIS_DATE="
print -u3 "WIS_ID="
print -u3 "XCALIA=false"
print -u3 ""

exec 3>&-

echo "Connexion to manager server and resources information collect ..."
${DMGR_DIR}/bin/wsadmin.sh -lang jython -f ${PYTHON_DIR}/configAppli.py ${SA_NAME} | awk '$0 ~ /^WAS/ { next } ; { print }' >> ${propsFile}

echo "Props file props generated : " ${propsFile}
exit 0

