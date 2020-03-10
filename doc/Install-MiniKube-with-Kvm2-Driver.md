### 1. Install MiniKube with Kvm2 Driver
Minikube is an open source tool that was developed to enable developers and system administrators to run a single cluster of Kubernetes on their local machine. Minikube starts a single node kubernetes cluster locally with small resource utilization. This is ideal for development tests and POC purposes.

##### Minikube supports Kubernetes features such as:
- DNS
- NodePorts
- ConfigMaps and Secrets
- Dashboards
- Container Runtime: Docker, CRI-O, and containerd
- Enabling CNI (Container Network Interface)
-  Ingress
- PersistentVolumes of type hostPath

##### Minimum hardware requirements
1. Physical or virtual system 
2. Base OS: Ubuntu 18.04 LTS
4. Minimum 4 vCPU
5. Minimum 16 GB RAM
6. Minimum 40 GB hard disk space


##### Step 1: Update system
Run the following commands to update all system packages to the latest release:
```bash
sudo apt-get update
sudo apt-get install apt-transport-https
sudo apt-get upgrade
```
##### Step 2: Install Docker from Ubuntu Repository
Installation from the standard Ubuntu repository consists of a single apt command. It may yield stable but lower docker version number:
```bash
sudo apt install docker.io
```
The following linux commands will start Docker and ensure that starts after the reboot:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```
##### Step 3: Install Docker Machine KVM driver
Download the binary and make it executable.
```bash
sudo apt-get -y install qemu-kvm libvirt-bin virt-top  libguestfs-tools virtinst bridge-utils
curl -LO https://storage.googleapis.com/minikube/releases/latest/docker-machine-driver-kvm2
chmod +x docker-machine-driver-kvm2
sudo mv docker-machine-driver-kvm2 /usr/local/bin/
```
##### Step 4: Download minikube
Download the minikube binary &  put the binary under /usr/local/bin directory
```bash
wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube-linux-amd64
sudo mv minikube-linux-amd64 /usr/local/bin/minikube
```
Confirm version installed
```bash
minikube version
```
##### Step 5: Install kubectl on Ubuntu
We need kubectl which is a command line tool used to deploy and manage applications on Kubernetes:
```bash
curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
```
Confirm version installed
```bash
kubectl version -o json
```
##### Step 6: Starting Minikube
With all components installed, you should be ready to start minikube with KVM driver.
Set KVM as default driver:
```bash
minikube config set vm-driver kvm2
```
The minikube start command will download VM image and configure the Kubernetes single node cluster

**Note:** Don't run below command as a root user
```bash
minikube start --cpus 4 --memory 8192 set vm-driver kvm2
```
To Enable dashboard run below command
```
minikube dashboard
```