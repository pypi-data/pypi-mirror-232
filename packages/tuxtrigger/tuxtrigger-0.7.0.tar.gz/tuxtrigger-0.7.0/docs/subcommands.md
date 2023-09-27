# TuxTrigger Subcommands

## Run mode yaml/squad

TuxTrigger checks out repositories by comparing fingerprint from git.kernel.org manifest file and/or git sha value.

There are two options where those values are stored in order to compare.

1. SQUAD - recommended sha-compare argument is set by default to squad, fingerprint and git sha are stored in squad_project metadata

```shell
tuxtrigger path/to/config.yaml --sha-compare=squad
```

2. YAML fingerprint and git-sha values are stored in .yaml file created by tuxtrigger in share folder

```shell
tuxtrigger path/to/config.yaml --sha-compare=yaml
```



## Output File

TuxTrigger is storing the state of each repositories in yaml file.
To declare a custom output file path type:

```shell
tuxtrigger path/to/config.yaml --output path/to/output.yaml
```
## Submit mode

By using ```--submit``` argument you are able to change behavior of tuxtrigger

- ```never``` - tuxtrigger will not submit build, plan to tuxsuite and will not send information to SQUAD
- ```change``` - (default value) - tuxtrigger will submit build, plan to tuxsuite and will send information to SQUAD only when change occurred in tracked repository
- ```always``` - tuxtrigger will submit build, plan to tuxsuite and will send information to SQUAD for every tracked branch from config file. Regardless of changes.

```shell 
tuxtrigger path/to/config.yaml --submit=always
```

## Pre submit script

When tracked repository has changed tuxtrigger can invoke your custom script. 
By passing ```--pre-submit``` argument you are able to define the path to script, which receives three values from tuxtrigger

1. repository url
2. branch name
3. new SHA value

```shell 
tuxtrigger path/to/config.yaml --pre-submit path/to/script.sh
```
## Disabling Tuxplan submit

Tuxtrigger can be used without sending a plan file to tuxsuite, by adding an argument ```--plan-disabled```
With that option tuxtrigger will check repositories for changes and can invoke the script if repo has changed.
After script execution tuxtrigger will submit new sha/fingerprint data to squad project.
(even when tuxplan option is disabled tuxtrigger will still invoke tuxsuite build for receiving ‘git_describe’ value).

```shell 
tuxtrigger path/to/config.yaml --plan-disabled
```

## Generate config

Argument ```--generate-config``` invoke tuxtrigger dry-run to prompt the result of generating configuration from config.yaml file. (also, you can check if regex value set in config file matches any branches from tracked repository)

```shell 
tuxtrigger path/to/config.yaml --generate-config
```

## Json output

```--json-out``` argument ables setting the path for json output file generated when plan is successfully submitted to tuxsuite

```shell
tuxtrigger path/to/config.yaml --json-out path/to/file.json
```

## Log File

To declare custom path for log file type:

```shell
tuxtrigger path/to/config.yaml --log-file path/to/log-file.txt
```

## Change Log Level

By default TuxTrigger log level is set to: info
You can adjust log level by choosing one of the levels (debug, info, warn, error)

```shell
tuxtrigger path/to/config.yaml --log-level=warn
```

## TuxSuite Plan Folder

All the plans should be in one directory:

```shell
tuxtrigger path/to/config.yaml --plan path/to/plan-folder
```

## Current version

```shell
tuxtrigger -v
```

## Help

```shell
tuxtrigger --help
```

