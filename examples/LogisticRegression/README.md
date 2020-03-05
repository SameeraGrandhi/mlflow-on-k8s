## Run an MLflow Project on Kubernetes
In this code we demonstrate how a simple Mlflow Project can be deployed & Run on top of  **Kubernetes**. This MLflow project that trains a linear regression model on the Wine Quality Dataset to predict the quality of red wine on a scale of 0–10 given a set of features as inputs. The project uses a Docker image to capture the dependencies needed to run training code. Running a project in a Docker environment allows for capturing non-Python dependencies.

`Note`: In Demo purpose we used MicroK8s cluster with Longhorn- distributed block cloud native storage
### Download Wine quliaty Dataset
please use this [link](https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-white.csv)  to Download wine-quality Dataset & rename the file name into ***wine-quality.csv***
### Execution guide
You can run your MLflow Project on Kubernetes by following these steps:
##### Step1. Add a Docker environment to your MLflow Project, if one does not already exist.

Sample Docker File:
 ```Docker
 FROM ubuntu:latest

LABEL maintainer="Pramati dev@pramati.com"

ENV MLFLOW_TRACKING_URI=mysql+mysqldb://pramati:password123@192.168.39.85:30036/mlflow


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

RUN mkdir /opt/mlflow

# add your dependencies here
```
##### Step2. Create MlFow Project File using Docker Enviroment
Update your Docker image name,list of parameters and command based on your use case
```yaml
name: LogisticRegression
docker_env:
   image: <Docker image name>
entry_points:
  main:
    parameters:
      alpha: float
      l1_ratio: {type: float, default: 0.1}
    command: "python train.py --alpha {alpha} --l1-ratio {l1_ratio}"
```

##### Step3. Create a backend configuration JSON file with the following entries

* **kube-context** The Kubernetes context where MLflow will run the job. If not provided, MLflow will use the current context. If no context is available, MLFlow will assume it is running in a Kubernetes cluster and it will use the Kubernetes service account running the current pod (‘in-cluster’ configuration).

* **repository-uri** The URI of the docker repository where the Project execution Docker image will be uploaded (pushed). Your Kubernetes cluster must have access to this repository in order to run your MLflow Project.

* **kube-job-template-path** The path to a YAML configuration file for your Kubernetes Job - a Kubernetes Job Spec. MLflow reads the Job Spec and replaces certain fields to facilitate job execution and monitoring; MLflow does not modify the original template file. For more information about writing Kubernetes Job Spec templates for use with MLflow, see the Job Templates section.

* **Example Kubernetes backend configuration**
 ```json
	 {
	    "kube-context": "<kube-context name>", # get kube-context name from ~/.kube/config 
	    "kube-job-template-path": "<kubernetes_job_template.yaml path>",
	    "repository-uri": "<Docker image name>"
	 }
```

##### Step4. Create a kubernetes job configuration Yaml file with the following entries
MLflow executes Projects on Kubernetes by creating Kubernetes Job resources. MLflow creates a Kubernetes Job for an MLflow Project by reading a user-specified Job Spec. When MLflow reads a Job Spec, it formats the following fields:

**metadata.name** Replaced with a string containing the name of the MLflow Project and the time of Project execution

**spec.template.spec.container[0].name** Replaced with the name of the MLflow Project

**spec.template.spec.container[0].image** Replaced with the URI of the Docker image created during Project execution. This URI includes the Docker image’s digest hash.

**spec.template.spec.container[0].command** Replaced with the Project entry point command specified when executing the MLflow Project.

Example Job Template:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
   name: "{replaced with MLflow Project name}"
   namespace: mlflowonkube
spec:
   ttlSecondsAfterFinished: 100
   backoffLimit: 1
   template:
      spec:
         containers:
         -  name: "{replaced with MLflow Project name}"
            image: <Docker image name>
            command:
            - ["{replaced with MLflow Project entry point command}"]
            volumeMounts:
            -  name: mlflow-persistent-storage
               mountPath: /mnt/mlflow
         imagePullSecrets:
         -  name: regcred
         volumes:
         -  name: mlflow-persistent-storage
            persistentVolumeClaim:
               claimName: mlflow-pv-claim
         resources:
            limits:
               memory: 512Mi
            requests:
               memory: 256Mi
         restartPolicy: Never
```

##### Step5. Run the Project using the MLflow Projects CLI 
```bash
export MLFLOW_TRACKING_URI=http://<ip>:30035
mlflow run <project_dir> --backend kubernetes --backend-config <project_dir>/kubernetes_config.json -P alpha=0.5
```
After the code successfully runs, you can get the following results:
```bash
2020/03/05 12:30:51 INFO mlflow.projects: === Building docker image srinivasanpramati2020/mlflow-on-kubernetes-docker:ddcbdff ===
2020/03/05 12:30:59 INFO mlflow.projects.kubernetes: === Pushing docker image srinivasanpramati2020/mlflow-on-kubernetes-docker:ddcbdff ===
2020/03/05 12:34:49 INFO mlflow.projects: === Created directory /tmp/tmpu6b4fm1m for downloading remote URIs passed to arguments of type 'path' ===
2020/03/05 12:34:49 INFO mlflow.projects.kubernetes: === Creating Job linear-crf-with-spatial-features-2020-03-05-12-34-49-025410 ===
2020/03/05 12:34:49 INFO mlflow.projects.kubernetes: Job started.
2020/03/05 12:37:34 INFO mlflow.projects.kubernetes: None
2020/03/05 12:37:34 INFO mlflow.projects: === Run (ID '44c87908562f4f3cbeda17c5bbc5ef98') succeeded ===
```
After running, you can view the result through MLflow UI:

In the browser, go to http://127.0.0.1:30050, you will get the following results.

<img src="img/mlflowui.png" width="1000" height="300" />

 ### How it works
 When you run an MLflow Project on Kubernetes it will execute below steps
 1. Ml Flow trying to Build new Docker image
 2. Ml FLow push new Docker Image to Docker Repository
 3. Starts a Kubernetes Job on your Kubernetes Cluster
 4. Kubernetes job download the Docker image and starts a corresponding docker container inside of Pod 
 5. Docker Container invoke your project entry point to logging params,metrics and artifacts
