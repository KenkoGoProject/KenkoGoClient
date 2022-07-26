import time


class GocqEvent:
    @staticmethod
    def server_event(event_type: str, event_data=None):
        return {
            'time': int(time.time()),
            'post_type': 'server_event',
            'server_event_type': event_type,
            'data': event_data
        }
