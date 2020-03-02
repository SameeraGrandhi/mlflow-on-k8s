## ML-Model-Flask application Deploy on Kubernetes
This is a Simple project to elaborate how Machine Learning Models are deployed on production using Flask API

### Project Structure
This project has two major parts :
1. app.py - This contains Flask APIs that receives wine  details through GUI or API calls, computes the precited value based on our model and returns it.
2. templates - This folder contains the HTML template to allow user to enter wine detail and displays the predicted wine quality.

### Steps to Build & Deploy the Project on 
#### Step1: Build & Push this Project into Docker Registry
Move to Project Directory & Run below commands to build and push Docker image to Docker Registry
```bash
cd <flask project path>
docker build -t model-flask:latest .
docker tag model-flask <your_repo_name>/mlflow-flask
docker push <your_repo_name>/mlflow-flask
```
Sample Dockerfile
```Dockerfile
FROM ubuntu:latest
LABEL maintainer="Pramati dev@pramati.com"
ENV LANG C.UTF-8
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
```

#### Step2: Update mlflow runid & Docker image name in Manifest file
update runid & docker image name in **flask-deployment.yaml** file
```yaml
apiVersion: v1
kind: Service
metadata:
   name: flaskapi-service
   namespace: <your namespace>
spec:
   selector:
      app: flaskapi
   type: NodePort
   ports:
   -  protocol: TCP
      port: 9791
      targetPort: 9791
      nodePort: 30091
---
apiVersion: apps/v1
kind: Deployment
metadata:
   name: flaskapi-deployment
   namespace: <your namespace>
   labels:
      app: flaskapi
spec:
   replicas: 1
   selector:
      matchLabels:
         app: flaskapi
   template:
      metadata:
         labels:
            app: flaskapi
      spec:
         containers:
         -  name: flaskapi
            image: <docker image name>
            env:
            -  name: MODEL_PATH
               value: /mnt/mlflow/0/<runid>/artifacts/model
            ports:
            -  containerPort: 9791
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
In Microk8s update docker image name in ***kubernetes/overlays/microk8s/patch.yaml***
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
   name: flaskapi-deployment
   namespace: <your namespace>
spec:
   template:
      spec:
         containers:
         -  name: flaskapi
            image: <docker image name>
```
#####  Step 3:  Start ml model flask server Service in a container
Run a below command to Start the ml model flask server in a kubernetes cluster

In MiniKube
```bash
cd <flask service manifest folder>
kustomize build kubernetes/overlays/minikube | kubectl apply -f -
```

In Microk8s
```bash
cd <flask service manifest folder>
kustomize build kubernetes/overlays/microk8s | microk8s.kubectl apply -f -
```

command to verify the pod running status
```bash
kubectl get pods -n <your namespace>
```
