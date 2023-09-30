#!/usr/bin/python

import os
import sys
import typer
import paramiko
import scp
from typing import List
from typing_extensions import Annotated
from pathlib import Path

class CyPerfAgentManager (object):
    agent_ips_help_text = 'One or more agent names (IP addresses or hostnames).'      \
                          ' Use quotation marks (`\'` or `"`) for whitespace (` `)'   \
                          ' separated values. Other valid separators are `,`, `;` and `:`.'
    @staticmethod
    def extrct_ips (ip_list: str):
        ips = []
        for ip1 in ip_list.split():
            for ip2 in ip1.split(','):
                for ip3 in ip2.split(';'):
                    for ip4 in ip3.split(':'):
                        ips.append (ip4)
        return ips

    def __init__ (self, agentIPs = []):
        self.userName = 'cyperf'
        self.password = 'cyperf'
        self.agentIPs = agentIPs
        self.client   = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __exec__(self, cmd, sudo=False):
        if sudo:
            cmd = f'sudo -S -p \'\' {cmd}' 
        for agent in self.agentIPs:
            try:
                print (f'>> Connectiong to agent {agent}')
                self.client.connect(agent, username=self.userName, password=self.password)
                channel = self.client.get_transport().open_session()
                channel.set_combine_stderr(1)
                try:
                    print (f'>> Executing command {cmd}')
                    _stdin, _stdout, _stderr = self.client.exec_command (cmd)
                    if sudo:
                        _stdin.write(self.password + "\n")
                        _stdin.flush()
                    print(_stdout.read().decode())
                except paramiko.ssh_exception.SSHException:
                    print (f'Failed to execute command {cmd}')
                self.client.close()
            except paramiko.ssh_exception.NoValidConnectionsError:
                print (f'Connection is refused by the server')
            except TimeoutError:
                print (f'Connection timed out')

    def __copy__(self, localPath, remotePath):
        for agent in self.agentIPs:
            try:
                print (f'>> Connectiong to agent {agent}')
                self.client.connect(agent, username=self.userName, password=self.password)
                try:
                    print (f'>> Tranferring file {localPath} to {remotePath}')
                    with scp.SCPClient(self.client.get_transport()) as _scp:
                        _scp.put(localPath, remotePath)
                except scp.SCPException:
                    print (f'Failed to transfer file {localPath} to {remotePath}')
                self.client.close()
            except paramiko.ssh_exception.NoValidConnectionsError:
                print (f'Connection is refused by the server')
            except TimeoutError:
                print (f'Connection timed out')

    def ControllerSet (self, controllerIP):
        cmd = f'cyperfagent controller set {controllerIP}'
        self.__exec__(cmd)

    def Reload (self):
        cmd = f'cyperfagent configuration reload'
        self.__exec__(cmd)

    def SetTestInterface (self, iface):
        cmd = f'cyperfagent interface test set {iface}'
        self.__exec__(cmd)

    def InstallBuild (self, debFile):
        remotePath = f'~/{os.path.basename(debFile)}'
        cmd        = f'apt install -y {remotePath}'
        self.__copy__ (debFile, remotePath)
        self.__exec__ (cmd, sudo=True)

agentContoller = typer.Typer()

@agentContoller.command()
def set_controller(agent_ips: Annotated[str, typer.Option(help = CyPerfAgentManager.agent_ips_help_text)],
                   controller_ip: Annotated[str, typer.Option()]):
    agents   = CyPerfAgentManager.extrct_ips (agent_ips)
    agentMgr = CyPerfAgentManager (agents)
    agentMgr.ControllerSet (controller_ip)

@agentContoller.command()
def reload(agent_ips: Annotated[str, typer.Option(help = CyPerfAgentManager.agent_ips_help_text)]):
    agents   = CyPerfAgentManager.extrct_ips (agent_ips)
    agentMgr = CyPerfAgentManager (agents)
    agentMgr.Reload ()

@agentContoller.command()
def set_test_interface(agent_ips: Annotated[str, typer.Option(help = CyPerfAgentManager.agent_ips_help_text)],
                       test_interface: Annotated[str, typer.Option()]):
    agents   = CyPerfAgentManager.extrct_ips (agent_ips)
    agentMgr = CyPerfAgentManager (agents)
    agentMgr.SetTestInterface (test_interface)

@agentContoller.command()
def install_build(agent_ips: Annotated[str, typer.Option(help = CyPerfAgentManager.agent_ips_help_text)],
                  debian_file_path: Annotated[Path, typer.Option(exists=True, dir_okay=False)]):
    agents   = CyPerfAgentManager.extrct_ips (agent_ips)
    agentMgr = CyPerfAgentManager (agents)
    agentMgr.InstallBuild (debian_file_path)

def main():
    progName = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    typer.main.get_command(agentContoller)(prog_name=progName)

if __name__ == "__main__":
    main()
