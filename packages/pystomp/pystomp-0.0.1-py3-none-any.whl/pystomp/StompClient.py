import websocket
websocket._logging._logger.level = -99
import stomper
import json

class StompClient:

    def __init__(self, url, on_connect=None):
        self.subscriptions = dict()
        self.on_connect = on_connect
        self.ws = websocket.WebSocketApp(url,
                                on_open=self.__on_open,
                                on_message=self.__on_message)
        
        self.ws.run_forever(reconnect=5)
    
    def __on_open(self, ws):
        ws.send("CONNECT\naccept-version:1.0,1.1,2.0\n\n\x00\n")

    def __on_message(self, ws, message):
        frame = stomper.Frame()
        unpacked_msg = stomper.Frame.unpack(frame, message)
        #print(unpacked_msg)
        if unpacked_msg["cmd"] == "CONNECTED":
            self.on_connect(self)
        if unpacked_msg["cmd"] == "MESSAGE":
            self.subscriptions[unpacked_msg["headers"]["destination"]](json.loads(unpacked_msg["body"]))
        

    def subscribe(self, topic : str, f):
        self.ws.send(stomper.subscribe(topic, "clientuniqueId", ack="auto"))
        self.subscriptions[topic] = f
    
    def publish(self, topic, message):
        self.ws.send(stomper.send(topic,message, content_type='application/json'))






