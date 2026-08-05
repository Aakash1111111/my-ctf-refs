"""
Challenge template to deploy instances in on-demand containers
"""

import logging
import os
import tarfile
import tempfile
import sys

import docker

from hacksport.problem import Challenge
from shell_manager.util import sanitize_name

logger = logging.getLogger(__name__)

class DockerChallenge(Challenge):
    """Challenge based on a docker container."""
    ports = {}

    def __init__(self):
        """ Connnects to the docker daemon"""
        # will be used as the tag on the docker image
        if hasattr(self, "name"):
            self.problem_name = sanitize_name(self.name)
        else:
            self.problem_name = "problem"
        # use an explicit remote docker daemon per the configuration
        try:
            tls_config = docker.tls.TLSConfig(
                ca_cert=self.docker_ca_cert,
                client_cert=(self.docker_client_cert, self.docker_client_key),
                verify=True)

            self.client = docker.DockerClient(base_url=self.docker_host, tls=tls_config)
            self.api_client = docker.APIClient(base_url=self.docker_host, tls=tls_config)
            logger.debug("Connecting to docker daemon with config")

        # Docker options not set in configuration so use the environment to
        # configure (could be local or remote)
        except AttributeError:
            logger.debug("Connecting to docker daemon with env")
            self.client = docker.from_env()

        # throws an exception if the server returns an error: docker.errors.APIError
        self.client.ping()

    def setup(self):
        # Challenge author should override setup to do additional setup takes
        # or pass arguments to the build process.
        self.initialize_docker({})

    def initialize_docker(self, build_args, timeout=600):

        self.image_name = 'challenges:{}'.format(self.problem_name)

        logger.debug("Building docker image: {}".format(self.image_name))

        labels= {'problem': self.problem_name}
        img = self._build_docker_image(build_args, timeout, labels)
        if img is None:
            raise Exception('Unable to build docker image')

        self.image_digest = img.id

        try:
            exposed_ports = img.attrs["Config"]["ExposedPorts"].keys()
        except KeyError:
            raise Exception("Dockerfile must expose at least 1 port")

        # Ensure all ports are represented and convert to ints, e.g. "5555/tcp"
        image_ports = [int(p.split("/")[0]) for p in exposed_ports]
        for p in image_ports:
            if p not in self.ports:
                self.ports[p] = Plain("challenge")

        logger.debug("Built image, digest: {}".format(self.image_digest))

    def _build_docker_image(self, build_args, timeout, labels={}, dockerfile="Dockerfile", context="."):
        """
        Run a docker build
        Args:
            build_args: dict of build arguments to pass to `docker build`
            timeout: how long to allow for the build

        Returns: boolean success
        """

        logger.debug(f"Building: {self.image_name} from context: {context}")
        try:
            img, logs = self.client.images.build(
                dockerfile=dockerfile,
                path=context,
                tag=self.image_name,
                buildargs=build_args,
                labels=labels,
                timeout=timeout)
        except docker.errors.BuildError as e:
            logger.error("Docker Build Error: " + e.msg)
            for entry in e.build_log:
                if 'stream' in entry:
                    line = entry['stream'].strip()
                else:
                    line = entry
                logger.debug(line)
            return None
        except docker.errors.APIError as e:
            logger.error("Docker API Error: " + e.explanation)
            return None

        return img

    def copy_from_image(self, src):
        """
        Copy a file/folder from within a build image to the local filesystem.
        Can only be run after the challenge image is created with
        `initialize_docker`.
        Args:
            src : path of file or folder within the challenge image
        """

        cwd = os.getcwd()
        logger.debug("Copy: {} from container to {}".format(src, cwd))
        try:
            cid = self.api_client.create_container(self.image_name)
            c = self.client.containers.get(cid)
            strm, stat = c.get_archive(src)

            with tempfile.NamedTemporaryFile('wb+',suffix=".tar") as tf:
                for chunk in strm:
                    tf.write(chunk)
                tf.flush()
                tf.seek(0)

                with tarfile.open(fileobj=tf) as tar:
                    res = tar.extractall()

            self.api_client.remove_container(cid)
        except Exception:
            logger.error("Fatal error in copy_from_image", exc_info=True)
            raise



# Utility classes to handle templating of ports. Will get formated twice in the
# following order host, then port (this is why the extra {} in the fmt string)
class HTTP():
    def __init__(self, desc, path="", link_text=""):
        self.desc = desc
        self.path = path
        self.link_text = link_text

    def dict(self):
        url = "http://{host}:{{port}}" + self.path
        if self.link_text == "":
            link = "<a href='{}' target='_blank'>{}</a>".format(url, url)
        else:
            link = "<a href='{}' target='_blank'>{}</a>".format(url, self.link_text)
        return {"fmt": link, "desc": self.desc}

class Netcat():
    def __init__(self, desc):
        self.desc = desc

    def dict(self):
        return {"fmt": "<code>nc {host} {{port}}</code>", "desc": self.desc}

class Plain():
    def __init__(self, desc):
        self.desc = desc

    def dict(self):
        return {"fmt": "<code>{host}:{{port}}</code>", "desc": self.desc}

class Custom():
    def __init__(self, fmt, desc):
        self.desc = desc
        self.fmt = fmt

    def dict(self):
        return {"fmt": self.fmt, "desc": self.desc}
