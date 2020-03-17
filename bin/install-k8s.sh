#!/bin/bash
#------------------------------------
## Install common dependencies 
#-----------------------------------
function commonOpe(){
	# --------------------------------------------------
	#   Install Prerequisites & Setup Python3  (Ubuntu)
	# --------------------------------------------------
	sudo apt-get update \
	  && apt-get install -y apt-transport-https dialog \
	     locales python3-pip python3-dev libmysqlclient-dev \
	  && cd /usr/local/bin \
	  && ln -s /usr/bin/python3 python \
	  && pip3 install --upgrade pip \
	  && pip3 install mysqlclient
	 
	sudo apt-get upgrade
	
	# -----------------------------------
	#  Setup Docker  (Ubuntu)
	# -----------------------------------
	if ! [ -x "$(command -v docker)" ]; then
	  echo "Installing docker..."
	  sudo apt install -y docker.io
	  sudo systemctl start docker
	  sudo systemctl enable docker
	else
	  echo "docker is already installed"
	fi
}


setup_Microk8s()
{
	# -----------------------------------
	#  Setup microk8s with snap (Ubuntu)
	# -----------------------------------
	if ! [ -x "$(command -v microk8s.kubectl)" ]; then
	  echo "Installing microk8s.kubectl..."
	  sudo snap install --channel=$K8S_VERSION/stable microk8s --classic
	  sudo microk8s.start
	  sudo microk8s.enable dns storage dashboard
	  sudo microk8s.enable gpu registry  # Optional
	  sudo microk8s.status --wait-ready
	  sudo usermod -a -G microk8s $USER
	  sudo mkdir -p $HOME/.kube
	  sudo chown -R $USER:$USER $HOME/.kube
	  sudo microk8s.kubectl config view --raw > $HOME/.kube/config
	else
	  sudo microk8s.start
	  echo "microk8s.kubectl is already installed"
	fi
	
	# -----------------------------------
	#  setup multi node cluster setup (Ubuntu)
	# -----------------------------------
	#get JOIN_NODE_ID
	JOIN_NODE_ID="$(microk8s.add-node | head -1 | sed -e "s/Join node with: //g")"
	echo "${JOIN_NODE_ID}"
	SCRIPT="sudo snap install --channel=$K8S_VERSION/stable microk8s --classic;sudo $JOIN_NODE_ID"
	echo "installation command"
	echo $SCRIPT
	for HOSTNAME in ${HOSTS} ; do
	    echo "trying to install microk8s in ${HOSTNAME}"
	    ssh -t -o StrictHostKeyChecking=no ${HOSTNAME} "${SCRIPT}"
	done
}

setup_Minikube_Kvm()
{
	# -----------------------------------
	#  Setup KVM2 Driver  (Ubuntu)
	# -----------------------------------
	if ! [ -x "$(command -v docker-machine-driver-kvm2)" ]; then
	  echo "Installing docker-machine-driver-kvm2..."
	  sudo apt-get -y install qemu-kvm libvirt-bin virt-top  libguestfs-tools virtinst bridge-utils
	  curl -LO https://storage.googleapis.com/minikube/releases/latest/docker-machine-driver-kvm2
	  chmod +x docker-machine-driver-kvm2
	  sudo mv docker-machine-driver-kvm2 /usr/local/bin/
	else
	  echo "docker-machine-driver-kvm2 is already installed"
	fi
	
	# -----------------------------------
	#  Setup Kubectl  (Ubuntu)
	# -----------------------------------
	if ! [ -x "$(command -v kubectl)" ]; then
	  echo "Installing kubectl..."
	  curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
	  chmod +x ./kubectl
	  sudo mv ./kubectl /usr/local/bin/kubectl
	else
	  echo "kubectl is already installed"
	fi
	
	# -----------------------------------
	#  Setup MiniKube  (Ubuntu)
	# ----------------------------------- 
	if ! [ -x "$(command -v minikube)" ]; then
	  echo "Installing minikube..."
	  curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
	  chmod +x minikube
	  sudo mv minikube /usr/local/bin/
	else
	  echo "minikube is already installed"
	fi
}

#Install Common Operation
sudo bash -c "$(declare -f commonOpe); commonOpe"

echo "Enter cluter type"
read CLUSTER_TYPE
case $CLUSTER_TYPE in
	microk8s)
	    echo "Enter K8s version"
		read K8S_VERSION
		echo "Enter worker nodes info (Sample: worker1@192.168.122.156 worker2@192.168.122.154)"
		read HOSTS
		sudo bash -c "$(declare -f setup_Microk8s); setup_Microk8s"
		dialog --title "Installed microk8s" --clear --msgbox "Microk8s successfully installed: \n\n$(microk8s.status)" 20 100
		;;
	minikube) 
	    echo "Enter number of cpu cores"
	    read CPU
		echo "Enter memory in MB"
	    read MEMORY
	    sudo bash -c "$(declare -f setup_Minikube_Kvm); setup_Minikube_Kvm"
		echo "Configuring minikube..."
	    minikube config set ShowBootstrapperDeprecationNotification false
	    minikube config set WantUpdateNotification false
	    minikube config set WantReportErrorPrompt false
	    minikube config set WantKubectlDownloadMsg false
	    dialog --title "Installed Minikube" --clear --msgbox "Minikube successfully installed: \nMinikube ip \n $(minikube ip)" 20 100
	    echo "Starting minikube..."
		minikube config set vm-driver kvm2
		minikube start --cpus $CPU --memory $MEMORY set vm-driver kvm2
		;;
	*) 
	    echo "unknown cluster type. can u choose microk8s or minikube"
		;;
  esac
