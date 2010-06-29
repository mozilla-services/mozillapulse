from base import *
from mozillapulse.utils import extract_bug_ids, repo_parts

# ------------------------------------------------------------------------------
# Generic base class for messages that have to do with HG
# ------------------------------------------------------------------------------
class GenericHgMessage(GenericMessage):

    def __init__(self):
        super(GenericHgMessage, self).__init__()
        self.routing_parts.append('hg')

# ------------------------------------------------------------------------------
# Messages that have to do with HG's open and close status
# ------------------------------------------------------------------------------
class HgRepoStatusMessage(GenericHgMessage):

    def __init__(self, repo):
        super(HgRepoStatusMessage, self).__init__()
        self.routing_parts.append('repo')

# FIXME: This doesn't really follow general -> specific pattern
class HgRepoClosedMessage(HgRepoStatusMessage):

    def __init__(self, repo):
        super(HgRepoClosedMessage, self).__init__()
        self.routing_parts.append('closed')
        self.routing_parts.append(repo)

# FIXME: This doesn't really follow general -> specific pattern
class HgRepoOpenedMessage(HgRepoStatusMessage):

    def __init__(self, repo):
        super(HgRepoOpenedMessage, self).__init__()
        self.routing_parts.append('opened')
        self.routing_parts.append(repo)

# ------------------------------------------------------------------------------
# Messages that have to do with commits
# ------------------------------------------------------------------------------
class GenericCommitMessage(GenericHgMessage):

    def __init__(self):
        super(GenericCommitMessage, self).__init__()
        self.routing_parts.append('commit')

    def _required_data_fields(self):
        tmp = super(GenericCommitMessage, self)._required_data_fields()
        tmp.append('when')
        tmp.append('changeset')
        tmp.append('who')
        tmp.append('message')
        tmp.append('link')
        return tmp

    def _prepare(self):
        super(GenericCommitMessage, self)._prepare()

        # Parse the message for bug ids
        bugs = extract_bug_ids(self.data['message'])
        if bugs:
            self.set_data('bug_ids', bugs)

# FIXME: This doesn't really follow general -> specific pattern
class HgCommitMessage(GenericCommitMessage):

    def __init__(self, repo):
        super(HgCommitMessage, self).__init__()
        self.set_data('repository', repo)

    def _required_data_fields(self):
        tmp = super(HgCommitMessage, self)._required_data_fields()
        tmp.append('repository')
        return tmp

    # Gnerate part of the routing key from the repository
    def _prepare_routing_key(self):
        # Parse the repo to make our routing key more specific
        parts = repo_parts(self.data['repository'])
        for part in parts:
            self.routing_parts.append(part)

        # Do the standard stuff
        super(HgCommitMessage, self)._prepare_routing_key()
