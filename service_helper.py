'''
Created on 02-Mar-2020

@author: srinivasan
'''
from abc import ABC, abstractmethod
import click
import docker
from docker.errors import BuildError
from jinja2 import Template
import logging
import os 
from retrying import retry
from sqlalchemy import create_engine
from time import sleep

from src.lib import settings, utils

logger = logging.getLogger(__name__)



class DockerClient(object):
    
    def __init__(self):
        self.client = docker.from_env()
    
    """
    Build Docker Image
    """

    def buildDockerImg(self, path, tag):
        try:
            logger.info("build Docker image with tag {}".format(tag))
            self.client.images.build(tag=tag, forcerm=True, nocache=True,
                                dockerfile='Dockerfile', path=path)
        except BuildError as build_error:
            for chunk in build_error.build_log:
                print(chunk)
            raise build_error

    """
    Pushing Docker image to Docker Registry
    """

    def push_image_to_registry(self, image_tag):
        logger.info("Pushing docker image %s", image_tag)
        for line in self.client.images.push(repository=image_tag,
                                        stream=True, decode=True):
            print(line)
            if 'error' in line and line['error']:
                raise Exception("Error while pushing to docker registry: "
                                         "{error}".format(error=line['error']))
        return self.client.images.get_registry_data(image_tag).id


class MysqlClient(object):
    
    """
    Create User and Give permission to access from remote machine
    """
    sql_query = """CREATE DATABASE IF NOT EXISTS {{mysql.dbname}}
                CREATE USER '{{mysql.user}}'@'%%' IDENTIFIED BY '{{mysql.password}}'
                GRANT ALL PRIVILEGES ON *.* TO '{{mysql.user}}'@'%%' WITH GRANT OPTION
                FLUSH PRIVILEGES"""

    def createUserAndGivePerm(self, conf):
        engine = create_engine(self.getDbUrl(conf), echo=True)
        try:
            conn = engine.connect()
            self.__testConnection(conn)
            for line in Template(self.sql_query)\
            .render(**conf).splitlines():
                conn.execute(line.strip())
        except Exception as e:
            logger.info("Mysql Client Exception {}".format(e))
            raise e
        else:
            if 'conn' in locals():
                conn.close()
            engine.dispose()
    
    def getDbUrl(self, conf):
        url = 'mysql+mysqldb://root:{{mysql.password}}@{{master_ip}}:{{mysql.nodePort}}/mysql'
        return Template(url).render(**conf)

    """
    Test connection
    """

    @retry(stop_max_attempt_number=10,
           wait_random_min=10000, wait_random_max=20000)
    def __testConnection(self, conn):
        conn.execute("select 'OK'")


class IService(ABC):
    
    @abstractmethod
    def prepareAndRun(self):
        pass
    
    @abstractmethod
    def set_next_Service(self, service):
        pass


class Service(IService, DockerClient):

    def __init__(self, service_name, config, cluster):
        super().__init__()
        self.service_name = service_name
        self.config = config
        self.cluster = cluster
        self.docker_path = None
        self._next_service = None
    
    """
    Generate the template
    """

    def template_render(self, yaml_path, subfolder=None):
        self.docker_path = None
        logger.info("template render the files in {} folder"\
                    .format(yaml_path))
        try:
            for i in utils.listdir_fullpath(yaml_path):
                with open(i[0], 'r') as template_file:
                    template = Template(template_file.read())
                output = template.render(**self.config)
                path = os.path.join(settings.OUTPUT_DIR, i[1])
                if subfolder:
                    path = os.path.join(settings.OUTPUT_DIR,
                                        subfolder, os.path.basename(i[1]))
                OUT_FILE = utils.createDirIfNotExist(path)
                if 'Dockerfile' in i[1]:
                    self.docker_path = OUT_FILE
                with open(OUT_FILE, 'w') as outfile:
                    outfile.write(output)
            logger.info("template has been generated in {} service".format(self.service_name))
        except Exception as e:
            logger.error("Exception occurred in template rendering {}".format(e))
            raise e

    @abstractmethod
    def prepareAndRun(self):
        if self._next_service:
            return self._next_service.prepareAndRun()
        return None
    
    def set_next_Service(self, service):
        self._next_service = service
        return service
    
    def deployInkube(self, path):
        cmd = "kustomize build {0} | {1} apply -f -".\
        format(path, self.config['kubectl'])
        logger.info("command {}".format(cmd))
        import subprocess
        import sys
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
        #print(process.stdout.read())
        for _line in process.stdout:
            line=_line.decode('utf-8')
            sys.stdout.write(line)
            if 'error' in line or 'refused' in line:
                process.kill()
                raise Exception("Error while Executing command:{}".format(line))
        process.kill()

    
