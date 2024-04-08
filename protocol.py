import json

class MessageProtocol:

    @classmethod
    def register(cls, width, height, uuid, name):
        message = { "method":"REGISTER", "width": width, "height":height, "uuid":uuid, "name":name }
        return json.dumps(message)

    @classmethod
    def log(cls, logs, uuid):
        message = { "method":"LOG", "logs": logs, "uuid":uuid }
        return json.dumps(message)