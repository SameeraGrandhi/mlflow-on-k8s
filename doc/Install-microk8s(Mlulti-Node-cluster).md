### 1. Install microk8s
microk8s is strictly for Linux. There is no VM involved. It is distributed and runs as a snap — a pre-packaged application (similar to a Docker container). Snaps can be used on all major Linux distributions, including Ubuntu, Linux Mint, Debian and Fedora.

##### microk8s supports Kubernetes features such as:
- Service Mesh: Istio, Linkerd
- Serverless: Knative
- Monitoring: Fluentd, Prometheus, Grafana, Metrics
- Ingress, DNS, Dashboard, Clustering
- Automatic updates to the latest Kubernetes version
- GPGPU bindings for AI/ML

##### Minimum hardware requirements
In ***Master*** Node:
1. Physical or virtual system 
2. Base OS: Ubuntu 18.04 LTS
4. Minimum 4 vCPU
5. Minimum 16 GB RAM
6. Minimum 40 GB hard disk space

In ***Worker*** Node:
1. Physical or virtual system 
2. Base OS: Ubuntu 18.04 LTS
4. Minimum 2 vCPU
5. Minimum 8 GB RAM
6. Minimum 15 GB hard disk space

##### Step 1: Preparing the environment on Ubuntu Server 18.04 LTS
There are several per-requisites that you need to do in order to have Kubernetes cluster setup  working correctly.
In a nutshell you need to:
-a. Make the cluster nodes resolvable either via DNS or via local /etc/hosts file
-b.Install Docker
-c. Install Microk8s

##### Step2: Update /etc/hosts
need to add this to the /etc/hosts file on all cluster nodes: 
```
172.17.1.229 IMCHLT304
192.168.122.156 worker1
```
Note: please add your ip and Dns name in that place

##### Step 3: Update system
Run the following commands to update all system packages to the latest release:
```bash
sudo apt-get update
sudo apt-get install apt-transport-https
sudo apt-get upgrade
```
##### Step 4: Install Docker from Ubuntu Repository
Installation from the standard Ubuntu repository consists of a single apt command. It may yield stable but lower docker version number:
```bash
sudo apt install docker.io
```
The following linux commands will start Docker and ensure that starts after the reboot:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

##### Step 5: Install MicroK8s(all nodes)
```bash
sudo snap install microk8s --classic --channel=1.16/stable
```
To Start MicroK8s service
```bash
sudo microk8s.start
```
```
Started.
Enabling pod scheduling
node/imchlt304 already uncordoned
```
To Stop MicroK8s service
```bash
sudo microk8s.stop
```
To check MicroK8s Running status
```
sudo microk8s.status
```
MicroK8s includes a ***microk8s.kubectl*** command:
```bash
sudo microk8s.kubectl get no
sudo microk8s.kubectl get services
```
To use MicroK8s with your existing kubectl:
```bash
sudo microk8s.kubectl config view --raw > $HOME/.kube/config
```
##### Step 6: Adding a worker node
To create a cluster out of two or more already-running MicroK8s instances, use the ***microk8s.add-node*** command. The MicroK8s instance on which this command is run will be the master of the cluster and will host the Kubernetes control plane:
```bash
# Run this command in master node to get join node information
microk8s.add-node
Join node with: microk8s.join 172.17.1.229:25000/vExlDzApstgmbgsOtkoZAklEtSJojpvn

If the node you are adding is not reachable through the default interface you can use one of the following:
 microk8s.join 172.17.1.229:25000/vExlDzApstgmbgsOtkoZAklEtSJojpvn
 microk8s.join 192.168.122.1:25000/vExlDzApstgmbgsOtkoZAklEtSJojpvn
 microk8s.join 192.168.39.1:25000/vExlDzApstgmbgsOtkoZAklEtSJojpvn
 microk8s.join 172.18.0.1:25000/vExlDzApstgmbgsOtkoZAklEtSJojpvn
 microk8s.join 10.1.83.0:25000/vExlDzApstgmbgsOtkoZAklEtSJojpvn
```
The add-node command prints a microk8s.join command which should be executed on the MicroK8s instance that you wish to join to the cluster:
```bash
# Execute this command in worker node to join this node into cluster
microk8s.join 192.168.122.1:25000/vExlDzApstgmbgsOtkoZAklEtSJojpvn
```
Joining a node to the cluster should only take a few seconds. Afterwards you should be able to see the node has joined:
```bash
microk8s.kubectl get no
```
```
NAME        STATUS   ROLES    AGE     VERSION
imchlt304   Ready    <none>   2d23h   v1.16.6
worker1     Ready    <none>   2d22h   v1.16.6
```
##### Step 7:Enable dashboard addon
The standard Kubernetes Dashboard is a convenient way to keep track of the activity and resource use of MicroK8s
```bash
microk8s.enable dashboard
```
To log in to the Dashboard, you will need the access token.This is generated randomly on deployment, so a few commands are needed to retrieve it:
```
token=$(microk8s.kubectl -n kube-system get secret | grep default-token | cut -d " " -f1)
microk8s.kubectl -n kube-system describe secret $token
```
```
Name:         default-token-rhm27
Namespace:    kube-system
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: default
              kubernetes.io/service-account.uid: a35f9bc5-0ff4-4380-8589-64f1585c35ea

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:     1103 bytes
namespace:  11 bytes
token:      eyJhbGciOiJSUzI1NiIsImtpZCI6IjBmajRoV1dtckFzWXhyTk9rVHVDM3I5UmJsR3FPWmFqT2daQjl1LWl5WUEifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJkZWZhdWx0LXRva2VuLXJobTI3Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImRlZmF1bHQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJhMzVmOWJjNS0wZmY0LTQzODAtODU4OS02NGYxNTg1YzM1ZWEiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZS1zeXN0ZW06ZGVmYXVsdCJ9.XsbxcjnLBlsoy_S5m_UV9ryEbauLzHm6kAtTDoA-2x2veLbYMl37mARYV2CKBcACErkZKRsR9zGKCi9_BHi25p4mIxLsVPsH2tD9JOfJVlbZLsT1nyXv3bL7Wj1WeSDCWKboY6JQBugKgJncLtLEDSdUvJVnHeatedQkLkXjdSiHVOEReiRjzoXctZ9y3Vgbgc_uzqbd_0JU_M0jkRqWyd3-pMaq_R0ei9PiPKEXNw79C1EqJDhIDKCvN9A8T1BxysmKDwC1lcG1JWuDCzmq5xdM66roWZZGsqjuGe8sLKf-aCWhKVTchrduDy8vc9a1KAXWxfw-3QADwdMHvpAnzw
```
Next, you need to connect to the dashboard service. While the MicroK8s snap will have an IP address on your local network (the Cluster IP of the kubernetes-dashboard service), you can also reach the dashboard by forwarding its port to a free one on your host with:
```
microk8s.kubectl port-forward -n kube-system service/kubernetes-dashboard 10443:443
```
You can then access the Dashboard at [https://127.0.0.1:10443](https://127.0.0.1:10443)

##### Step 8:Enable private Docker registry
Deploy a private image registry and expose it on localhost:32000. run below command to enable
```bash
microk8s.enable registry
```

***check [Link](https://microk8s.io/docs/registry-private) to work with private docker registry***

***Note***: Kubernetes cluster setup required distributed storage.
List of Open source to support cloud native Storage in kubernetes
- [Longhorn](https://github.com/longhorn/longhorn)
- [Rook](https://rook.io/)
  - [Ceph](https://ceph.io/)

