FROM ubuntu:latest

LABEL maintainer="srinivasan.ramalingam@imaginea.com"

ENV MLFLOW_HOME /app/mlflow
ENV SERVER_PORT {{mlflow.port}}
ENV SERVER_HOST 0.0.0.0
ENV ARTIFACT_STORE {{mlflow.mountPath}}
ENV BACKEND_STORE mysql+mysqldb://{{mysql.user}}:{{mysql.password}}@{{master_ip}}:{{mlflow.nodePort}}/{{mysql.dbname}}


RUN apt-get update \
  && apt-get install -y locales python3-pip python3-dev libmysqlclient-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip \
  && pip3 install mysqlclient
  
# Set the locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8 
  
RUN pip3 install mlflow

COPY ./start.sh ${MLFLOW_HOME}/start.sh

EXPOSE ${SERVER_PORT}/tcp

WORKDIR ${MLFLOW_HOME}

VOLUME ["${MLFLOW_HOME}"]

RUN chmod -R 777 ${MLFLOW_HOME}/start.sh

ENTRYPOINT ["bash","./start.sh" ]
