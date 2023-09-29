from datetime import datetime
from pycurl import Curl
from .errors import *
from .utils import *

import asyncio
import signal
import pycurl
import os

class Funload:

    def __init__(
        self,
        url: str,
        destination: str="./",
        progress_bar: bool = False,
        block: bool = False,
    ) -> None:
        
        self.__session: Curl = Curl()
        self.__task: asyncio.Task = None
        self.__url: str = url
        self.__destination: str = destination
        self.__status: str = ""
        self.__downloaded: int = 0
        self.__speed: int = 0
        self.__file_size: float = 0.00
        self.__percentage: float = 0.00
        self.__is_progress_bar: bool = progress_bar
        self.__is_blocking: bool = block
        self.__is_finished: bool = True
        self.__is_paused: bool = False
        self.__estimate: datetime = 0
        self.__elapsed_time: datetime = 0
        
        self.set_curl_opts()
        
        signal.signal(signal.SIGINT, self.stop)

    def set_curl_opts(self):
        self.__session.setopt(self.__session.URL, self.__url)
        self.__session.setopt(self.__session.FOLLOWLOCATION, True)
        self.__session.setopt(self.__session.MAXREDIRS, 10)

        
        if self.__destination.endswith("/") or os.path.isdir(self.__destination):
            file_name = parse_file_name(
                self.__session.getinfo(self.__session.EFFECTIVE_URL)
            )
            
            self.__destination = self.__destination.rstrip("/") + "/" 
            self.__destination += file_name

    async def start(self):

        if not self.is_finished:
            return

        self.__is_finished = False

        file_descriptor = open(self.__destination, "wb+")
        self.__session.setopt(self.__session.WRITEDATA, file_descriptor)

        thread = asyncio.to_thread(self.__session.perform)

        start_time = datetime.now()

        if self.__is_blocking:
            await thread
        else:
            if self.__is_progress_bar:
                self.__session.setopt(self.__session.NOPROGRESS, False)
                self.__session.setopt(
                    self.__session.XFERINFOFUNCTION, 
                    lambda total_data, received_data, _, __: asyncio.run(
                        self.__download_file(
                            received_data=received_data,
                            total_data=total_data,
                            start_time=start_time
                        )
                    )
                )

            self.__task = asyncio.create_task(thread)
            
            while not self.__downloaded:
                await asyncio.sleep(0)
            
            asyncio.create_task(self.__watch_download_action())

    async def __download_file(self, total_data, received_data, start_time: datetime):
        while self.__is_paused:
            self.__status = "Paused"
            await asyncio.sleep(0)

        if not self.__status == "Stopped":
            self.__status = "Downloading"
        else:
            return pycurl.E_ABORTED_BY_CALLBACK
        
        self.__file_size = total_data
        self.__downloaded = received_data

        await asyncio.sleep(0)

        try:
            self.__estimate, self.__elapsed_time, self.__speed, self.__percentage = parse_progress_details(
                received_data=received_data,
                total_data=total_data,
                start_time=start_time
            )
        except ZeroDivisionError:
            pass

    async def __watch_download_action(self):
        try:
            await self.__task
            self.__status = "Downloaded"
        except pycurl.error as e:
            self.__is_finished = True
            err_code, message = e.args
            if err_code == pycurl.E_GOT_NOTHING:
                raise EmptyResponse(message)
            else:
                raise GenericError(f"{e}: {message}")

        self.__is_finished = True

    async def wait(self):
        return await self.__task if not self.__task.done() else False

    def stop(self, *args):
        if self.__is_blocking:
            return False

        self.__status = "Stopped"
        self.__task.cancel()
        
        if args:
            import os
            os._exit(signal.SIGINT)

        return True
    
    async def retry(self):
        if self.__status != "Stopped":
            self.stop()
        
        await asyncio.sleep(1)

        self.__status = ""
        self.__is_finished = True

        self.__session = Curl()
        self.set_curl_opts()

        await self.start()

    @property
    def is_finished(self):
        return self.__is_finished
    
    def pause(self):
        if self.__is_finished:
            return False

        self.__is_paused = True
        return True

    def resume(self):
        if self.__is_blocking:
            return False

        self.__is_paused = False
        return True

    @property
    def file_name(self):
        return self.__destination

    @property
    def file_size(self):
        return self.__file_size

    @property
    def downloaded(self):
        return self.__downloaded

    @property
    def estimate(self):
        return self.__estimate

    @property
    def percentage(self):
        return self.__percentage

    @property
    def speed(self):
        return self.__speed

    @property
    def status(self):
        return self.__status

    @property
    def elapsed_time(self):
        return self.__elapsed_time