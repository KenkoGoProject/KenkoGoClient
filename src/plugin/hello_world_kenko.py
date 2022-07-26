from assets.cq_code import CqCode
from module.gocq_api import GocqApi


class HelloWorld:
    def __init__(self, api: GocqApi):
        print('Initializing HelloWorld...')
        self.api = api

    def on_message(self, message):
        if message['post_type'] == 'message':
            msg: str = message['raw_message']
            if CqCode.at(message['self_id']) in msg:
                print('有人叫我')
                message['message'] = '你干嘛~~~'
                self.api.send_msg(message)
