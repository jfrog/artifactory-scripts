#!/bin/bash

artifactoryRegistry=
repositoryName=fedora

destinationRepositoryName=
specificTag=
destinationUserName=
noUpdate=false
forceUpdate=false
localRepoName=
localPrefix=my
flavor=
pkgRepo=


[ -x ~/.jfrog/docker.rc ] && . ~/.jfrog/docker.rc


help(){
    cat <<EOF
    Localize a docker repository to use a local artifactory.
    It will detect the flavor of linux and configure the package manager to use the local repository

    Usage: $(basename $0) <opts> remote tag artifactory
    Where:
        repository = Docker repository to localize
        tag        = Specific repository tag to localize
        artifactory= Local docker registry
        These can also be specified with option switches
    Opts:
        -a --artifactory    Local docker registry               required
        -r --remote         Remote image name on docker.io      required
        -p --prefix         Prefix to add to local repository   defaults to: $localPrefix
        -l --local          Local image name                    defaults to: remote image name with prefix
        -t --tag            Specific tag to localize            defaults to: all tags for that image
        -i --install        URL of local package repository     no default
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
            -p|--prefix) localPrefix=$2; shift 2 ;;
            -l|--local) destinationRepositoryName=$2; shift 2 ;;
    	    -i|--install) pkgRepo=$2; shift 2 ;;
            -t|--tag) specificTag=$2; shift 2 ;;
            -n|--noupdate) noUpdate=true; shift ;;
            -f|--force) forceUpdate=true; shift ;;
            -h|--help) help ; exit 0 ;;
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

     echo Localizing $artifactoryRegistry/$repositoryName${specificTag:+:}${specificTag} into $artifactoryRegistry/$destinationRepositoryName${specificTag:+:}${specificTag}
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
    docker build --tag=$artifactoryRegistry/$destinationRepositoryName${tag:+:}${tag} work
    docker push $artifactoryRegistry/$destinationRepositoryName${tag:+:}${tag}
    rm -rf work
}

localize-centos(){
    local repo=$1
    local tag=$2
    local hash=$3

    mkdir -p work/{tmp,etc/yum.repos.d}

    curl $pkgRepo/rpm-local/develop.repo -o work/etc/yum.repos.d/develop.repo
    sed -i '/enabled/ d;$ ienabled=0' work/etc/yum.repos.d/develop.repo
    curl $pkgRepo/rpm-local/release.repo -o work/etc/yum.repos.d/release.repo
    sed -i '/enabled/ d;$ ienabled=1' work/etc/yum.repos.d/release.repo

    cat >work/tmp/fetchepel.sh <<-EOF1
        #!/bin/bash
set -x
        distro=\$(sed -n 's/^distroverpkg=//p' /etc/yum.conf)
        releasever=\$(rpm -q --qf "%{version}" -f /etc/\$distro)
        basearch=\$(rpm -q --qf "%{arch}" -f /etc/\$distro)

        cat >/etc/yum.repos.d/tmp.repo <<-EOF
[tmp]
name=epel temp repo
baseurl=$pkgRepo/fedora/epel/\$releasever/\$basearch
gpgcheck=0
EOF
        yum --disablerepo=* --enablerepo=tmp install -y epel-release
        yum --disablerepo=* --enablerepo=tmp clean all

        rm /etc/yum.repos.d/tmp.repo
EOF1
    chmod +x work/tmp/fetchepel.sh

    cat >work/Dockerfile <<EOF
FROM $artifactoryRegistry/$repositoryName:$tag
MAINTAINER jayd@jfrog.com

COPY tmp /tmp
RUN /tmp/fetchepel.sh
RUN sed -i "\
    /^mirror/ s/^/#/; \
    s/^#base/base/; \
    /baseurl/ s%http.://\(mirror.centos.org\|download.fedoraproject.org/pub\)%$pkgRepo%; \
    s%file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS%$pkgRepo/centos/RPM-GPG-KEY-CentOS%; \
    s%file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL%$pkgRepo/fedora/epel/RPM-GPG-KEY-EPEL%; \
    " /etc/yum.repos.d/*.repo
COPY etc /etc

CMD "/bin/bash"

EOF

    build_and_tag

}

localize-fedora(){
    local repo=$1
    local tag=$2
    local hash=$3

    mkdir -p work/{etc/yum.repos.d,tmp}

    curl $pkgRepo/rpm-local/develop.repo -o work/etc/yum.repos.d/develop.repo
    sed -i '/enabled/ d;$ ienabled=0' work/etc/yum.repos.d/develop.repo
    curl $pkgRepo/rpm-local/release.repo -o work/etc/yum.repos.d/release.repo
    sed -i '/enabled/ d;$ ienabled=1' work/etc/yum.repos.d/release.repo

    cat >work/Dockerfile <<EOF
FROM $repo:$tag
MAINTAINER jayd@jfrog.com
RUN sed -i "\
    /^\(mirror\|meta\)/ s/^/#/; \
    s/^#base/base/; \
    /baseurl/ s%https*://download.fedoraproject.org/pub%$pkgRepo/fedora%; \
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
RUN sed -i 's%https*://[a-z.]*archive.ubuntu.com%$pkgRepo%' \$(find /etc/apt/sources.list* -name *list)
RUN apt-key adv --recv-key --keyserver keyserver.ubuntu.com 40976EAF437D05B5
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
RUN sed -i 's%https*://\(http.debian.net\|security.debian.org\)%$pkgRepo%' \$(find /etc/apt/sources.list* -name *list)
CMD "/bin/bash"

EOF

    build_and_tag
}

process(){

    docker pull ${artifactoryRegistry}/${repositoryName}${specificTag:+:}${specificTag} >/dev/null
    docker images $artifactoryRegistry/$repositoryName |\
        awk "(NR > 1 && \"$specificTag\" == \"\") || (\"$specificTag\" != \"\" && /$specificTag/) {print \$1 \" \" \$2 \" \" \$3}" | while read repo tag hash; do
        echo $repo $tag $hash
        [[ $repo == *$artifactoryRegistry* ]] || continue;
        whichFlavor $hash
        if [ $flavor ]; then
            localize-$flavor $repo $tag $hash
        fi
    done

}

parse "$@"
process

