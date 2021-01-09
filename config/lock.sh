ADM_CONFIG=`dirname $0`
LOCK_FILE=$ADM_CONFIG/config.lock


if [ $# -ne 1 ]
then
        echo "USAGE : `basename $0` <pid>"
        exit 1
fi


if test -f $LOCK_FILE
then
# on verifie si le process qui a pris le verrou est toujours en cours d'execution
  pidLock=`cat $LOCK_FILE`
  if (( `ps -p${pidLock} | wc -l` != 1 )); then
    echo "Config locked by `cat $LOCK_FILE`. Try later."
    exit 1
  fi
fi

echo $1 > $LOCK_FILE
