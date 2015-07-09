#!/bin/bash

registry=
name=fedora

destination=
tag=
destinationUserName=
noUpdate=false
forceUpdate=false
localRepoName=
prefix=my
flavor=
artifactoryRoot=
ubuntuUrl=
centosUrl=
fedoraUrl=
debianUrl=
suseUrl=


[ -x ~/.jfrog/docker.rc ] && . ~/.jfrog/docker.rc


help(){
    cat <<EOF
    Localize a docker repository to use a local artifactory.
    It will detect the flavor of linux and configure the package manager to use the local repository

    Usage: $(basename $0) <opts> remote tag artifactory install
    Where:
        remote     = Docker repository to localize
        tag        = Specific repository tag to localize
        artifactory= Local docker registry
        install    = URL of local repository
        These can also be specified with option switches
    Opts:
        -a --artifactory    Local docker registry               required
        -r --remote         Remote image name on docker.io      required
        -p --prefix         Prefix to add to local repository   defaults to: $prefix
        -l --local          Local image name                    defaults to: remote image name with prefix
        -t --tag            Specific tag to localize            defaults to: all tags for that image
        -i --install        URL of local package repository     no default
        -n --noupdate       Don\'t update the local artifactory defaults to: false
        -f --force          Force the update to overwrite       defaults to: false
EOF
}

parse(){
    local PARM=$(getopt -o a:r:l:t:i:nfhnp:c \
        --long 'artifactory','remote','local','tag','install','noupdate','force','help','name','prefix','nocache' \
        -n "$(basename $0)" -- "$@" )

    if [ $? != 0 ]; then help; exit 1; fi

    eval set -- "$PARM"

    while true; do
        case "$1" in
            -a|--artifactory) registry=$2; shift 2 ;;
            -r|--remote) name=$2; shift 2 ;;
            -p|--prefix) prefix=$2; shift 2 ;;
            -l|--local) destination=$2; shift 2 ;;
    	    -i|--install) artifactoryRoot=$2; shift 2 ;;
            -t|--tag) tag=$2; shift 2 ;;
            -n|--noupdate) noUpdate=true; shift ;;
            -f|--force) forceUpdate=true; shift ;;
	    -c|--nocache) noCache="--no-cache=true"; shift ;;
            -h|--help) help ; exit 0 ;;
            --) shift ; break ;;
            *) echo "Internal Error!"; exit 1;;
        esac
     done

     name=${1:-$name}
     tag=${2:-$tag}
     registry=${3:-$registry}
     artifactoryRoot=${4:-$artifactoryRoot}
     ubuntuUrl=${ubuntuUrl:-${artifactoryRoot}/ubuntu}
     centosUrl=${centosUrl:-${artifactoryRoot}/centos}
     fedoraUrl=${fedoraUrl:-${artifactoryRoot}/fedora}
     debianUrl=${debianUrl:-${artifactoryRoot}/debian}
     suseUrl=${suseUrl:-${artifactoryRoot}/suse}

     if [ "$registry"        == "" ]; then echo "local artifactory fqdn must not be null"; help; exit 1; fi
     if [ "$name"            == "" ]; then echo "remote image name must not be null"; help; exit 1; fi
     if [ "$artifactoryRoot" == "" ]; then echo "package repository base URL must not be null"; help; exit 1; fi

     destination=${destination:-${prefix}${name}}

     echo Localizing $registry/$name${tag:+:}${tag} into $registry/$destination${tag:+:}${tag}
}

whichFlavor(){
    local image="$1"
    local container="tmp.$$"
    local release=""
    if  release=$(docker run --rm $image cat /etc/os-release 2>/dev/null || \
                   docker run --rm $image cat /etc/redhat-release 2>/dev/null ); then
        release=$(echo $release | tr A-Z a-z)
        flavor=$( ( [[ $release == *ubuntu* ]] && echo "ubuntu" ) || \
                  ( [[ $release == *debian* ]] && echo "debian" ) || \
                  ( [[ $release == *centos* ]] && echo "centos" ) || \
                  ( [[ $release == *fedora* ]] && echo "fedora" ) )
    elif release=$(docker run --rm $image cat /etc/SuSE-brand 2>/dev/null); then
        flavor="suse"
    fi
}

