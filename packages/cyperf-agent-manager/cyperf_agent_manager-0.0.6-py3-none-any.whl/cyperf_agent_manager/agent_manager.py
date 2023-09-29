#!/usr/bin/python

import os
import sys
import typer
import paramiko
from typing import List
from typing_extensions import Annotated

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

    def __exec__(self, cmd):
        for agent in self.agentIPs:
            try:
                print (f'>> Connectiong to agent {agent}')
                self.client.connect(agent, username=self.userName, password=self.password)
                channel = self.client.get_transport().open_session()
                channel.set_combine_stderr(1)
                try:
                    print (f'>> Executing command {cmd}')
                    _stdin, _stdout, _stderr = self.client.exec_command (cmd)
                    print(_stdout.read().decode())
                except paramiko.ssh_exception.SSHException:
                    print (f'Failed to execuye command {cmd}')
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

def main():
    progName = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    typer.main.get_command(agentContoller)(prog_name=progName)

if __name__ == "__main__":
    main()
