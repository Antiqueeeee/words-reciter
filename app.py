from fastapi import FastAPI
from Basements.InterfaceParams import *
from Basements.dataEngine import DataManager
import uvicorn
from config import *
import json
app = FastAPI()


class Server(FastAPI):
    def __init__(self):
        super().__init__()
        self.manager_data = DataManager()
        self.post("/publisher_select_word")(self.publisher_select_word)

    def publisher_select_word(self, params:params_publisher_select_word):
        publisher, grade, edition, volume, unit = params.publisher, params.grade, params.edition, params.volume, params.unit
        results = self.manager_data.publisher_select_word(
            publisher = publisher, grade = grade,
            edition = edition, volume = volume,
            unit = unit
        )
        return json.dumps(results, ensure_ascii=False)

    def run(self, host, port):
        uvicorn.run(self, host=host, port=port)

if __name__ == "__main__":
    server = Server()
    server.run(SERVER_HOST, SERVER_PORT)
