from multiprocessing import Process
from dataclasses import dataclass
import uuid
import typing
import logging
import asyncio
import time

__all__ = ['ProcessWatcher', 'ProcessData']

logger = logging.getLogger(__name__)

@dataclass
class ProcessData():
    """Data struct to hold process information"""
    id: uuid.UUID
    start_function : typing.Callable
    args : typing.Iterable
    process: Process

class ProcessWatcher():
    """A monitoring class that starts and monitors state of launched multiprocessing processes.
    Run processes with add_process() and then run monitor() to start monitoring all added processes.
    """
    def __init__(self) -> None:
        self._processes : typing.Dict[uuid.UUID, ProcessData] = {}

    def add_process(self, func: typing.Callable, args: typing.Iterable = []) -> uuid.UUID:
        """Runs 'func' callable with 'args' in another process and adds it appends it to monitoring list.

        Args:
            func (typing.Callable): A callable to start as process
            args (typing.Iterable, optional): Args to callable. Defaults to [].

        Returns:
            uuid.UUID: uuid of added process
        """
        id = uuid.uuid4()
        process = Process(target=func, args=args)
        self._processes[id] = ProcessData(id, func, args, process)
        process.start()
        return id

    async def terminate_process(self, id: uuid.UUID, timeout: float = 10):
        """Terminates process

        Args:
            id (uuid.UUID): uuid of the process, acquired by add_process()
            timeout (float, optional): timeout, if exceeded segkills process. Defaults to 10.
        """
        p_data = self._processes[id]
        process = p_data.process
        process.terminate()
        epoch_start = time.time()
        while time.time() - epoch_start < timeout:
            if not process.is_alive():
                break
            await asyncio.sleep(5)
        if process.is_alive():
            logger.warning(f"Process with uuid [{id}] was not terminated before timeout, SEGKILL'ing it...")
            process.kill()
        self._processes.pop(id)
    
    async def terminate_processes(self, ids: typing.List[uuid.UUID], timeout: float = 10):
        """Terminates multiple processes

        Args:
            ids (typing.List[uuid.UUID]): list of uuid
            timeout (float, optional): timeout for segkill. Defaults to 10.
        """
        terminations = []
        for id in ids:
            terminations.append(asyncio.create_task(self.terminate_process(id, timeout)))
        await asyncio.gather(*terminations)
        
    async def terminate_all_processes(self, timeout: float = 10):
        """Terminate all processes

        Args:
            timeout (float, optional): timeout for segkill. Defaults to 10.
        """
        await self.terminate_processes(list(self._processes.keys()), timeout)
    
    async def monitor(self):
        """Main loop in which monitoring occures
        """
        # while not self._force_stop_flag and len(self._processes) > 0:
        while len(self._processes) > 0:
            for id in list(self._processes.keys()):
                p_data = self._processes[id]
                process = p_data.process
                if process.exitcode is None and not process.is_alive(): # Not finished and not running
                    # Do your error handling and restarting here assigning the new process to processes[n]
                    logger.error(f"Process with starting function '{p_data.start_function}' is dead, restarting...")
                    process = Process(target=p_data.start_function, args=p_data.args)
                    process.start()
                    p_data.process = process
                elif process.exitcode is not None and process.exitcode != 0:
                    logger.error(f"Process with starting function '{p_data.start_function}' exited with code {process.exitcode}, restarting...")
                    process = Process(target=p_data.start_function, args=p_data.args)
                    process.start()
                    p_data.process = process
                elif process.exitcode == 0:
                    logger.info(f"Process with starting function '{p_data.start_function}' finished successfully")
                    process.join() # Allow tidyup
                    del self._processes[id] # Removed finished items from the dictionary 
                    # When none are left then loop will end
                await asyncio.sleep(2)