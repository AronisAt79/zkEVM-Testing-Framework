#!/bin/bash
set -x

USER=$(whoami)
ENV_FILE_NAME="environment.json"
WORKING_DIR_NAME=$(basename $(pwd))
NETWORK_ID=$1
CHAIN_ID=$2
PARAMS="/tmp/params"

if [ ! $WORKING_DIR_NAME = "brownie" ]; then
    echo "Run this script from the brownie directory"
    exit 1
fi

if [ $# -ne 2 ]; then
    echo "Usage: $0 <K8|TESTNET|REPLICA|TA> <99>"
    exit 1
fi

install_pkgs() {
    sudo apt-get update
    sudo apt-get install jq python3.10-venv python3-pip -y 
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
}

install_brownie() {
    /home/$USER/.local/bin/pipx install eth-brownie
    /home/$USER/.local/bin/pipx inject eth-brownie pandas
    source ~/.profile
}

add_network() {
    URL=$(jq .rpcUrls.${NETWORK_ID}_BASE $ENV_FILE_NAME | sed 's/$/l2/ ; s/"//g')
    brownie networks add zkevm-chain ${NETWORK_ID}_BASE host=$URL chainid=$CHAIN_ID
}

run_brownie () {
    brownie compile
    brownie run scripts/deploy.py --network ${NETWORK_ID}_BASE
}

run_brownie_test () {
    echo $PATH | grep '/.local/bin'
    if [ $? -ne 0 ]; then
        source ~/.profile
    fi
    if [ $NETWORK_ID = "TA" ]; then
        if [ -f $PARAMS ]; then
            brownie run scripts/globals.py main `cat $PARAMS` --network ${NETWORK_ID}_BASE
            rm $PARAMS
        else
            brownie run scripts/globals.py main --network ${NETWORK_ID}_BASE
        fi
    else
        brownie run scripts/globals.py --network ${NETWORK_ID}_BASE
    fi
}

main() {
    BROWNIE_EXISTS="/home/$USER/.local/bin/brownie"
    if [ ! -f $BROWNIE_EXISTS ]; then
        install_pkgs
        install_brownie
        add_network
        run_brownie
        run_brownie_test
    else
        run_brownie_test
    fi
}

main
    
exit 0
