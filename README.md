# MLflow Project on Kubernetes
  A Simple MLFLow Project will demonstrates how to create,dockerized and run an MLflow project on Kubernets cluster to manage project dependencies

**Note:** to understand more on this repo. please ref this [link](https://docs.google.com/presentation/d/1fyvNeqVVdXxR9KZsS0ksoWPO_4lg9n7FfMmnawbec-8/edit?usp=sharing)
## Steps to run kuberenetes job
1. Platform Setup
2. Create Mlflow Project based on the [sample Project](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/tree/master/examples/LogisticRegression)
3. Create your ml model flask api service based on your use cases. Sample project [url](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/tree/master/examples/FlaskMlflowServe)

# Platform Setup
This context describes all the installation process for To run Mlflow project on  minikube/Kubernetes Cluster starting from scratch. This will covers all aspect of its installation including all various softwares needed, and how to deploy the required services on kubernetes cluster.



### 1. Install MiniKube/Kubernetes Cluster
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
$ kubectl create ns <your namespace>
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
