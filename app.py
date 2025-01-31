from fastapi import FastAPI
from fastapi import Response
from fastapi.responses import FileResponse
from Basements.InterfaceParams import *
from Basements.dataEngine import DataManager
from Basements.ServiceEngine import ServiceEngine
import uvicorn
from config import *
import json
app = FastAPI()


class Server(FastAPI):
    def __init__(self):
        super().__init__()
        self.manager_data = DataManager()
        self.service_engine = ServiceEngine()
        self.post("/publisher_select_word")(self.publisher_select_word)
        self.post("/get_publisher")(self.get_publisher)
        self.post("/get_grades")(self.get_grades)
        self.post("/get_volumes")(self.get_volumes)
        self.post("/get_editions")(self.get_editions)
        self.post("/get_units")(self.get_units)
        self.post("/get_word_audio")(self.get_word_audio)
        self.post("/created_word_related_graph")(self.created_word_related_graph)

    def publisher_select_word(self, params:params_publisher_select_word):
        publisher, grade, edition, volume, unit = params.publisher, params.grade, params.edition, params.volume, params.unit
        results = self.service_engine.publisher_select_word(
            publisher = publisher, grade = grade,
            edition = edition, volume = volume,
            unit = unit
        )
        return json.dumps(results, ensure_ascii=False)

    def run(self, host, port):
        uvicorn.run(self, host=host, port=port)

    def get_publisher(self):
        return self.service_engine.get_publisher()

    def get_grades(self, params:params_get_grades):
        publisher = params.publisher
        return self.service_engine.get_grade(publisher)

    def get_volumes(self, params:params_get_volumes):
        publisher, grade = params.publisher, params.grade
        return self.service_engine.get_volume(publisher, grade)

    def get_editions(self, params:params_get_editions):
        publisher, grade, volume = params.publisher, params.grade, params.volume
        return self.service_engine.get_edition(publisher, grade, volume)

    def get_units(self, params:params_get_units):
        publisher, grade, volume, edition = params.publisher, params.grade, params.volume, params.edition
        return self.service_engine.get_unit(publisher, grade, volume, edition)

    def get_word_audio(self, params:params_get_word_audio):
        filename = params.filename
        if os.path.exists(filename):
            return FileResponse(filename, media_type="audio/wav")
        return Response(status_code=404, content="File not found.")

    def created_word_related_graph(self, params:params_obtain_word_related):
        word = params.word
        nodes, links = self.service_engine.word_related_graph(word)
        return {"nodes": nodes, "links": links}

if __name__ == "__main__":
    server = Server()
    server.run(SERVER_HOST, SERVER_PORT)
