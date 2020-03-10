# MLflow Project on Kubernetes
  
The purpose of the project is to demonstrate how to create, dockerized and run a
MLflow project in the kubernetes cluster. Data science team gets easy access to the 
scalable kubernetes platform with MLFlow to train, test and deploy the models. 
Also gets standard pipeline templates to manage project dependencies and create 
a convenient model pipelines with model serving for Data Science Team. The templates 
provided are simple enough for Data Science team to consume, so that they can spend
more time on models and data than on platform.


## Getting Started

When installing the Kubernetes cluster from scratch & scale out mlflow job on kubernetes we are encouraged to follow the order specified below
1. Platform setup & configuration Steps
2. Create MLflow project using docker (rather than conda) to manage project dependencies. [sample Project](examples/LogisticRegression)
3. Create your ml model serve flask api service based on your use cases. [Sample project](examples/FlaskMlflowServe)

### End to End Flow Diagram:
![wkg](doc/uploads/flow_dia.png)
### Software Prerequisites
1. Use Python 3.6
2. Linux-specific Software Requirements
   * Ubuntu 18.04
   * Snap  - for microk8s setup
   * Virtualbox/Kvm Driver - for Minikube setup

### Platform setup & configuration Steps
The followed context describes all the installation process for To run the Mlflow project on  minikube/microk8s Cluster starts from scratch. This will covers all aspects of its installation, including all various softwares needed & how to deploy the required services on kubernetes cluster. Follow these general installation and configuration steps, located in this below section

1. Install and configure the MiniKube/Microk8s Cluster
2. Clone the repo
3. Create a new namespace for our application
4. Create a new secret for our application
5. Additional Software Requirements

#### 1. Install MiniKube/Microk8s/Amazon EKS Cluster
There are so many open source tools are available in market now a days to build kubernetes cluster. Here we are, covered in Minikube,Amazon EKS and Microk8s installation process
* Install **Minikube** to work with Kubernetes on a local environment for purpose. Check the [Install-MiniKube-with-Kvm2-Driver.md](doc/Install-MiniKube-with-Kvm2-Driver.md) to Install MiniKube with Kvm2 Driver
* Install **Microk8s** to work with Kubernetes on a Multi node cluster purpose. Check the [Install-microk8s-Mlulti-Node-cluster.md](doc/Install-microk8s(Mlulti-Node-cluster).md) to Install microk8s
* Install **Amazon EKS** to work with Kubernetes on a Multi node cluster purpose. Check the [Install-and-configure-Amazon-EKS-Cluster](doc/Install-and-configure-Amazon-EKS-Cluster.md) to Install miok8s

##### Note: In our Example project we used Microk8s

#### 2. Clone the repo
Clone this repository. In a terminal, run:

```
$ git clone https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes.git
```
#### 3. Create namespace in kubernetes
Run below command to create namespace in kubernetes
```
# Minikube
$ kubectl create ns <your namespace>

# MicroK8s
$ microk8s.kubectl create ns <your namespace>
```

#### 4. Create a new secret for our application
Run below command to create secret in kubernetes
```bash
 kubectl create secret generic regcred -n <your namespace>  --from-file=.dockerconfigjson=/home/<username>/.docker/config.json --type=kubernetes.io/dockerconfigjson #replace username & namespace
```

#### 5. Additional Software Requirements
The following service are required to run a mlflow project on kuberenets Cluster
1. Mysql
2. Mlflow Server
3. Nexus

If you do not want to deploy the services through  automation process, use these alternate, [manual deployment procedures](doc/Manual-Deployment-process-for-additional-required-service.md)

If you want to deploy the services through automation process, follow these general configuration and deployment steps
##### a. Update Meta data information in `setting.py`(src/lib/settings.py)
```python
config = {
  "namespace": "mlflowonkube",
  "cluster": "microk8s", # cluster type name based on your installation
  "master_ip":"172.17.1.229",  
  "kubectl":"microk8s.kubectl", #kubernetes command line
  "kube_context":"microk8s", #get kube context name from `~/.kube/config` file
  "mysql": {
    "user":"pramati", #mysql username
    "password": "password123", #mysql password
    "dbname":"mlflow", #mysql database name
    "port":"3306",    # target port
    "nodePort":"30036", # expose port 
    "mountPath": "/var/lib/mysql", # volumn mount path
    "storage":"1Gi", # maximum storage size
    "isSkip": False # help to skip this service setup if it's true
  },
  "mlflow": {
    "port":"5002",
    "nodePort":"30035",
    "mountPath": "/mnt/mlflow", 
    "storage":"1Gi",
    "docker_image": "172.17.1.229:32000/mlflow-server:registry", # private microk8s Docker registry image name
    "isSkip": False
  },
  "nexsus": {
    "mountPath": "/mnt/nexsus",
    "docker_image": "sonatype/nexus3",
    "isSkip": False
  },
  "flask": {
    "mountPath": "/mnt/mlflow",
    "nodePort":"30091",
    "docker_image": "172.17.1.229:32000/mlflow-flask:registry",
    "run_id":"fe25e92156fa4b10b6b3a165a31ce676" # mlflow job run id
  },
  "kube_job": {
    "projectname":"LogisticRegression", # custom kubernetes mlflow project name
    "mountPath": "/mnt/mlflow", # volumn mount path to store artifacts
    "entry_cmd":"train.py --alpha {alpha} --l1-ratio {l1_ratio}", #entry command to train model
    "docker_image": "172.17.1.229:32000/mlflow-flask:registry", # private microk8s Docker registry image name
    "limit_mem":"512Mi", # maximum memory required to completed the model training
    "requests_mem":"256Mi", # initial Required memory
    "maintainer" :"srinivasan.ramalingam@imaginea.com"
  }
}
```

##### a. Run below command to start the aumotated process
```bash
python service_helper.py --setup_platform
```

After running, you can view the services through Kubernetes Dashboard:
In the browser, go to https://127.0.0.1:10443 (``we use microk8s, the port may be varied in your case``), you will get the following service are up.
1. Mysql
2. Mlfowserver
3. Nexus

###### a.1 command to generate Sample Mlflow project
```bash
python service_helper.py --generate_ml_template
```
```bash
__main__     INFO     current output Directory Path /home/srinivasan/workspace_python/cluster_setup/output/1583304596398
docker.utils.config DEBUG    Trying paths: ['/home/srinivasan/.docker/config.json', '/home/srinivasan/.dockercfg']
docker.utils.config DEBUG    Found file at path: /home/srinivasan/.docker/config.json
docker.auth  DEBUG    Found 'auths' section
docker.auth  DEBUG    Found entry (registry='192.168.39.85:30002', username='admin')
docker.auth  DEBUG    Found entry (registry='https://index.docker.io/v1/', username='srinivasanpramati2020')
__main__     INFO     template render the files in /home/srinivasan/workspace_python/cluster_setup/src/lib/template/mlflow folder
__main__     INFO     template has been generated in MlflowTemplateGen service
__main__     INFO     Sample Template generated in /home/srinivasan/workspace_python/cluster_setup/output/1583304596398/mlflow_on_kubernetes folder
```
