import json

class MessageProtocol:

    @classmethod
    def register(cls, width, height, uuid, name):
        message = { "method":"REGISTER", "width": width, "height":height, "uuid":uuid, "name":name }
        return json.dumps(message)

    @classmethod
    def keep_alive(cls, uuid):
        message = { "method":"KEEP_ALIVE", "uuid":uuid }
        return json.dumps(message)