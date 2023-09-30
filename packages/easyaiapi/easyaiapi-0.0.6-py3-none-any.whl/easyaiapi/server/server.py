from enum import Enum, auto
from typing import Annotated, Any, Callable, Optional
from fastapi import File, WebSocket, FastAPI
from easyaiapi.utils import ImageJsonForm, read_base64_image
from opencv_stream import ModelOutput, Option, Model
import uuid
import numpy as np
import uvicorn
from base64 import b64decode

class ConnectionType(Enum):
    HTTP = auto()
    WEBSOCKET = auto()
       

def handle_result(result: Option):

    if not result.is_ok():
        output = {"success": False, "message": str(result.exception)}            
    else:
        data: ModelOutput = result.unwrap()
        output = {"success": True, "data": data.to_dict()}            
                
    return output      

                            
class EasyAIServer(FastAPI):
    
    def __init__(self, **options):
        super().__init__(**options)
 
    def run(self, port:int=8080, host:str="0.0.0.0"):
        uvicorn.run(self, host=host, port=port)

    def stream(self, endpoint: str, on_received:Callable[[str], Any]=lambda x: Option(x), on_connect:Callable[[str], None]=None, on_disconnect:Callable[[str], None]=None):
        
        on_connect = on_connect if callable(on_connect) else lambda _ : None
        on_disconnect = on_disconnect if callable(on_disconnect) else lambda _ : None

        def wrapper(func:Callable[[Any, str], None]):
            
            @self.websocket(endpoint)
            async def websocket_index(websocket: WebSocket):

                client_address = websocket.client or f"id: {uuid.uuid4()}"
                print(f"{client_address} HAS ARRIVED")
                
                await websocket.accept()
                on_connect(client_address)
                exception = None
                
                try:
                    
                    while True:

                        data = await websocket.receive_text()
                        result: Option = on_received(data)
                        
                        if not result.is_ok():
                           await websocket.send_json({
                               "success": False,
                               "message": str(result.exception)
                           })
                        
                        else:    
                            await websocket.send_json(
                                func(result.unwrap(), client_address)
                            )
                
                except Exception as e:
                    exception = e
                
                await websocket.close()
                on_disconnect(client_address)

                if exception:
                    raise exception

        
        return lambda f: wrapper(f)   


    def videostream(self, endpoint: str,  on_connect:Callable[[str], None]=None, on_disconnect:Callable[[str], None]=None):

        on_received = lambda data: read_base64_image(data)
        return self.stream(endpoint, on_received, on_connect, on_disconnect) 


    def create_model_enpoint(self, endpoint: str, model: Model, connection_type: ConnectionType):
        
        def index(image: np.ndarray, client_address:str):
            return handle_result(model(image))

        if connection_type == ConnectionType.WEBSOCKET:
            self.videostream(endpoint)(index)
        
        elif connection_type == ConnectionType.HTTP:
            
            @self.post(endpoint)
            def index(file: ImageJsonForm):
                
                result: Option = file.read()
                
                if not result.is_ok():
                    return result
                
                return handle_result(model(result.unwrap()))
        
        else:
            raise Exception(f"Invalid ConnectionType: `{connection_type}`")


    def create_model_enpoint_multi_client(self, endpoint, get_model_fn: Callable[[], Model], resize_shape:Optional[tuple[int, int]]=None):
        
        models: dict[str, Model] = {}
         
        def on_connect(client_address:str):
            models[client_address] = get_model_fn()

        def on_disconnect(client_address:str):
            del models[client_address]

        self.videostream(endpoint, resize_shape, on_connect=on_connect, on_disconnect=on_disconnect)
        def index(image: np.ndarray, client_address):
            return handle_result(models[client_address].predict(image))

