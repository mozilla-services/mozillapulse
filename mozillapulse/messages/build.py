from base import *

# ------------------------------------------------------------------------------
# Generic base class for messages that have to do with builds
# ------------------------------------------------------------------------------

class BuildMessage(GenericMessage):
    def __init__(self, event):
        super(BuildMessage, self).__init__()
        self.routing_parts.append(event['event'])
        self.metadata['master_name'] = event['master_name']
        self.metadata['message_id'] = event['id']

        for key, value in event['payload'].items():
            self.set_data(key, value)
