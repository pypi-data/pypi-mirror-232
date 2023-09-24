# support-toolbox
A suite of CLI tools for the support team contained within a Python package.

## Current Release
[Version 0.2.8](https://pypi.org/manage/project/support-toolbox/releases/)

[Support Toolbox Guide](https://dataworld.atlassian.net/wiki/spaces/CX/pages/1601765417/Support+Toolbox+Guide)


## Purpose
The `support-toolbox` PyPi package is a collection of CLI tools designed to simplify and automate tasks by abstracting from direct interaction with APIs and manual processes. Currently, the toolbox supports automating:
```
Available tools:
1. upload_latest_jar
2. create_service_accounts
3. delete_users
4. revert_soft_delete
5. clear_user_layer
6. deploy_integrations
7. deploy_browse_card
```


## Installation Guide
**Install Python**

1. Install [Python](https://www.python.org/downloads/) on your computer and select the option to add Python to your system's PATH.

**Setting up a Virtual Environment**

2. Create a Python virtual environment using `python` or `python3`. Activate the environment, being sure to `cd` into the directory that was created if needed: 
```bash
python3 -m venv st-venv
```
```bash
source bin/activate
```

**Install Package**

3. Install the `support-toolbox` package from PyPI using `pip` or `pip3`:
```bash
pip3 install support-toolbox
```

## Usage Guide

1. In your terminal, `cd` into the virtual environment directory you created during installation.
```bash
cd st-venv
```
2. Activate the Virtual Environment:
```bash
source bin/activate
```

**Run the CLI Tool**

3. Run the CLI tool from your terminal by using the package name:
```bash
support-toolbox
```


## Additional Dependencies
1. Clone [cli](https://github.com/datadotworld/cli) and [integration-templates](https://github.com/datadotworld/integration-templates) to the following directories:
```bash
git clone YOUR_CLI_SSH_URL ~/.dw/cli
```
```bash
git clone YOUR_INTEGRATION_TEMPLATES_SSH_URL ~/
```
2. Configure your systems path to include the `cli` file
```bash
export PATH=${PATH}:${HOME}/.dw/cli/bin
```

## Using a Tool for the First Time
When using these tools for the first time, you will encounter two types of tokens: permanent and runtime.

### Permanent Tokens

During the initial setup, you'll be prompted to provide these tokens for specific tools. If you make a mistake during this setup, don't worry; you can reset your tokens.

To reset your tokens:

1. Open a terminal.
2. Use the `cd` command to navigate to your Home directory:

  ```bash
   cd ~
   ```
3. Run the following command to reset your tokens:


  ```bash
  rm -rf .tokens.ini
  ```
This command will remove the token file, allowing you to reconfigure your tokens when you launch the tool again.

