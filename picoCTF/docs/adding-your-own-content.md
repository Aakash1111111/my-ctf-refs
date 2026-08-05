This section will cover how to create your own problems and bundles for the
picoCTF Platform. There are some step-by-step examples that you can
follow along with in the [tutorials](./tutorials/picoprimer-custom-challenge.md).

## Creating a Problem

To create a problem, you must set up a directory with the appropriate files and deploy it
using the shell\_manager utility on the shell server. We will now outline how to do that.

### Problem Specification

A problem specification is a directory consisting of your problem files. The following files
are recognized and used by the shell\_manager.

| File name | Required | Description|
|-----------|----------|------------|
|problem.json| yes | This file will specify the core information about the problem, including the name, category, score, and so forth. The full specification can be found [here](./specs/problem.json.md)|
|challenge.py| yes | This script will specify how problem generation should occur.  The full documentation for setting up this script can be found [here](./specs/challenge.py.md).|
|requirements.txt| no |  Specifies pip requirements for your problem|
|install\_dependencies| no | A script that will be executed after installing your problem.|

Any other files in your problem directory will be deployed as-is.

### Testing Your Problem

When you think your challenge is ready, you should test it before deploying real problem instances.
First install/update your problem by running `sudo shell_manager install <problem-directory>`, then `sudo shell_manager status` to find the name assigned to your installed problem. Then, you can use `sudo shell_manager deploy -d <installed-problem-name>` to generate a test instance of the
problem. This test instance will not have an running services, but all of the files will be
generated and placed in a temporary directory. This deployment directory will be output
by the previous command, so you should verify that it looks as it should.

### Deploying Instances

After verifying the dry-run output, you can run `sudo shell_manager deploy <installed-problem-name>` to deploy an instance of the problem.
Additionally, you can use the `-n` parameter to specify the number of instances to deploy.
To make sure that it is running properly, you can run `sudo shell_manager status`. Your problem will appear in the status list under a sanitized version of the name specified in `problem.json`, which may differ from the name of the source directory you used to deploy it.

### Enabling Problems

Deployed instances/bundles are not automatically enabled on the web server. An admin must first login and visit the Admin Management page. As mentioned in the [set up page](./setup.md), the first account you set up will be the site administrator.
Under the 'Shell Server' tab, problems can be added via the 'Load Deployment' button, and the status of such problems (whether they are loaded or not) can be checked via the 'Check Status' button. 
Problems can then be enabled or disabled for the competitors via the 'Manage Problems' tab.

## Creating a Bundle

You can create a "bundle" of problems, which specifies a map of prerequisites that users must solve before unlocking each problem. All problems specified in the bundle must be installed before the bundle itself can be installed.
Then, create a `bundle.json` file following the specification described [here](./specs/bundle.json.md.

Now, run `sudo shell_manager install-bundle <path-to-bundle.json>` to install your bundle. Installed bundles will appear in the `sudo shell_manager status` output. After loading the deployment from the shell server in the web problem management UI, the problem unlock requirements specified in the bundle will take effect.
