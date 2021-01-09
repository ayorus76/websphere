#!/bin/sh

export DATE=$(date +"%d%m%y")

export MANAGESA_DIR=${HOME}/bin/managesa					# Example : /home/was7/bin/managesa
export MANAGESA_CONF_DIR=${MANAGESA_DIR}/config					# Example : /home/was7/bin/managesa/config
export SCRIPT_ROOT_DIR=$(cd -P $(dirname $0); pwd)				# Example : /applix/WA/PAWAS01I/config/samples_assurance/tst-test0

RUNCMD_JYTHON=${MANAGESA_CONF_DIR}/runJython.ksh
RUNCMD_JACL=${MANAGESA_CONF_DIR}/run.sh

export PYTHON_DIR=${SCRIPT_ROOT_DIR}/jython
export JACL_DIR=${SCRIPT_ROOT_DIR}/jacl

#------------
# Logs & lock
#------------

LOG_DEPLOY="${SCRIPT_ROOT_DIR}/tmp/$(basename $0 .ksh).log"			# Example : /applix/WA/PAWAS01I/config/samples_assurance/tst-test0/tmp/DeployPres.log

echo "log file : $LOG_DEPLOY"

echo "" > $LOG_DEPLOY
if (( $? != 0 )); then
  echo "Unable to write to $LOG_DEPLOY"
  exit 9
fi

${MANAGESA_CONF_DIR}/lock.sh $$
if (( $? != 0 )); then
  echo "Unable to get lock " >> $LOG_DEPLOY
  exit 10
fi


#-----------------
# runJacl function
#-----------------

runJacl() {
 echo "Running : $1 $2" >> $LOG_FILE
 echo "Running : $1 $2 ..."
 $RUNCMD_JACL $$ $1 ${JACL_DIR}/$2 >> $LOG_FILE
 if (( $? != 0 ))
 then
   echo "*** ERROR when executing $1 $2" >> $LOG_FILE
   echo "*** ERROR : see $LOG_FILE"
   if (( $3 != 1 ))
   then
     ${MANAGESA_CONF_DIR}/unlock.sh
     exit 1
   fi
 else
   echo "$1 $2 -> OK" >> $LOG_FILE
   echo "$1 $2 -> OK"
 fi
}


#-------------------
# runJython function
#-------------------

runJython() {
 echo "Running : $1 $2" >> $LOG_FILE
 echo "Running : $1 $2 ..."
 $RUNCMD_JYTHON $$ $1 ${PYTHON_DIR}/$2 >> $LOG_FILE
 if (( $? != 0 ))
 then
   echo "*** ERROR when executing $1 $2" >> $LOG_FILE
   echo "*** ERROR : see $LOG_FILE"
   if (( $3 != 1 ))
   then
     ${MANAGESA_CONF_DIR}/unlock.sh
     exit 1
   fi
 else
   echo "$1 $2 -> OK" >> $LOG_FILE
   echo "$1 $2 -> OK"
 fi
}


#------------------
# Deployment launch
#------------------

#runJython Deploy $(basename $0 .ksh)-variables 0
runJacl Deploy $(basename $0 .ksh)-variables 0

#-------
# Unlock
#-------

${MANAGESA_CONF_DIR}/unlock.sh

#----------------------
# Nodes synchronization
#----------------------

echo "Synchronizing nodes..."
${MANAGESA_CONF_DIR}/fullSync.sh >> $LOG_DEPLOY
if (( $? != 0 )); then
  echo "*** ERROR when synchronizing nodes, see $LOG_DEPLOY"
  exit 1
fi
echo "Synchronization complete" >> $LOG_DEPLOY
echo "Synchronization complete"

