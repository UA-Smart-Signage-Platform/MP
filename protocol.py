import json

class MessageProtocol:

    @classmethod
    def register(cls, width, height, uuid):
        message = { "method":"REGISTER", "width": width, "height":height, "uuid":uuid }
        return json.dumps(message)

    @classmethod
    def log(cls, logs, uuid):
        message = { "method":"LOG", "logs": logs, "uuid":uuid }
        return json.dumps(message)