#!/bin/bash

artifactoryRegistry=
repositoryName=

destinationRepositoryName=
specificTag=
destinationUserName=
noUpdate=false
forceUpdate=false
localPrefix=

[ -x ~/.jfrog/docker.rc ] && . ~/.jfrog/docker.rc

help(){
    cat <<EOF
    Copy docker.io image(s) into a local artifactory repository

    Usage: $(basename $0) <opts> remote tag artifactory
    Where:
        repository = Docker repository to localize
        tag        = Specific repository tag to localize
        artifactory= Local docker registry
        These can also be specified with option switches
    Opts:
        -a --artifactory    Local docker registry               required
        -r --remote         Remote image name on docker.io      required
        -p --prefix         Prefix to add to local repository   ${localPrefix:+defaults to: $localPrefix}
        -l --local          Local image name                    defaults to: remote image name with prefix
        -t --tag            Specific tag to localize            defaults to: all tags for that image
        -n --noupdate       Don\'t update the local artifactory defaults to: false
        -f --force          Force the update to overwrite       defaults to: false
EOF
}

parse(){


    local PARM=$(getopt -o a:r:l:t:nfhn0 \
        --long 'artifactory','remote','local','tag','noupdate','force','help','name','prefix' \
        -n "$(basename $0)" -- "$@" )

    if [ $? != 0 ]; then help; exit 1; fi

    eval set -- "$PARM"

    while true; do
        case "$1" in
            -a|--artifactory) artifactoryRegistry=$2; shift 2 ;;
            -r|--remote) repositoryName=$2; shift 2 ;;
            -l|--local) destinationRepositoryName=$2; shift 2 ;;
            -t|--tag) specificTag=$2; shift 2 ;;
            -n|--noupdate) noUpdate=true; shift ;;
            -f|--force) forceUpdate=true; shift ;;
            -h|--help) help ; exit 0 ;;
            -p|--prefix) localPrefix=$2; shift 2 ;;
            --) shift ; break ;;
            *) echo "Internal Error!"; exit 1;;
        esac
     done

     repositoryName=${1:-$repositoryName}
     specificTag=${2:-$specificTag}
     artifactoryRegistry=${3:-$artifactoryRegistry}

     if [ "$artifactoryRegistry" == "" ]; then echo "local artifactory fqdn must not be null"; help; exit 1; fi
     if [ "$repositoryName" == ""      ]; then echo "remote image name must not be null"; help; exit 1; fi

     destinationRepositoryName=${destinationRepositoryName:-${localPrefix}${repositoryName}}

     echo Duplicating $repositoryName into $artifactoryRegistry/$destinationRepositoryName
}

pullImages() {
    echo "INFO: Pulling needed images from destination repository $artifactoryRegistry"
    if [ -n "$specificTag" ]; then
        docker pull ${artifactoryRegistry}/${destinationRepositoryName}:${specificTag} || \
        echo "INFO: $destinationRepositoryName:$specificTag does not exists in destination $artifactoryRegistry"
    else
        docker pull ${artifactoryRegistry}/${destinationRepositoryName} || \
        echo "INFO: $destinationRepositoryName does not exists in destination $artifactoryRegistry"
    fi
    echo "INFO: Pulling needed images from source repository"
    if [ -n "$specificTag" ]; then
        docker pull ${repositoryName}:${specificTag} || (echo "ERROR: Failed to pull $repositoryName:$specificTag" && return 1)
    else
        docker pull --all-tags ${repositoryName} || (echo "ERROR: Failed to pull $repositoryName" && return 2)
    fi
    return 0
}

pushOneImage() {
    local tagName="$1"
    [ -z "$tagName" ] && (echo "ERROR: did not provide tag name" && return 1)
    local imageId=$(docker images ${repositoryName} | awk -v rn=${repositoryName} -v tn=${tagName} '($1 == rn) && ($2 == tn) { print $3 }')
    if [ -z "$imageId" ]; then
        echo "ERROR: Could not find image with repository ${repositoryName} and tag $tagName"
        return 2
    else
        echo "INFO: Found image $imageId for ${repositoryName}:$tagName"
    fi
        
    # Check if image already exists in destination
    local forceTag=""
    local localImageId=$(docker images ${artifactoryRegistry}/${destinationRepositoryName} | awk -v tn=$tagName '$2 == tn { print $3 }')
    if [ -z "$localImageId" ]; then
        echo "INFO: Destination does not contain ${destinationRepositoryName}:${tagName}"
    else
        echo "INFO: Destination contain ${destinationRepositoryName}:${tagName} with id ${localImageId}"
        if ${noUpdate}; then
            echo "INFO: Skipping image update since no-update flag is set"
            return 0
        fi
        if ${forceUpdate}; then
            forceTag="--force=true"
        fi
    fi
    echo "INFO: Pushing $imageId ${repositoryName}:${tagName} into ${artifactoryRegistry}/${destinationRepositoryName}:${tagName}"
    docker tag ${forceTag} ${imageId} ${artifactoryRegistry}/${destinationRepositoryName}:${tagName} && \
    docker push ${artifactoryRegistry}/${destinationRepositoryName}:${tagName}
}

pullAndUpAllImages() {
    if [ -n "$specificTag" ]; then
        echo "INFO: Pushing tag $specificTag"
        pushOneImage "$specificTag"
        return $?
    else
        echo "INFO: Pushing all tags of $repositoryName"
        for tag in $(docker images ${repositoryName} | awk -v rn=${repositoryName} '$1 == rn { print $2 }'); do
            echo "INFO: Pushing tag $tag"
            pushOneImage "$tag" || return $?
        done
    fi
}

 parse "$@" && \
 pullImages && \
 pullAndUpAllImages
 
