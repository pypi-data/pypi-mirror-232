import asyncio
from typing import Callable, Optional, Union
import websockets
from .source import Video

class NoDataException(Exception):
    pass

class WssClient:

    def get_data(self):
        raise NotImplementedError("Must implement 'get_data'") 


    def on_data_received(self, data: str):
        raise NotImplementedError("Must implement 'on_data_received'")     


    def start(self, uri:str):

        async def wrapper():

            async with websockets.connect(uri) as websocket:

                while True:  

                    try:
                        data = self.get_data()

                        if not data:
                            break

                        await websocket.send(data)
                        message = await websocket.recv()

                        self.on_data_received(message)

                    except NoDataException:
                        break    

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(wrapper())


    def from_source(get_data: Callable, on_data_received: Callable)->"WssClient":

        ws = WssClient()
        ws.get_data = get_data
        ws.on_data_received = on_data_received

        return ws    


    @classmethod
    def from_video_source(cls, path_or_camera_index:Union[str, int], on_data_received: Callable, shape:Optional[tuple[int, int]]=None, show_video=True)->"WssClient":
        video = Video(path_or_camera_index, shape, show_video)
        return cls.from_source(video.read, on_data_received)



