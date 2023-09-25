#!/bin/bash

case $1 in -[h?] | --help)
    script= $(basename $0)
    echo "
        Usage: $script 
            needs to be run inside of './docker/' folder
            
            [ --help ] Outputs this help message.
        "
    exit 0;;
esac

CURDIR=`pwd`
if [[ "$(echo $CURDIR | awk -F / '{print $NF}')" != "docker" ]]; then
    printf '%s\n' "must be in ./docker/ folder" >&2
    exit 1
fi

{
    cd ..
    {
        CLONECMD="git clone https://$1@github.com/revenue-solutions-inc/DataScienceTools.git DST"
        eval $CLONECMD
        rm -rf DataScienceTools
        rsync -av --exclude=.git --exclude=dockerutils --exclude=example_run DST/ DataScienceTools
        rm -rf DST

    } || {
        if [[ ! -d DataScienceTools ]]; then
            printf '%s\n' "could not clone DataScienceTools repository" >&2
            exit 1
        fi
    }
    # cd DataScienceTools && rm -rf `find . -name dockerutils` && rm -rf `find . -name example_run` && rm -rf `find . -name .git`

} || {
    printf '%s\n%s\n%s\n' "error encountered finding DataScienceTools repo or in copying process - please run this in FormsProcessing/ML, with DataScienceTools repo (with the exact folder name) and located in the same directory as FormsProcessing" >&2
    exit 1    
}
cd $CURDIR
