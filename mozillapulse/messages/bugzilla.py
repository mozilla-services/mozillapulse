from base import *

# ------------------------------------------------------------------------------
# Generic base class for messages that have to do with bugs
# ------------------------------------------------------------------------------

class GenericBugMessage(GenericMessage):

    def __init__(self):
        super(GenericBugMessage, self).__init__()
        self.routing_parts.append('bug')

    def _required_data_fields(self):
        tmp = super(GenericBugMessage, self)._required_data_fields()
        tmp.append('who')
        tmp.append('when')
        return tmp

    def set_bugdata(self, bugdata):
        self.set_data('bug', bugdata)

# ------------------------------------------------------------------------------
# High-level bug state messages (for end-user convenience)
# ------------------------------------------------------------------------------

class BugStateMessage(GenericBugMessage):

    def __init__(self, what):
        super(BugStateMessage, self).__init__()
        self.routing_parts.append(what)

class BugCreatedMessage(BugStateMessage):

    def __init__(self):
        super(BugCreatedMessage, self).__init__('new')

class BugClosedMessage(BugStateMessage):

    def __init__(self):
        super(BugClosedMessage, self).__init__('closed')

class BugReopenedMessage(BugStateMessage):

    def __init__(self):
        super(BugReopenedMessage, self).__init__('reopened')


# TODO: Should this have top-level fields?
class BugUndupedMessage(BugStateMessage):

    def __init__(self):
        super(BugUndupedMessage, self).__init__('unduped')

class BugDupedMessage(BugStateMessage):

    def __init__(self):
        super(BugDupedMessage, self).__init__('duped')

    def _required_data_fields(self):
        tmp = super(BugDupedMessage, self)._required_data_fields()
        tmp.append('dupe')
        tmp.append('original')
        return tmp

# ------------------------------------------------------------------------------
# Messages about changing bug values
# ------------------------------------------------------------------------------

class BugAddedMessage(GenericBugMessage):

    def __init__(self, what):
        super(BugAddedMessage, self).__init__()
        self.routing_parts.append('added')
        self.routing_parts.append(what)

    def _required_data_fields(self):
        tmp = super(BugAddedMessage, self)._required_data_fields()
        tmp.append('bug')
        tmp.append('value')
        return tmp

class BugRemovedMessage(GenericBugMessage):

    def __init__(self, what):
        super(BugRemovedMessage, self).__init__()
        self.routing_parts.append('removed')
        self.routing_parts.append(what)

    def _required_data_fields(self):
        tmp = super(BugRemovedMessage, self)._required_data_fields()
        tmp.append('bug')
        tmp.append('value')
        return tmp

class BugChangedMessage(GenericBugMessage):
    
    def __init__(self, what):
        super(BugChangedMessage, self).__init__()
        self.routing_parts.append('changed')
        self.routing_parts.append(what)

    def _required_data_fields(self):
        tmp = super(BugChangedMessage, self)._required_data_fields()
        tmp.append('bug')
        return tmp

    def _validate(self):
        super(BugChangedMessage, self)._validate()
        if 'before' not in self.data and 'after' not in self.data:
            raise MalformedMessage('require either "before" or "after" field')

        if not self.data['before'] and not self.data['after']:
            raise MalformedMessage('before and after fields cannot both be blank')

        if self.data['before'] == self.data['after']:
            raise MalformedMessage('before and after fields cannot be the same')
