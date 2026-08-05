import json
import logging
import os
import shutil
import socket
from os.path import join

from hacksport.operations import execute
from shell_manager.util import (
    BUNDLE_ROOT,
    DEPLOYED_ROOT,
    get_problem,
    get_problem_root,
    SHARED_ROOT,
    PROBLEM_ROOT,
    STAGING_ROOT,
    get_pid_hash,
    sanitize_name,
    get_bundle,
    get_bundle_root,
    release_lock,
)

logger = logging.getLogger(__name__)


def get_all_problems():
    """ Returns a dictionary of name-hash:object mappings """

    problems = {}
    if os.path.isdir(PROBLEM_ROOT):
        for name in os.listdir(PROBLEM_ROOT):
            try:
                problem = get_problem(get_problem_root(name, absolute=True))
                problems[name] = problem
            except FileNotFoundError as e:
                pass
    return problems


def get_all_bundles():
    """ Returns a dictionary of name:object mappings """

    bundles = {}
    if os.path.isdir(BUNDLE_ROOT):
        for name in os.listdir(BUNDLE_ROOT):
            try:
                bundle = get_bundle(get_bundle_root(name, absolute=True))
                bundles[name] = bundle
            except FileNotFoundError as e:
                pass
    return bundles


def get_all_problem_instances(problem_name):
    """
    Returns a list of instances for a given problem

    Args:
        problem_name: Sanitized problem name with hash.
    """

    instances = []
    instances_dir = join(DEPLOYED_ROOT, problem_name)
    if os.path.isdir(instances_dir):
        for name in os.listdir(instances_dir):
            if name.endswith(".json"):
                try:
                    instance = json.loads(open(join(instances_dir, name)).read())
                except Exception as e:
                    continue

                instances.append(instance)

    return instances


def publish(args):
    """ Main entrypoint for publish """

    problems = get_all_problems()
    bundles = get_all_bundles()

    output = {"problems": [], "bundles": []}

    for name_with_hash, problem in problems.items():
        logger.debug("Finding instances of %s", name_with_hash)
        problem["instances"] = get_all_problem_instances(name_with_hash)
        problem["sanitized_name"] = sanitize_name(problem["name"])
        problem["unique_name"] = name_with_hash
        output["problems"].append(problem)

    for _, bundle in bundles.items():
        output["bundles"].append(bundle)

    print(json.dumps(output, indent=2))


def clean(args):
    """ Main entrypoint for clean """
    # remove staging directories
    if os.path.isdir(STAGING_ROOT):
        logger.info("Removing the staging directories")
        shutil.rmtree(STAGING_ROOT)

    # remove lock file
    release_lock()


def status(args):
    """ Main entrypoint for status """

    bundles = get_all_bundles()
    problems = get_all_problems()

    def get_instance_status(instance):
        status = {
            "instance_number": instance["instance_number"],
            "port": instance["port"] if "port" in instance else None,
            "flag": instance["flag"],
        }

        status["connection"] = False
        if "port" in instance:
            port = instance["port"]
            try:
                # XXX: assumes that the challenge is hosted locally
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("localhost", port))
                s.close()
                status["connection"] = True
            except ConnectionRefusedError as e:
                logger.debug(f"instance: {instance['instance_number']} has port: {port} but can't connect")
                pass
        if instance["service"]:
            result = execute(
                ["systemctl", "is-failed", instance["service"]], allow_error=True
            )
        else:
            result = execute(["systemctl", "is-failed"], allow_error=True)
        status["service"] = result.return_code == 1

        if status["port"] is not None and not status["connection"]:
            status["service"] = False

        return status

    def get_problem_status(name_with_hash, problem):
        problem_status = {
            "name": problem["name"],
            "unique_name": problem["unique_name"],
        }
        instances = get_all_problem_instances(name_with_hash)
        instance_statuses = []
        for instance in instances:
            instance_statuses.append(get_instance_status(instance))

        problem_status["instances"] = instance_statuses

        return problem_status

    def print_problem_status(problem, prefix=""):
        def pprint(string):
            print("{}{}".format(prefix, string))

        pprint(
            "* [{}] {} ({})".format(
                len(problem["instances"]), problem["name"], problem["unique_name"]
            )
        )

        if args.all:
            for instance in problem["instances"]:
                pprint("   - Instance {}".format(instance["instance_number"]))
                pprint("       flag: {}".format(instance["flag"]))
                pprint("       port: {}".format(instance["port"]))
                pprint(
                    "       service: {}".format(
                        "active" if instance["service"] else "failed"
                    )
                )
                pprint(
                    "       connection: {}".format(
                        "online" if instance["connection"] else "offline"
                    )
                )

    def print_bundle(bundle, path, prefix=""):
        def pprint(string):
            print("{}{}".format(prefix, string))

        pprint("* {} ({})".format(bundle["name"], path))

    def get_bundle_status(bundle):
        problem_statuses = []
        for name_with_hash in bundle["problems"]:
            problem = problems.get(name_with_hash)
            problem_statuses.append(get_problem_status(name_with_hash, problem))
        bundle["problems"] = problem_statuses
        return bundle

    if args.problem is not None:
        problem = problems.get(args.problem, None)
        if problem is None:
            print('Could not find problem "{}"'.format(args.problem))
            return

        problem_status = get_problem_status(args.problem, problem)
        if args.json:
            print(json.dumps(problem_status, indent=4))
        else:
            print_problem_status(problem_status, prefix="")

    elif args.bundle is not None:
        bundle = bundles.get(args.bundle, None)
        if bundle is None:
            print('Could not find bundle "{}"'.format(args.bundle))
            return

        if args.json:
            print(json.dumps(get_bundle_status(bundle), indent=4))
        else:
            print_bundle(bundle, args.bundle, prefix="")

    else:
        return_code = 0
        if args.json:
            result = {
                "bundles": bundles,
                "problems": list(
                    map(lambda tup: get_problem_status(*tup), problems.items())
                ),
            }
            print(json.dumps(result, indent=4))
        elif args.errors_only:
            for path, problem in problems.items():
                problem_status = get_problem_status(path, problem)

                # Determine if any problem instance is offline
                for instance_status in problem_status["instances"]:
                    if not instance_status["service"]:
                        print_problem_status(problem_status, prefix="  ")
                        return_code = 1
        else:
            print("** Installed Bundles [{}] **".format(len(bundles)))
            shown_problems = []
            for path, bundle in bundles.items():
                print_bundle(bundle, path, prefix="  ")

            print("** Installed Problems [{}] **".format(len(problems)))
            for path, problem in problems.items():
                problem_status = get_problem_status(path, problem)

                # Determine if any problem instance is offline
                for instance_status in problem_status["instances"]:
                    if not instance_status["service"]:
                        return_code = 1

                print_problem_status(problem_status, prefix="  ")

        if return_code != 0:
            print("WARNING: Some instances offline. Run with -e to see failing instances")
            exit(return_code)
