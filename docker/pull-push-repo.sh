#!/bin/bash

registry=
name=

destination=
tag=
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
            -a|--artifactory) registry=$2; shift 2 ;;
            -r|--remote) name=$2; shift 2 ;;
            -l|--local) destination=$2; shift 2 ;;
            -t|--tag) tag=$2; shift 2 ;;
            -n|--noupdate) noUpdate=true; shift ;;
            -f|--force) forceUpdate=true; shift ;;
            -h|--help) help ; exit 0 ;;
            -p|--prefix) localPrefix=$2; shift 2 ;;
            --) shift ; break ;;
            *) echo "Internal Error!"; exit 1;;
        esac
     done

     name=${1:-$name}
     tag=${2:-$tag}
     registry=${3:-$registry}

     if [ "$registry" == "" ]; then echo "local artifactory fqdn must not be null"; help; exit 1; fi
     if [ "$name" == ""     ]; then echo "remote image name must not be null"; help; exit 1; fi

     destination=${destination:-${localPrefix}${name}}

     echo Duplicating $name into $registry/$destination
}

pullImages() {
    echo "INFO: Pulling needed images from destination repository $registry"
    if [ -n "$tag" ]; then
        docker pull ${registry}/${destination}:${tag} || \
        echo "INFO: $destination:$tag does not exists in destination $registry"
    else
        docker pull ${registry}/${destination} || \
        echo "INFO: $destination does not exists in destination $registry"
    fi
    echo "INFO: Pulling needed images from source repository"
    if [ -n "$tag" ]; then
        docker pull ${name}:${tag} || (echo "ERROR: Failed to pull $name:$tag" && return 1)
    else
        docker pull --all-tags ${name} || (echo "ERROR: Failed to pull $name" && return 2)
    fi
    return 0
}

pushOneImage() {
    local tagName="$1"
    [ -z "$tagName" ] && (echo "ERROR: did not provide tag name" && return 1)
    local imageId=$(docker images ${name} | awk -v rn=${name} -v tn=${tagName} '($1 == rn) && ($2 == tn) { print $3 }')
    if [ -z "$imageId" ]; then
        echo "ERROR: Could not find image with repository ${name} and tag $tagName"
        return 2
    else
        echo "INFO: Found image $imageId for ${name}:$tagName"
    fi
        
    # Check if image already exists in destination
    local forceTag=""
    local localImageId=$(docker images ${registry}/${destination} | awk -v tn=$tagName '$2 == tn { print $3 }')
    if [ -z "$localImageId" ]; then
        echo "INFO: Destination does not contain ${destination}:${tagName}"
    else
        echo "INFO: Destination contain ${destination}:${tagName} with id ${localImageId}"
        if ${noUpdate}; then
            echo "INFO: Skipping image update since no-update flag is set"
            return 0
        fi
        if ${forceUpdate}; then
            forceTag="--force=true"
        fi
    fi
    echo "INFO: Pushing $imageId ${name}:${tagName} into ${registry}/${destination}:${tagName}"
    docker tag ${forceTag} ${imageId} ${registry}/${destination}:${tagName} && \
    docker push ${registry}/${destination}:${tagName}
}

pullAndUpAllImages() {
    if [ -n "$tag" ]; then
        echo "INFO: Pushing tag $tag"
        pushOneImage "$tag"
        return $?
    else
        echo "INFO: Pushing all tags of $name"
        for tag in $(docker images ${name} | awk -v rn=${name} '$1 == rn { print $2 }'); do
            echo "INFO: Pushing tag $tag"
            pushOneImage "$tag" || return $?
        done
    fi
}

 parse "$@" && \
 pullImages && \
 pullAndUpAllImages
 
