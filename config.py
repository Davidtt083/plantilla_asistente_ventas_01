import os

class Config:
    SECRET_KEY = 'tu_clave_secreta_aqui'
    MONGO_URI = "mongodb+srv://davidtt083:12345qwerty@chatbot01.k9en0.mongodb.net/usuarios?retryWrites=true&w=majority&appName=chatbot01"
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")