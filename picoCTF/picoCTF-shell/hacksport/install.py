"""
Handles installation of problems onto the shell server(s).

When a problem is _installed_, this means that the problem source files have
been parsed and converted into a debian package stored at
SHARED_ROOT/debs.

Additionally, the source files of the problem will be copied (via the debian
package) into SHARED_ROOT/sources.

The problem will then appear in the list of available problems, which is
determined by traversing the SHARED_ROOT/sources directory.

When this problem is _deployed_, shell_manager will attempt to reinstall the
debian package first, in case the problem has dependencies that have not
been fulfilled on the current shell server.
"""
from ast import literal_eval
import logging
import subprocess
import os
import shutil
import json
from shell_manager.package import package_problem
from shell_manager.util import (
    get_problem,
    DEB_ROOT,
    FatalException,
    join,
    SHARED_ROOT,
    get_problem_root_hashed,
    get_bundle,
    PROBLEM_ROOT,
    BUNDLE_ROOT,
    sanitize_name,
    acquire_lock,
    release_lock,
)
from hacksport.deploy import generate_staging_directory

logger = logging.getLogger(__name__)


def install_problem(problem_path, allow_reinstall=False):
    """
    Install a problem from a source directory.

    Args:
        problem_path: path to the problem source directory
    """
    problem_obj = get_problem(problem_path)
    if (
        os.path.isdir(get_problem_root_hashed(problem_obj, absolute=True))
        and not allow_reinstall
    ):
        logger.error(
            f"Problem {problem_obj['unique_name']} is already installed. You may specify --reinstall to reinstall an updated version from the specified directory."
        )
        return
    logger.info(f"Installing problem {problem_obj['unique_name']}...")

    acquire_lock()

    staging_dir_path = generate_staging_directory(
        problem_name=problem_obj["unique_name"]
    )
    logger.debug(
        f"{problem_obj['unique_name']}: created staging directory"
        + f" ({staging_dir_path})"
    )

    generated_deb_path = package_problem(
        problem_path, staging_path=staging_dir_path, out_path=DEB_ROOT
    )
    logger.debug(f"{problem_obj['unique_name']}: created debian package")

    try:
        subprocess.run(
            "DEBIAN_FRONTEND=noninteractive apt-get -y install "
            + f"--reinstall {generated_deb_path}",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
        )
    except subprocess.CalledProcessError:
        logger.error("An error occurred while installing problem packages.")
        raise FatalException
    finally:
        release_lock()
    logger.debug(f"{problem_obj['unique_name']}: installed package")
    logger.info(f"{problem_obj['unique_name']} installed successfully")


def find_problem_sources(root_path):
    """
    Find all problem source directories that exist under the given root.

    Any directory with a problem.json is considered a source directory.

    Args:
        root_path: the problem directory
    Returns:
        A list of problem paths.
    """
    problem_source_paths = []
    for dir_path, _, files in os.walk(root_path):
        if "problem.json" in files and "__staging" not in dir_path:
            problem_source_paths.append(dir_path)
    return problem_source_paths


def install_problems(args):
    """
    Entrypoint for problem installation.

    Allows for installation of multiple/nested problem source folders.
    """
    if not args.problem_paths:
        logger.error("No problem source path(s) specified")
        raise FatalException

    problem_paths = []
    for base_path in args.problem_paths:
        problem_paths.extend(find_problem_sources(base_path))

    for problem_path in problem_paths:
        install_problem(problem_path, (args.reinstall is not None))


def uninstall_problem(problem_name):
    """
    Uninstalls a given problem, which means that the generated debian package
    and source files within the SHARED_ROOT directory are removed.

    An uninstalled problem will no longer appear when listing problems, even
    if deployed instances remain (undeploying all instances of a problem
    before uninstallation is recommended.)

    Additionally, any assigned instance ports for the problem will be
    removed from the port map.
    """
    acquire_lock()

    try:
        # Remove .deb package used to install dependencies on deployment
        os.remove(join(DEB_ROOT, problem_name + ".deb"))

        # Remove problem source used for templating instances
        shutil.rmtree(join(PROBLEM_ROOT, problem_name))

        # Remove any ports assigned to this problem from the port map
        port_map_path = join(SHARED_ROOT, "port_map.json")
        with open(port_map_path, "r") as f:
            port_map = json.load(f)
            port_map = {literal_eval(k): v for k, v in port_map.items()}

        port_map = {k: v for k, v in port_map.items() if k[0] != problem_name}

        with open(port_map_path, "w") as f:
            stringified_port_map = {repr(k): v for k, v in port_map.items()}
            json.dump(stringified_port_map, f)

    except Exception as e:
        logger.error(f"An error occurred while uninstalling {problem_name}:")
        logger.error(f"{str(e)}")
        raise FatalException

    logger.info(f"{problem_name} removed successfully")
    release_lock()


def uninstall_problems(args):
    """
    Entrypoint for problem removal.

    All shell servers' instances of a problem should be undeployed prior
    to use, as this command will remove the problem source files and
    its listing within shell_manager, stranding any remaining instances.
    """
    if not args.problem_names:
        logger.error("No problem name(s) specified")
        raise FatalException

    for problem_name in args.problem_names:
        uninstall_problem(problem_name)


def install_bundle(args):
    """
    "Installs" a bundle (validates it and stores a copy).

    "Bundles" are just JSON problem unlock weightmaps which are exposed to
    and used by the web server.

    All problems specified in a bundle must already be installed.
    """
    if not args.bundle_path:
        logger.error("No problem source path specified")
        raise FatalException
    bundle_path = args.bundle_path
    bundle_obj = get_bundle(bundle_path)

    if os.path.isdir(join(BUNDLE_ROOT, sanitize_name(bundle_obj["name"]))):
        logger.error(
            f"A bundle with name {bundle_obj['name']} is " + "already installed"
        )
        raise FatalException

    for problem_name, info in bundle_obj["dependencies"].items():
        if not os.path.isdir(join(PROBLEM_ROOT, problem_name)):
            logger.error(
                f"Problem {problem_name} must be installed "
                + "before installing bundle"
            )
            raise FatalException
        for dependency_name in info["weightmap"]:
            if not os.path.isdir(join(PROBLEM_ROOT, dependency_name)):
                logger.error(
                    f"Problem {dependency_name} must be installed "
                    + "before installing bundle"
                )
                raise FatalException

    bundle_destination = join(
        BUNDLE_ROOT, sanitize_name(bundle_obj["name"]), "bundle.json"
    )
    os.makedirs(os.path.dirname(bundle_destination), exist_ok=True)
    shutil.copy(bundle_path, bundle_destination)
    logger.info(f"Installed bundle {bundle_obj['name']}")


def uninstall_bundle(args):
    """
    Uninstall a bundle by deleting it from the shell servers.

    Problems referenced within the bundle are not affected.
    """
    if not args.bundle_name:
        logger.error("No bundle name specified")
        raise FatalException
    bundle_name = args.bundle_name

    bundle_dir = join(BUNDLE_ROOT, sanitize_name(bundle_name))
    if not os.path.isdir(bundle_dir):
        logger.error(f"Bundle '{bundle_name}' is not installed")
    else:
        shutil.rmtree(bundle_dir)
        logger.info(f"Bundle '{bundle_name}' successfully removed")
