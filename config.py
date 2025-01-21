from dotenv import load_dotenv
import os

mode = os.getenv('env', 'dev')
load_dotenv(mode + '.env')

NEO4J_URI = os.getenv('NEO4J_URI', "http://localhost:7474")
NEO4J_USER = os.getenv('NEO4J_USER', "neo4j")
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', "neo4j")

SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
SERVER_HOST = os.getenv('SERVER_HOST', "127.0.0.1")

TTS_DEFAULT_PARMS = {"VOICE" : "en-US-SteffanNeural", "RATE": -30, "VOLUME": 50, "PITCH": 0}