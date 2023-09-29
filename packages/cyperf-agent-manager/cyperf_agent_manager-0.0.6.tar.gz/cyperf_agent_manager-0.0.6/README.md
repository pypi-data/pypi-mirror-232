# cyperf-agent-manager
A simple python script that can ssh into multiple cyperf agents and run some pre-defined commands

[![PyPI - Version](https://img.shields.io/pypi/v/cyperf-agent-manager.svg)](https://pypi.org/project/cyperf-agent-manager)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cyperf-agent-manager.svg)](https://pypi.org/project/cyperf-agent-manager)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)
- [CLI](#cli)
- [Module](#module)

## Installation

```console
pip install cyperf-agent-manager
```

_If `pip` command is not found on your system then use the following commands to install `pip`._

```cosnole
$ wget https://bootstrap.pypa.io/get-pip.py
$ python get-pip.py
```
_If `python` command is also not found then please look for `python3` command. Otherwise install `python3`._

## License

`cyperf-agent-manager` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## CLI
This package installs a command called `cyperf-agent-manager` that is a very thin wrapper over `cyperf_agent_manager` package. This top level commands has many subcommands that can be used to execute different operations on multiple agents at simultaneously.

The command details can be found by running the script with `--help` option, as shown in the following blocks.
```
[PROMPT]:~$ cyperf-agent-manager --help
Usage: cyperf-agent-manager [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  reload
  set-controller
  set-test-interface

```
### Setting controller IP for multiple agents
```
[PROMPT]:~$ cyperf-agent-manager set-controller --help
Usage: cyperf-agent-manager set-controller [OPTIONS]

Options:
  --agent-ips     TEXT  One or more agent names (IP addresses or hostnames). Use quotation marks (`'` or `"`) for whitespace (` `) separated values. Other valid separators are `,`, `;` and `:`. [default: None] [required]
  --controller-ip TEXT  [required]
  --help                Show this message and exit.

Example:
========

[PROMPT]:~$ cyperf-agent-manager set-controller --controller-ip 10.36.75.126 --agent-ips '10.36.75.69 10.36.75.70'
>> Connectiong to agent 10.36.75.69
>> Executing command cyperfagent controller set 10.36.75.126

Controller is set successfully.

Current Configurations
  Controller:           10.36.75.126:30422
  Management Interface: ens160
  Test Interface:       ens192

Please make sure that the URL and interfaces are set correctly for the tests to run.

Portmanager service restarted.

Connecting....Connected


>> Connectiong to agent 10.36.75.70
>> Executing command cyperfagent controller set 10.36.75.126

Controller is set successfully.

Current Configurations
  Controller:           10.36.75.126:30422
  Management Interface: ens160
  Test Interface:       ens192

Please make sure that the URL and interfaces are set correctly for the tests to run.

Portmanager service restarted.

Connecting....Connected

```
### Reloading configuration for multiple agents
```
[PROMPT]:~$ cyperf-agent-manager reload --help
Usage: cyperf-agent-manager reload [OPTIONS]

Options:
  --agent-ips TEXT  One or more agent names (IP addresses or hostnames). Use quotation marks (`'` or `"`) for whitespace (` `) separated values. Other valid separators are `,`, `;` and `:`. [default: None] [required]
  --help            Show this message and exit.

Example:
========

[PROMPT]:~$ cyperf-agent-manager reload --agent-ips '10.36.75.69 10.36.75.70'
>> Connectiong to agent 10.36.75.69
>> Executing command cyperfagent configuration reload

Current Configurations
  Controller:           10.36.75.126:30422
  Management Interface: ens160
  Test Interface:       ens192

Please make sure that the URL and interfaces are set correctly for the tests to run.

Portmanager service restarted.

Connecting.....Connected


>> Connectiong to agent 10.36.75.70
>> Executing command cyperfagent configuration reload

Current Configurations
  Controller:           10.36.75.126:30422
  Management Interface: ens160
  Test Interface:       ens192

Please make sure that the URL and interfaces are set correctly for the tests to run.

Portmanager service restarted.

Connecting....Connected


```
### Setting test interface for multiple agents
```
[PROMPT]:~$ cyperf-agent-manager set-test-interface --help
Usage: cyperf-agent-manager set-test-interface [OPTIONS]

Options:
  --agent-ips      TEXT  One or more agent names (IP addresses or hostnames). Use quotation marks (`'` or `"`) for whitespace (` `) separated values. Other valid separators are `,`, `;` and `:`. [default: None] [required]
  --test-interface TEXT  [required]
  --help                 Show this message and exit.

Example:
========

[PROMPT]:~$ cyperf-agent-manager set-test-interface --agent-ips '10.36.75.69 10.36.75.70' --test-interface auto
>> Connectiong to agent 10.36.75.69
>> Executing command cyperfagent interface test set auto

Test Interface is set successfully.

Current Configurations
  Controller:           10.36.75.126:30422
  Management Interface: ens160
  Test Interface:       auto (Auto-detected interface is ens192)

Please make sure that the URL and interfaces are set correctly for the tests to run.
Use the following commands to explicitly set the Management and Test interfaces:
  cyperfagent interface management set <Management interface name>
  cyperfagent interface test set <Test interface name>

Portmanager service restarted.


>> Connectiong to agent 10.36.75.70
>> Executing command cyperfagent interface test set auto

Test Interface is set successfully.

Current Configurations
  Controller:           10.36.75.126:30422
  Management Interface: ens160
  Test Interface:       auto (Auto-detected interface is ens192)

Please make sure that the URL and interfaces are set correctly for the tests to run.
Use the following commands to explicitly set the Management and Test interfaces:
  cyperfagent interface management set <Management interface name>
  cyperfagent interface test set <Test interface name>

Portmanager service restarted.


```

## Module
The python module installed by this package in `cyperf_agent_manager`. This can be used from a custom python script. Here is a smaple code that uses the `cyperf_agent_manager` module.
```
import cyperf_agent_manager.agent_manager as caMgr

agentIPs     = [ '192.168.0.1', '192.168.0.2' ]
controllerIP = '192.168.100.1'
testIface    = 'ens192'

agentMgr     = caMgr.CyPerfAgentManager(agentIPs)

agentMgr.ControllerSet (controllerIP)
agentMgr.Reload ()
agentMgr.SetTestInterface (testIface)
```