class MysqlService(Service, MysqlClient):
    
    def __init__(self, config):
        super().__init__("mysql", config,
                         config['cluster'])
    
    def prepareAndRun(self):
        if not self.config['mysql']['isSkip']:
            logger.info("started to create mysql service in our kubernetes cluster")
            self.template_render(os.path.join(settings.BASE_DIR,
                                              "src", "mysql"))
            self.deployInkube(os.path.join(settings.OUTPUT_DIR,
                         "mysql", "overlays", self.cluster))
            # wait for few min
            logger.info("waiting for mysql service up")
            sleep(120)
            # retry and wait
            self.createUserAndGivePerm(self.config)
        return super().prepareAndRun()


class MLFlowService(Service):

    def __init__(self, config):
        super().__init__("mlflowserver", config,
                         config['cluster'])
    
    def prepareAndRun(self):
        if not self.config['mlflow']['isSkip']:
            self.template_render(os.path.join(settings.BASE_DIR,
                                              "src", "mlflowserver"))
            tag = self.config['mlflow']['docker_image']
            
            # build mlflow server Docker Image
            self.buildDockerImg(os.path.dirname(self.docker_path),
                                 tag)
            # Push Docker image from local to Docker Registry
            self.push_image_to_registry(tag)
            # deploy the command in kubernetes
            self.deployInkube(os.path.join(settings.OUTPUT_DIR,
                         "mlflowserver", "overlays", self.cluster))
        return super().prepareAndRun()


class NexusService(Service):
    
    def __init__(self, config):
        super().__init__("nexus", config,
                         config['cluster'])
    
    def prepareAndRun(self):
        if not self.config['nexsus']['isSkip']:
            self.template_render(os.path.join(settings.BASE_DIR,
                                              "src", "nexus"))
            self.deployInkube(os.path.join(settings.OUTPUT_DIR,
                         "nexus", "overlays", self.cluster))
        return super().prepareAndRun()


class FlaskService(Service):
    
    def __init__(self, config):
        super().__init__("flask", config,
                         config['cluster'])
    
    def prepareAndRun(self):
        self.template_render(os.path.join(settings.BASE_DIR,
                                          "src", "flask"))
        self.deployInkube(os.path.join(settings.OUTPUT_DIR,
                     "flask", "overlays", self.cluster))
        return super().prepareAndRun()


class LaunchService(object):
    
    def __init__(self, config):
        self.config = config
    
    """
    Launch all the service
    """

    def launch(self):
        mysql = MysqlService(self.config)
        mlflow = MLFlowService(self.config)
        nexsus = NexusService(self.config)
        mysql.set_next_Service(mlflow).set_next_Service(nexsus)
        mysql.prepareAndRun()


class TemplateGeneration(Service):
    
    def __init__(self, config):
        super().__init__("MlflowTemplateGen", config,
                         config['cluster'])
    
    def prepareAndRun(self):
        self.template_render(os.path.join(settings.BASE_DIR,
                                          "src", "lib", "template", "mlflow"),
                                          self.config['kube_job']['projectname'])
        logger.info("Sample Template generated in {} folder"\
                    .format(os.path.join(settings.OUTPUT_DIR,
                                         self.config['kube_job']['projectname'])))
        return None


@click.command()
@click.option('--setup_platform', is_flag=True, help="Will help us to set platform.")
@click.option('--flask_deploy', is_flag=True, help="Will help us to deploy flask application.")
@click.option('--generate_ml_template', is_flag=True, help="Will help us to generate Mlflow on Kubernetes template.")
def cli(setup_platform, flask_deploy, generate_ml_template):
    logger.info("current output Directory Path {}".format(settings.OUTPUT_DIR))
    if setup_platform:
        conf=settings.config
        import base64
        passw=conf['mysql']['password']
        conf['enc_password']=str(base64.b64encode(passw.encode('utf-8')), 'utf-8')
        LaunchService(conf).launch()
    if flask_deploy:
        FlaskService(settings.config).prepareAndRun()
    if generate_ml_template:
        TemplateGeneration(settings.config).prepareAndRun()


if __name__ == '__main__':
    cli()

