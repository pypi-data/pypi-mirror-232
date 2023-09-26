import re
import subprocess as sp
from signal import SIGINT
from threading import Thread
from glob import glob

from .common import cyan_print
from typing import Union
import socket
from termcolor import colored

from .common import get_path_delimiter

pdel = get_path_delimiter()


class Factory:
    """This class encapsulates a process that manages the python provider factory dotnet application

    """

    def __init__(
            self,
            host: str,
            port: int,
            user: Union[str, None],
            domain: Union[str, None],
            whitelist_me: bool,
            _fbn_run: bool,
    ):
        """Constructor of the Factory class

        Args:
            host (str): the host that the target api server is running at
            port (int): the port that the target api server is exposed at
            user (str): the user to route with. Can be a user ID, global or None. In the none case a browser window will
             be opened for you to log in with.
            domain (str): which finbourne domain to run in such as fbn-ci (internal), fbn-qa (internal) or fbn-prd.
            _fbn_run (bool): finbourne-internal option for an alternative rabbitMQ authentication when running in K8s.

        """

        if re.match('^[\w._-]+$', host) is None:
            raise ValueError(f"Invalid value for host: {host}")

        if not isinstance(port, int):
            raise ValueError(f"Port number must be an integer. Was {type(port).__name__} ({port})")

        path_parts = __file__.split(pdel)[:-1] + ['bin', 'tools', 'net6.0', 'any', 'Finbourne.Honeycomb.Host.dll']
        self.dll_path = pdel.join(path_parts)

        self.cmd = f'dotnet {self.dll_path} --quiet '

        if domain is not None:
            self.cmd += f'--authClientDomain={domain} '

        if user is not None and user != 'global':
            self.cmd += f'--localRoutingUserId "{user}" '

        elif user is not None and user == 'global':
            self.cmd += f'--routeAs:Global '

        self.cmd += f'--config "PythonProvider:BaseUrl=>http://{host}:{port}/api/v1/" '

        if whitelist_me and user == 'global':
            my_machine_name = socket.gethostname().split('.')[0]
            print(colored(f'🚨Warning: machine name "{my_machine_name}" has been whitelisted and providers are runnning globally🚨', 'red'))
            self.cmd += f'"DataProvider:RoutingTypeGlobalMachineWhitelist=>{my_machine_name}" '

        if _fbn_run:
            self.cmd += '"Metrics:Enabled=>true" '
            self.cmd += '"NameServiceClient:RabbitConfigFile=>honeycomb-rabbit-config-plain.json" '
            self.cmd += '"NameServiceClient:RabbitUserPassword->/usr/app/secrets/service-main" '

        self.starting = True
        self.process = None
        self.print_thread = Thread(target=self.__print_process_output)
        self.errored = False

    def start(self):
        """Start the factory process. This will block the program while the setup is running.

        """

        if len(glob(self.dll_path)) != 1:
            cmd = 'python -m lumipy.setup --secrets=<your secrets file>'
            raise ValueError(f'Provider factory dll is missing. Have you run the provider setup?\n  Try:\n    {cmd}')

        if len(glob(self.dll_path.split('Finbourne')[0] + '*.pem')) != 2:
            cmd = 'python -m lumipy.setup --secrets=<your secrets file>'
            raise ValueError(f'Certificate pem files are missing. Have you run the provider setup?\n  Try:\n    {cmd}')

        cyan_print('Starting python provider factory')
        print(self.cmd, end='\n\n')

        self.process = sp.Popen(self.cmd.split(), shell=False, stdout=sp.PIPE, stderr=sp.PIPE)

        self.print_thread.start()

        while self.starting:
            pass

        self.errored = self.process.poll() is not None

        if self.errored:
            self.print_thread.join()

    def stop(self):
        """Stop the factory process and shut down the providers. This will block the program while the termination is
        completing.

        """
        if self.process.poll() is not None:
            # no-op
            return

        cyan_print('\nStopping python provider factory')

        self.process.send_signal(SIGINT)

        while self.process.poll() is None:
            pass

        self.print_thread.join()

    def __print_process_output(self):

        # Set a loop running in another thread that periodically polls the process
        # When there's a new line of output print it
        # If the process is in exit state, set block=False so the stop method stops blocking

        bad_lines = 0
        while self.process.poll() is None:

            output = self.process.stdout.readline().decode('utf-8').rstrip()

            if output:
                print(output)

            if 'RemoteCancellation: ResubscribeAsync failed with' in output:
                bad_lines += 1
            else:
                # reset count in case it's a blip
                bad_lines = 0

            if bad_lines > 50:
                self.errored = True
                break

            if 'Running! Hit Ctrl+C to shut down services' in output:
                self.starting = False
