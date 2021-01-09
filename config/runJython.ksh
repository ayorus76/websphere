#!/bin/ksh

export LC_ALL=en_US

ADM_CONFIG=`dirname $0`                                 # "${HOME}/bin/managesa/config" folder
LOCK_FILE=$ADM_CONFIG/config.lock

#-------------
# Script usage
#-------------

if (( $# != 3 && $# != 4 ))
then
        echo "USAGE : `basename $0` <pid> <deployScript> <customFile> [true|false] "
        exit 1
fi

currentPid=$1
deployScript=${PYTHON_DIR}/$2.py			# Script : Deploy.py
stdProfileFile=$ADM_CONFIG/standard.py
appCustomFile=$3.py					# Application custom file : DeployPres-variables.py or DeployApp-variables.py
profileCustomFile="true"


#----------------------
# Custom file existence
#----------------------

if [ ! -f $appCustomFile ] ; then
        echo "ERROR : file $appCustomFile does not exist !"
        exit 1
fi


#----------------
# Lock activation
#----------------

if [ -f $LOCK_FILE ]
then
        lockedBefore="true"
        pidLock=`cat $LOCK_FILE`

        if [[ "$pidLock" != "$currentPid" ]]; then
                echo "Config locked by $pidLock. Try later."
                exit 1
        fi
else
        lockedBefore="false"
        echo $currentPid > $LOCK_FILE
fi


#---------------------------------------------
# Deployment command preparation and execution
#---------------------------------------------

#$DMGR_HOME/bin/wsadmin.sh -javaoption "-Dpython.path=$libPath" -lang jython $cmd

#cmd="$DMGR_DIR/bin/wsadmin.sh -lang jyhon -profile $stdProfileFile"
#cmd="$cmd -profile $appCustomFile"

cmd="$DMGR_DIR/bin/wsadmin.sh -lang jython -profile $appCustomFile"
cmd="$cmd -f $deployScript $ADM_CONFIG"

$cmd    # Script call

RESULT=$?


#-------------
# Lock release
#-------------

if [[ "$lockedBefore" = "false" ]]; then
        rm $LOCK_FILE
fi

if (( $RESULT != 0 )); then
        exit $RESULT
fi

