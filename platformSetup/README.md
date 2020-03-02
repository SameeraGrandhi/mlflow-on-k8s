# Platform Setup
This Project describes all the installation process for To run Mlflow project on  minikube/Kubernetes Cluster starting from scratch. This will covers all aspect of its installation including all various softwares needed, and how to deploy the required services on kubernetes cluster.



### 1. Install MiniKube/Kubernetes Cluster
Check the [wiki](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/wikis/platform-setup-on-minikube) to Install MiniKube with Kvm2 Driver

Check the [wiki](https://gitlab.pramati.com/devops-practise/kubernetes/wikis/Getting-Started) to Install Kubernetes Cluster

Check the [wiki](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/wikis/platform-setup-on-microk8s(Mlulti-Node-cluster)) to Install Kubernetes Cluster using microk8s

### 2. Clone the repo
Clone this repository. In a terminal, run:

```
$ git clone https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes.git
```
### 3. Create namespace in kubernetes
Run below command to create namespace in kubernetes
```
$ kubectl create ns <your namespace>
```

### 4. Create the Database service on kubernetes
The backend consists of a MySQL database & it has a Deployment and a Service. The deployment manages the pods started for mysql service. The Service creates a stable DNS entry for mysql service  so they can reference their dependencies by name.
##### Step 1: Update mysql password in manifest file
Edit the mysql **kustomization.yaml** file to update password
``` yaml
secretGenerator:
- name: mysql-pass
  namespace: <your namespace>
  literals:
  - password=<your password>
resources:
- mysql-deployment.yaml
- client-pod.yaml
```
#####  Step 2:  Update namespace in all Manifest file 
Edit name space in **client-pod.yaml** file
``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: mysql-client
  namespace: <your namespace>
  labels:
    name: mysql-client
spec:
  containers:
  - name: mysql-client
    image: ellerbrock/alpine-mysql-client
    command: ["sleep", "1000"]
```
Edit name space in **mysql-pv.yaml** file
``` yaml
apiVersion: v1
kind: PersistentVolume
metadata:
   name: mysql-pv-volume
   namespace:  <your namespace>
   labels:
      type: local
spec:
   storageClassName: manual
   capacity:
      storage: 1Gi
   accessModes:
   - ReadWriteOnce
   hostPath:
      path: /mnt/db-data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
   name: mysql-pv-claim
   namespace:  <your namespace>
   labels:
      app: mysql
spec:
   storageClassName: manual
   accessModes:
   - ReadWriteOnce
   resources:
      requests:
         storage: 1Gi
   volumeName: mysql-pv-volume
```

Edit name space in **mysql-deployment.yaml** file
``` yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
  namespace: <your namespace>
spec:
  type: NodePort
  ports:
  - port: 3306
    nodePort: 30036
    name: http
  selector:
    app: mysql
---
apiVersion: apps/v1 
kind: Deployment
metadata:
  name: mysql
  namespace: <your namespace>
spec:
  selector:
    matchLabels:
      app: mysql
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - image: mysql:5.6
        name: mysql
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-pass
              key: password
        ports:
        - containerPort: 3306
          name: mysql
        volumeMounts:
        - name: mysql-persistent-storage
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-persistent-storage
        persistentVolumeClaim:
          claimName: mysql-pv-claim
```
#####  Step 3:  Start Mysql Service in a container
Run a below command to Start the mysql service in a Mini-Kube cluster
```bash
cd <mysql manifest folder>
kustomize build mysql/overlays/minikube | microk8s.kubectl apply -f -
```

Run a below command to Start the mysql service in a MicroK8s cluster
```bash
cd <mysql manifest folder>
kustomize build mysql/overlays/microk8s | microk8s.kubectl apply -f -
```
command to verify the pod running status
```bash
kubectl get pods -n <your namespace>
```
#####  Step 4: Create Database & User to update the mlflow tracking information
Run below command to get minikube ip address
```bash
minikube ip
```
Run below command to get microk8s ip address
```bash
#run this command in master node
ifconfig
```

login to mysql server to create database and user
```bash
mysql -h <ip> --port=30036 -u root -p
> enter <your password>
```
Sql to Create database & User
~~~~sql
create database mflow;
CREATE USER 'pramati'@'%' IDENTIFIED BY '<your password>';
GRANT ALL PRIVILEGES ON *.* TO 'pramati'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
~~~~

### 5. Create the Mlflow Server service on Kubernetes
mlFlow is a framework that supports the machine learning lifecycle. This means that it has components to monitor your model during training and running, ability to store models, load the model in production code and create a pipeline.

#####  Step 1: Update Mysql BACKEND_STORE Connection url in Docker file

```Dockerfile
FROM ubuntu:latest

LABEL maintainer="srinivasan.ramalingam@imaginea.com"

ENV MLFLOW_HOME /app/mlflow
ENV SERVER_PORT 5000
ENV SERVER_HOST 0.0.0.0
ENV ARTIFACT_STORE /mnt/mlflow
ENV BACKEND_STORE mysql+mysqldb://pramati:<your_password>@<minikube_ip>:30036/mlflow


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
```

#####  Step 2: Create Kubernetes Secrets to store Docker resgistry information

To create Docker config.json, please login to Docker from terminal 
```bash
docker login
```
To Create Kubernetes Secrets please run the below commands
```bash
kubectl create secret generic regcred -n <your namespace>  --from-file=.dockerconfigjson=/home/<user>/.docker/config.json --type=kubernetes.io/dockerconfigjson
```

#####  Step 3: Build & push mlflow server image
Run a below command to Build & Push Docker image from local machine to Docker registry
```bash
cd <mlflow server docker file path>
docker build -t mlflow-server:latest .
docker tag mlflow-server:latest <docker_reponame>/mlflow-server:latest
docker push <docker_reponame>/mlflow-server:latest
```


#####  Step 4: Update namespace & Docker image name in all Manifest file

Edit name space in **mlflow-server-pv.yaml** file
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
   name: mlflow-pv-volume
   namespace: <your namespace>
   labels:
      type: local
spec:
   storageClassName: manual
   capacity:
      storage: 1Gi
   accessModes:
   - ReadWriteOnce
   hostPath:
      path: /mnt/mlflow
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
   name: mlflow-pv-claim
   namespace: <your namespace>
   labels:
      app: mlflowserver
spec:
   storageClassName: manual
   accessModes:
   - ReadWriteOnce
   resources:
      requests:
         storage: 1Gi
   volumeName: mlflow-pv-volume
```

Edit name space in **mlflowserver-deployment.yaml** file
``` yaml
apiVersion: v1
kind: Service
metadata:
   name: mlflowserver
   namespace: <your namespace>
spec:
   type: NodePort
   ports:
   -  port: 5000
      protocol: TCP
      nodePort: 30035
      name: http
   selector:
      app: mlflowui
---
apiVersion: apps/v1
kind: Deployment
metadata:
   name: mlflowserver
   namespace: <your namespace>
spec:
   selector:
      matchLabels:
         app: mlflowui
   strategy:
      type: Recreate
   template:
      metadata:
         labels:
            app: mlflowui
      spec:
         containers:
         -  image: <your docker image name>
            name: mlflowserver
            ports:
            -  containerPort: 5000
               name: mlflowui
            volumeMounts:
            -  name: mlflow-persistent-storage
               mountPath: /mnt/mlflow
         imagePullSecrets:
         -  name: regcred
         volumes:
         -  name: mlflow-persistent-storage
            persistentVolumeClaim:
               claimName: mlflow-pv-claim
```
#####  Step 5:  Start Mlflow server Service in a container
Run a below command to Start the mlflow service service in a MiniKube cluster
```bash
kustomize build mlflowserver/overlays/minikube | microk8s.kubectl apply -f -
```
Run a below command to Start the mlflow service service in a Microk8s cluster
```bash
kustomize build mlflowserver/overlays/microk8s | microk8s.kubectl apply -f -
```
command to verify the pod running status
```bash
kubectl get pods -n <your namespace>
```



