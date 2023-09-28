#!/usr/bin/python

import os
import sys
import typer
import subprocess
from typing import List
from typing_extensions import Annotated

class CyPerfAgentManager (object):
    def __init__ (self, agentIPs = []):
        self.userName = 'cyperf'
        self.password = 'cyperf'
        self.agentIPs = agentIPs

    def __exec__(self, cmd):
        for agent in self.agentIPs:
            print (f'Configuring agent {agent}')
            sshcmd = f'sshpass -p {self.password} ssh -o StrictHostKeyChecking=accept-new {self.userName}@{agent} {cmd}'
            pipe = subprocess.Popen(sshcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = pipe.communicate()
            if pipe.returncode:
                print(f'[stderr] {result[1].decode(encoding="utf-8")}')
            for line in result[0].decode(encoding='utf-8').split('\n'):
                print(line)

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
def set_controller(agent_ips: Annotated[List[str], typer.Argument()],
                   controller_ip: Annotated[str, typer.Option()]):
    agentMgr = CyPerfAgentManager (agent_ips)
    agentMgr.ControllerSet (controller_ip)

@agentContoller.command()
def reload(agent_ips: Annotated[List[str], typer.Argument()]):
    agentMgr = CyPerfAgentManager (agent_ips)
    agentMgr.Reload ()

@agentContoller.command()
def set_test_interface(agent_ips: Annotated[List[str], typer.Argument()],
                   test_interface: Annotated[str, typer.Option()]):
    agentMgr = CyPerfAgentManager (agent_ips)
    agentMgr.SetTestInterface (test_interface)

def main():
    progName = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    typer.main.get_command(agentContoller)(prog_name=progName)