build_and_tag(){
    for s in ~/.jfrog/docker.rc.d/$flavor*.sh; do
        [ -x $s ] && . $s
    done
    docker build $noCache --force-rm=true --rm=true --tag=$registry/$destination${tag:+:}${tag} work
    docker push $registry/$destination${tag:+:}${tag}
    rm -rf work
}

localize-centos(){
    local repo=$1
    local tag=$2
    local hash=$3

    mkdir work
    cat >work/Dockerfile <<EOF
FROM $registry/$name:$tag
MAINTAINER jayd@jfrog.com

RUN sed -i "\
    /^mirror/ s/^/#/; \
    s/^#base/base/; \
    /baseurl/ s%http.://mirror.centos.org/centos%$centosUrl%; \
    s%file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS%$centosUrl/RPM-GPG-KEY-CentOS%; \
    " /etc/yum.repos.d/*.repo
CMD "/bin/bash"

EOF

    build_and_tag

}

localize-fedora(){
    local repo=$1
    local tag=$2
    local hash=$3

    mkdir -p work/{etc/yum.repos.d,tmp}

    curl $artifactoryRoot/rpm-local/develop.repo -o work/etc/yum.repos.d/develop.repo
    sed -i '/enabled/ d;$ ienabled=0' work/etc/yum.repos.d/develop.repo
    curl $artifactoryRoot/rpm-local/release.repo -o work/etc/yum.repos.d/release.repo
    sed -i '/enabled/ d;$ ienabled=1' work/etc/yum.repos.d/release.repo

    cat >work/Dockerfile <<EOF
FROM $repo:$tag
MAINTAINER jayd@jfrog.com
RUN sed -i "\
    /^\(mirror\|meta\)/ s/^/#/; \
    s/^#base/base/; \
    /baseurl/ s%https*://download.fedoraproject.org/pub%$fedoraUrl%; \
    " /etc/yum.repos.d/*.repo
COPY etc /etc

CMD "/bin/bash"

EOF

    build_and_tag

}

localize-ubuntu(){
    local repo=$1
    local tag=$2
    local hash=$3

    mkdir -p work

    cat >work/Dockerfile <<EOF
FROM $repo:$tag
MAINTAINER jayd@jfrog.com
RUN sed -i 's%https*://[a-z.]*archive.ubuntu.com%$ubuntuUrl%;s/^deb-src/#deb-src/' \$(find /etc/apt/sources.list* -name *list)
RUN apt-key adv --recv-key --keyserver keyserver.ubuntu.com 40976EAF437D05B5
RUN apt-get update
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:openjdk-r/ppa
RUN sed -i 's%http://ppa.launchpad.net%${artifactoryRoot}/ppa%' /etc/apt/sources.list.d/*ppa*
RUN apt-get autoremove --purge software-properties-common -y
RUN apt-get clean all
CMD "/bin/bash"

EOF

    build_and_tag
}

localize-debian(){
    local repo=$1
    local tag=$2
    local hash=$3

    mkdir -p work

    cat >work/Dockerfile <<EOF
FROM $repo:$tag
MAINTAINER jayd@jfrog.com
RUN sed -i 's%https*://\(http.debian.net/debian\|security.debian.org\)%$debianUrl%' \$(find /etc/apt/sources.list* -name *list)
CMD "/bin/bash"

EOF

    build_and_tag
}

process(){

    docker pull ${registry}/${name}${tag:+:}${tag} >/dev/null
    docker images $registry/$name |\
        awk "(NR > 1 && \"$tag\" == \"\") || (\"$tag\" != \"\" && /$tag/) {print \$1 \" \" \$2 \" \" \$3}" | while read repo tag hash; do
        echo $repo $tag $hash
        [[ $repo == *$registry* ]] || continue;
        whichFlavor $hash
        if [ $flavor ]; then
            localize-$flavor $repo $tag $hash
        fi
    done

}

parse "$@"
process
