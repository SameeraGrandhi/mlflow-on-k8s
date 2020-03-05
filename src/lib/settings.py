'''
Created on 03-Mar-2020

@author: srinivasan
'''
import logging.config
import os
import time

from src.lib import utils

# project Base Directory Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

current_milli_time = lambda: int(round(time.time() * 1000))

config = {
  "namespace": "mlflowonkube",
  "cluster": "minikube",
  "master_ip":"172.17.1.229",
  "kubectl":"microk8s.kubectl",
  "kube_context":"minikube",
  "mysql": {
    "user":"pramati_new1",
    "password": "password123",
    "dbname":"mlflow",
    "port":"3306",
    "nodePort":"30036",
    "mountPath": "/var/lib/mysql",
    "storage":"1Gi",
    "isSkip": False
  },
  "mlflow": {
    "port":"5002",
    "nodePort":"30035",
    "mountPath": "/mnt/mlflow",
    "storage":"1Gi",
    "docker_image": "172.17.1.229:32000/mlflow-server:registry",
    "isSkip": False
  },
  "nexsus": {
    "mountPath": "/mnt/nexsus",
    "docker_image": "",
    "isSkip": False
  },
  "flask": {
    "mountPath": "/mnt/mlflow",
    "nodePort":"30091",
    "docker_image": "172.17.1.229:32000/mlflow-flask:registry",
    "run_id":"fe25e92156fa4b10b6b3a165a31ce676"
  },
  "kube_job": {
    "projectname":"mlflow_on_kubernetes",
    "mountPath": "/mnt/mlflow",
    "entry_cmd":"train.py --alpha {alpha} --l1-ratio {l1_ratio}",
    "docker_image": "172.17.1.229:32000/mlflow-flask:registry",
    "limit_mem":"512Mi",
    "requests_mem":"256Mi",
    "maintainer" :"srinivasan.ramalingam@imaginea.com"
  }
}

# OutFile Generated Path
OUTPUT_DIR = utils.createDirIfNotExist(os.path.join(BASE_DIR,
                                                 "output", str(current_milli_time())))

# logging configuration information
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': utils.createDirIfNotExist(os.path.join(BASE_DIR,
                'logs/service_helper.log'))
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    }
})

