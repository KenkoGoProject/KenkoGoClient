import json

from no_use.server_status import ServerStatus


class JsonEncoderEx(json.JSONEncoder):
    def default(self, _object):
        if isinstance(_object, ServerStatus):
            return {
                'code': _object.value,
                'name': _object.name
            }
        return json.JSONEncoder.default(self, _object)
