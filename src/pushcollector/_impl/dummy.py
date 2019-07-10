class DummyCollector(object):
    # Registered as backend 'dummy', this implementation does nothing at all
    # with the passed data.
    def update_push_items(self, items):
        pass

    def attach_file(self, filename, content):
        pass

    def append_file(self, filename, content):
        pass
