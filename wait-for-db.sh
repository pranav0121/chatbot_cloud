#!/bin/bash
# Wait-for-it script for database readiness
# Usage: ./wait-for-db.sh host:port [timeout] -- command

set -e

HOST=""
PORT=""
TIMEOUT=15
QUIET=0

usage() {
    echo "Usage:"
    echo "  wait-for-db.sh host:port [-t timeout] [-- command args]"
    echo "  -h HOST | --host=HOST       Host or IP under test"
    echo "  -p PORT | --port=PORT       TCP port under test"
    echo "  -t TIMEOUT | --timeout=TIMEOUT"
    echo "                              Timeout in seconds, zero for no timeout"
    echo "  -q | --quiet                Don't output any status messages"
    echo "  -- COMMAND ARGS             Execute command with args after the test finishes"
}

wait_for() {
    if [[ $TIMEOUT -gt 0 ]]; then
        echo "Waiting $TIMEOUT seconds for $HOST:$PORT"
    else
        echo "Waiting for $HOST:$PORT without a timeout"
    fi
    
    start_ts=$(date +%s)
    while :
    do
        if [[ $TIMEOUT -gt 0 ]]; then
            result=$(timeout 1 bash -c "</dev/tcp/$HOST/$PORT" 2>/dev/null && echo "open" || echo "closed")
        else
            result=$(bash -c "</dev/tcp/$HOST/$PORT" 2>/dev/null && echo "open" || echo "closed")
        fi
        
        if [[ "$result" == "open" ]]; then
            end_ts=$(date +%s)
            echo "$HOST:$PORT is available after $((end_ts - start_ts)) seconds"
            break
        fi
        
        if [[ $TIMEOUT -gt 0 ]]; then
            end_ts=$(date +%s)
            if [[ $((end_ts - start_ts)) -ge $TIMEOUT ]]; then
                echo "Operation timed out" >&2
                exit 1
            fi
        fi
        
        sleep 1
    done
}

wait_for_db_ready() {
    echo "Testing database connectivity to $HOST:$PORT"
    
    # Test MSSQL specifically
    python3 -c "
import pyodbc
import time
import sys

def test_connection():
    drivers = ['ODBC Driver 17 for SQL Server', 'ODBC Driver 13 for SQL Server', 'SQL Server']
    
    for driver in drivers:
        try:
            conn_str = f'DRIVER={{{driver}}};SERVER=$HOST,$PORT;DATABASE=master;UID=sa;PWD=\$DB_PASSWORD;'
            conn = pyodbc.connect(conn_str, timeout=5)
            conn.close()
            print(f'Successfully connected to MSSQL using {driver}')
            return True
        except Exception as e:
            print(f'Failed to connect with {driver}: {e}')
            continue
    return False

max_attempts = ${TIMEOUT:-30}
for attempt in range(1, max_attempts + 1):
    print(f'Database connection attempt {attempt}/{max_attempts}')
    if test_connection():
        print('Database is ready!')
        sys.exit(0)
    time.sleep(1)

print('Database connection failed after all attempts')
sys.exit(1)
    " || exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]
do
    case $1 in
        *:* )
        HOST=$(printf "%s\n" "$1"| cut -d : -f 1)
        PORT=$(printf "%s\n" "$1"| cut -d : -f 2)
        shift 1
        ;;
        -q | --quiet)
        QUIET=1
        shift 1
        ;;
        -t)
        TIMEOUT="$2"
        if [[ $TIMEOUT == "" ]]; then break; fi
        shift 2
        ;;
        --timeout=*)
        TIMEOUT="${1#*=}"
        shift 1
        ;;
        -h)
        HOST="$2"
        if [[ $HOST == "" ]]; then break; fi
        shift 2
        ;;
        --host=*)
        HOST="${1#*=}"
        shift 1
        ;;
        -p)
        PORT="$2"
        if [[ $PORT == "" ]]; then break; fi
        shift 2
        ;;
        --port=*)
        PORT="${1#*=}"
        shift 1
        ;;
        --)
        shift
        break
        ;;
        --help)
        usage
        exit 0
        ;;
        *)
        echo "Unknown argument: $1"
        usage
        exit 1
        ;;
    esac
done

if [[ "$HOST" == "" || "$PORT" == "" ]]; then
    echo "Error: you need to provide a host and port to test."
    usage
    exit 1
fi

# Wait for port to be open
wait_for

# Additionally test database readiness for MSSQL
if [[ "$PORT" == "1433" ]]; then
    wait_for_db_ready
fi

# Execute command if provided
if [[ $# -gt 0 ]]; then
    exec "$@"
fi
