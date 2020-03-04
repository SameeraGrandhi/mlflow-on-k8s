# Platform Setup
This Project describes all the installation process for To run Mlflow project on  minikube/Kubernetes Cluster starting from scratch. This will covers all aspect of its installation including all various softwares needed, and how to deploy the required services on kubernetes cluster.



### 1. Install MiniKube/Kubernetes Cluster
Check the [wiki](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/wikis/Install-MiniKube-with-Kvm2-Driver) to Install MiniKube with Kvm2 Driver

Check the [wiki](https://gitlab.pramati.com/srinivasanr/mlflowonkubernetes/wikis/Install-microk8s(Mlulti-Node-cluster)) to Install Kubernetes Cluster using microk8s

Check the [wiki](https://gitlab.pramati.com/devops-practise/kubernetes/wikis/Getting-Started) to Install Kubernetes Cluster



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