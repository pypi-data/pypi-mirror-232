<img src=".github/images/logo.png" width="200" height="200" />

![version](https://img.shields.io/pypi/v/rdsmon?color=%2342f54b&label=rdsmon&style=flat-square)
[![codecov](https://codecov.io/gh/symonk/rdsmon/branch/main/graph/badge.svg)](https://codecov.io/gh/symonk/rdsmon)
[![docs](https://img.shields.io/badge/documentation-online-brightgreen.svg)](https://symonk.github.io/rdsmon/)

# rdsmon
commandline tool for monitoring aws RDS instances

-----

## Quick Start

The requirements for using `rdsmon` are relatively straight forward, however you will need:

#### Installation
Install the tool - `pip install rdsmon` (to install the latest version)

#### Authentication
Typically you require an access token for a user that is configured for rds accessibility using
aws `IAM` roles.  Once your user has been created, you will require an `access key` and this
should be either configured on disk, or exposed to the environment running `rdsmon`.  It is
completely unadvised to user the `root` user and the account running the tool should have as
minimal permissions as possible.  The `IAM` capabilities required by the tool are:

 * Todo

 **Important**: Properly configured IAM roles/users should be in place, tokens should be kept secure,
 under no circumstances should you share them with anybody.  `rdsmon` utilises the same mechanisms
 by the `boto3` aws SDK for credential detection and usage.

 To better understand IAM user and policies, please refer to:

 [AWS IAM user creation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console)

 [AWS Access Tokens](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey)


##### Configuration on disk

Once you have appropriate `IAM` roles and have created an `access_key`, these should be stored in:

`~/.aws/credentials`

```console
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

You may also want to add a default region to the aws configuration file, this should be set in:

`~/.aws/config`

```console
[default]
region=us-east-1
```

-----

## Monitoring an RDS instance

Todo

-----

## Contributing to rdsmon

Ensure you have `python3.11+` installed and `poetry`:

```console
git clone https://github.com/symonk/rdsmon
cd rdsmon
poetry shell
poetry install
 ```

This will create an `editable` install, you can point your `IDE` to the virtualenv output by `poetry shell` and begin contributing.

Linting the code is done via `tox -e linting`, additionally `pre-commit install` will run the linter before committing automatically.

`tox -e py311` will run all tests against `python3.11`

-----