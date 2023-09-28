# cyperf-agent-manager
A simple python script that can ssh into multiple cyperf agents and run some pre-defined commands

[![PyPI - Version](https://img.shields.io/pypi/v/cyperf-agent-manager.svg)](https://pypi.org/project/cyperf-agent-manager)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cyperf-agent-manager.svg)](https://pypi.org/project/cyper-fagent-manager)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install cyperf-agent-manager
```

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
  test-interface

```
## Setting controller IP for multiple agents
```
[PROMPT]:~$ cyperf-agent-manager set-controller --help
Usage: cyperf-agent-manager set-controller [OPTIONS] AGENT_IPS...

Arguments:
  AGENT_IPS...  [required]

Options:
  --controller-ip TEXT  [required]
  --help                Show this message and exit.

Example:
========

[PROMPT]:~$ cyperf-agent-manager set-controller --controller-ip 10.36.75.126 10.36.75.69 10.36.75.70
Configuring agent 10.36.75.69

Controller is set successfully.

Current Configurations
  Controller:           10.36.75.126:30422
  Management Interface: ens160
  Test Interface:       ens192

Please make sure that the URL and interfaces are set correctly for the tests to run.

Portmanager service restarted.

Connecting....Connected


Configuring agent 10.36.75.70

Controller is set successfully.

Current Configurations
  Controller:           10.36.75.126:30422
  Management Interface: ens160
  Test Interface:       ens192

Please make sure that the URL and interfaces are set correctly for the tests to run.

Portmanager service restarted.

Connecting....Connected

```
## Reloading configuration for multiple agents
```
[PROMPT]:~$ cyperf-agent-manager reload --help
Usage: cyperf-agent-manager reload [OPTIONS] AGENT_IPS...

Arguments:
  AGENT_IPS...  [required]

Options:
  --help  Show this message and exit.

Example:
========

[PROMPT]:~$ cyperf-agent-manager reload 10.36.75.69 10.36.75.70
Configuring agent 10.36.75.69

Current Configurations
  Controller:           10.36.75.126:30422
  Management Interface: ens160
  Test Interface:       ens192

Please make sure that the URL and interfaces are set correctly for the tests to run.

Portmanager service restarted.

Connecting.....Connected


Configuring agent 10.36.75.70

Current Configurations
  Controller:           10.36.75.126:30422
  Management Interface: ens160
  Test Interface:       ens192

Please make sure that the URL and interfaces are set correctly for the tests to run.

Portmanager service restarted.

Connecting....Connected


```
## Setting test interface for multiple agents
```
[PROMPT]:~$ cyperf-agent-manager test-interface --help
Usage: cyperf-agent-manager test-interface [OPTIONS] AGENT_IPS...

Arguments:
  AGENT_IPS...  [required]

Options:
  --test-interface TEXT  [required]
  --help                 Show this message and exit.

Example:
========

[PROMPT]:~$ cyperf-agent-manager test-interface --test-interface auto 10.36.75.69 10.36.75.70
Configuring agent 10.36.75.69

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


Configuring agent 10.36.75.70

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
import cyperf_agent_manager as caMgr

agentIPs     = [ '192.168.0.1', '192.168.0.2' ]
controllerIP = '192.168.100.1'
testIface    = 'ens192'

agents       = caMgr.CyPerfAgent(agentIPs)

agents.ControllerSet (controllerIP)
agents.Reload ()
agents.SetTestInterface (testIface)
```
