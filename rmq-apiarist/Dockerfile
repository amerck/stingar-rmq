FROM centos:centos7

LABEL maintainer="Alexander Merck <alexander.t.merck@gmail.com>"
LABEL name="apiarist"
LABEL version="0.1"
LABEL release="1"
LABEL summary="Honeypot data collector and normalizer"
LABEL description="Apiarist is a framework for collecting and normalizing data feeds from various honeypots and integrating with the STINGAR tool suite"
LABEL authoritative-source-url="https://github.com/amerck/apiarist"
LABEL changelog-url="https://github.com/amerck/apiarist/commits/master"

# Set DOCKER var - used by Apiarist init to determine logging
ENV pkgs "git jq python2-devel python2-pip"
ENV user "apiarist"
ENV pip_pkgs "pika pymongo flask"
ENV workdir "/home/${user}"

RUN yum install -y epel-release \
    && yum install -y $pkgs \
    && yum clean all \
    && rm -rf /var/cache/yum

RUN pip --no-cache-dir install --upgrade pip setuptools

RUN pip install $pip_pkgs

RUN useradd $user \
    && usermod -aG users $user

COPY apiarist $workdir/apiarist
RUN chown -R $user $workdir
USER $user
WORKDIR $workdir

ENTRYPOINT python $workdir/apiarist/apiarist.py --config $workdir/apiarist/apiarist.cfg --rabbitmq --normalizer
