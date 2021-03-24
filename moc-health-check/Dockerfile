FROM openshift/jenkins-2-centos7:latest
USER root
RUN yum install -y python3
RUN python3 --version
RUN yum install -y python3-devel
RUN yum install -y python3-setuptools
RUN python3 /usr/lib/python3.6/site-packages/easy_install.py pip
RUN pip3 install --user --upgrade pip 

RUN pip3 --version
RUN yum install -y gcc libcurl-devel libcurl-openssl-devel openssl-devel python3-dev
RUN export PYCURL_SSL_LIBRARY=nss
RUN export LDFLAGS="-L/usr/local/opt/openssl/lib"
RUN export CPPFLAGS="-I/usr/local/opt/openssl/include"
RUN pip3  install --no-cache-dir --compile --ignore-installed --install-option="--with-nss" pycurl
RUN pip3 install pfurl