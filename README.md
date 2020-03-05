# MLflow Project on Kubernetes
  
The purpose of the project is to demonstrates  how to create,dockerized and run an MLflow project on Kubernets cluster to manage project dependencies  and  to create a convenient and easy-to-use application for DataSciene Team to run an mlfow project on kubernetes cluster with out having any prior knowelege on the Dev ops side to train  ml model & model serve.

**Note:** to understand more on this repo. please ref this [link](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/blob/master/mlflowonkubernetes.pdf)

## Getting Started
   Todo

## Steps to run kuberenetes job
1. Platform Setup
2. Create Mlflow Project based on the [sample Project](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/tree/master/examples/LogisticRegression)
3. Create your ml model flask api service based on your use cases. Sample project [url](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/tree/master/examples/FlaskMlflowServe)

## Platform Setup
This context describes all the installation process for To run Mlflow project on  minikube/microk8s Cluster starting from scratch. This will covers all aspect of its installation including all various softwares needed & how to deploy the required services on kubernetes cluster.

### 1. Install MiniKube/Microk8s Cluster
Check the [wiki](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/wikis/Install-MiniKube-with-Kvm2-Driver) to Install MiniKube with Kvm2 Driver

Check the [wiki](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/wikis/Install-microk8s(Mlulti-Node-cluster)) to Install Kubernetes Cluster using microk8s

### 2. Clone the repo
Clone this repository. In a terminal, run:

```
$ git clone https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes.git
```
### 3. Create namespace in kubernetes
Run below command to create namespace in kubernetes
```
# Minikube
$ kubectl create ns <your namespace>

# MicroK8s
$ microk8s.kubectl create ns <your namespace>
```

### 4. Addtional Required service deployment process
The following service are required to run a mlflow project on kuberenets Cluster
1. Mysql
2. Mlflow Server
3. Nexus

To Deploy this service mannually please check this [link](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/wikis/Manual-Deployment-process-for-additional-required-service)

To Automate this deployment process. please follow the below steps
#### a. Update Meta data information in `setting.py`(src/lib/settings.py)
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

#### a. Run below command to start the aumotated process
```bash
python service_helper.py --setup_platform
```

After running, you can view the services through Kubernetes Dashboard:
In the browser, go to https://127.0.0.1:10443 (``we use microk8s, the port may be varied in your case``), you will get the following service are up.
1. Mysql
2. Mlfowserver
3. Nexus

<img src="img/kubernetes.png" width="1000" height="500" />

##### a.1 command to build Sample Mlflow project
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
