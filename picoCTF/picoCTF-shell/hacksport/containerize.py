"""
Containerize

Functionality to deploy existing hacksport compatible challenges within a
docker container. Intended to serve as a compatibility layer to "lift" legacy
challenges into a fully isolated environment like DockerChallenge.

This is intended as a replacement for the existing deploy functionality. For
example, rather than "deploying" a challenge instance, you would "containerize"
it.
"""

import glob
import json
import logging
import os
import pathlib
import shutil

from hacksport.docker import DockerChallenge
from hacksport.status import get_all_problem_instances
from hacksport.deploy import (
        deploy_init,
        generate_staging_directory,
        update_problem_class,
        STATIC_FILE_ROOT,
        FLAG_FMT)
from shell_manager.util import (
        get_problem,
        get_problem_root,
        sanitize_name,
        DEPLOYED_ROOT)

REPO_NAME = "shellmanager"

logger = logging.getLogger(__name__)

def containerize_problems(args):
    """ Main entrypoint for problem containerization """

    # determine what we are deploying
    problem_names = args.problem_names
    if args.instances:
        instance_list = args.instances
    else:
        instance_list = list(range(0, args.num_instances))

    logger.debug(f"Containerizing: {problem_names} {instance_list}")

    # build base images required
    ensure_base_images()

    deploy_init(contain=True)
    flag_fmt = args.flag_format if args.flag_format else FLAG_FMT

    for name in problem_names:
        if not os.path.isdir(get_problem_root(name, absolute=True)):
            logger.error(f"'{name}' is not an installed problem")
            continue

        logger.debug(f"Problem  : {name}")
        src = get_problem_root(name, absolute=True)
        metadata = get_problem(src)

        cur_instances = [i["instance_number"] for i in get_all_problem_instances(name)]
        logger.debug(f"Existing : {cur_instances}")

        origwd = os.getcwd()
        for instance in instance_list:
            if instance in cur_instances:
                logger.warn(f"Instance already deployed: {instance}")
                continue

            logger.debug(f"Instance : {instance}")

            # copy source files to a staging directory and switch to it
            staging = generate_staging_directory(problem_name=name, instance_number=instance)
            dst = os.path.join(staging,"_containerize")
            shutil.copytree(src, dst)
            os.chdir(dst)

            # build the image
            containerize(metadata, instance, flag_fmt)

        # return to the orginal directory
        os.chdir(origwd)

def containerize(metadata, seed, flag_fmt):
    logger.info(f"containerize: {metadata['name']}")

    if os.path.isfile("Dockerfile"):
        logger.error("Error: cannot containerize, problem already contains a Dockerfile")
        return None

    # Add a Dockerfile to support shiming the challenge deploy
    dockerfile = os.path.join(os.path.dirname(__file__), "static", "docker", "Dockerfile.containerize")
    shutil.copyfile(dockerfile, "Dockerfile")

    # Use DockerChallenge to shim a deployment within a container. The actually
    # challenge will be built standard class within the image. Load with
    # default variables and configuration settings
    Problem = update_problem_class(DockerChallenge, metadata, "", "", "")

    builder = Problem()

    builder.problem_name = sanitize_name(metadata["name"])

    # standard DockerChallenge build sequence
    builder.initialize()
    builder.initialize_docker({"SEED": str(seed), "FORMAT": flag_fmt})

    # fetch static downloads from image
    html_static = os.path.join(builder.web_root, STATIC_FILE_ROOT)
    builder.copy_from_image(html_static)

    # Copy static downloads to local HTTP server
    static = glob.glob(os.path.join(STATIC_FILE_ROOT,"*"))
    if len(static) > 1:
        logger.warn(f"more than one static dir for containerized instance: {static}")
    for src in static:
        dst = os.path.join(html_static, os.path.basename(src))
        # remove target directory (not always cleaned/removed on undeploy)
        if os.path.isdir(dst):
            logger.warn(f"removing stale static directory: {dst}")
            shutil.rmtree(dst)
        logger.debug(f"moving {src} to {html_static}")
        shutil.move(src, html_static)

    # fetch instance json from image
    builder.copy_from_image(DEPLOYED_ROOT)
    local = os.path.join(os.path.basename(DEPLOYED_ROOT),"**","*.json")
    deployed = glob.glob(local, recursive=True)
    if len(deployed) != 1:
        logger.error("Error challenge failed to deploy in a container")
        return None

    # load instance to allow patching
    instance = None
    with open(deployed[0]) as instance_json:
        instance = json.load(instance_json)

    # add DockerChallenge style fields
    instance["docker_challenge"] = True
    instance["instance_digest"] = builder.image_digest
    instance["port_info"] = {n: p.dict() for n, p in builder.ports.items()}

    # remove invalid fields
    instance["service"] = None
    instance["server"] = None   # shell only knows internal docker host
    if "socket" in instance:
        del instance["socket"]
    if "port" in instance:
        del instance["port"]

    # hint to front end
    instance["containerize"] = True

    # write patched instance json to "register" it with shell_manager
    json_dst = os.path.join(*pathlib.Path(deployed[0]).parts[1:])
    dst = os.path.join(DEPLOYED_ROOT, json_dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst,'w') as out:
        json.dump(instance, out)


# TODO: add check if images exist
# TODO: add warning on first build
# TODO: add option to skip/force rebuild
def ensure_base_images():
    """Build the base image that 'containerized' challenges will be built on"""

    origwd = os.getcwd()
    docker_files = os.path.join(os.path.dirname(__file__), "static", "docker")
    os.chdir(docker_files)

    images = [("base", "Dockerfile.base", "."),
            ("hacksport", "Dockerfile.hacksport", "/picoCTF-env"),
            ("shellmanager", "Dockerfile.config", "/opt/hacksports")]

    for build in images:
        name, dockerfile, context = build
        # Use existing DockerChallenge infrastrucutre to consistently build images.
        builder = DockerChallenge()
        builder.image_name = f"{REPO_NAME}/{name}"

        # Copy Dockerfile into context. While the docker cli allows a seperate
        # -f, the SDK would require building a custom context.
        dockerfile_tmp = os.path.join(context, dockerfile)
        clean = False
        try:
            shutil.copyfile(dockerfile, dockerfile_tmp)
        except shutil.SameFileError:
            clean = True

        # build the image
        img = builder._build_docker_image(
                build_args={},
                timeout=600,
                labels={},
                dockerfile=dockerfile,
                context=context)

        if img is None:
            logger.error(f"Failed to build base image: {builder.image_name}")
            return False
        else:
            logger.debug(f"{builder.image_name} built: {img.id}")

        # Clean up the temporary, in context, Dockerfile.
        if not clean:
            os.remove(dockerfile_tmp)

    # Resore working directory
    os.chdir(origwd)
