from .local import LocalCollector
from .dummy import DummyCollector
from .proxy import CollectorProxy


class Collector(object):
    """A collector for log files and push item data.

    This class defines the interface for all pushcollector backends.
    Instances of this class shouldn't be constructed directly; rather,
    the :meth:`~pushcollector.Collector.get` method should be used to
    obtain a collector of the desired backend.
    """

    _BACKENDS = {}
    _INITIAL_BACKEND = "local"
    _DEFAULT_BACKEND = _INITIAL_BACKEND

    def update_push_items(self, items):
        """Record a state change on one or more push items.

        Arguments:
            items (List[dict])
                    A list of push item dicts.

                    Each dict must have, at minimum, "filename" and "state"
                    keys. For complete information on the format of push item
                    dicts, see the :ref:`schema` documentation.

                    An exception will be raised if any push item does not match
                    the documented schema.

        Returns:
            :class:`~concurrent.futures.Future`
                A Future resolved with None when the push item update succeeds,
                or resolved with an error if the update failed.
        """
        raise NotImplementedError()

    def attach_file(self, filename, content):
        """Collect some content into a file of the specified name.

        Parameters:
            filename (str)
                The name of a file to be created (or overwritten).

            content (bytes, str)
                Content to be written into the file.

                Both binary and text files are supported.

                If a ``str`` is provided, it will always be encoded
                as UTF-8.

        Returns:
            :class:`~concurrent.futures.Future`
                A Future resolved with None when the file has been written,
                or resolved with an error if the operation failed.
        """
        raise NotImplementedError()

    def append_file(self, filename, content):
        """Like :meth:`attach_file`, except that if the named file already
        exists, content is appended to it rather than overwriting the file.
        """
        raise NotImplementedError()

    @classmethod
    def get(cls, backend=None):
        """Obtain a collector using the specified backend.

        Parameters:
            backend (str)
                If provided, must be the name of an existing pushcollector backend.
                An instance of this backend will be used.

                If omitted/None, the library's default backend will be used.
                The default backend is initially set to "local".

        Returns:
            :class:`~pushcollector.Collector`
                An object implementing the ``Collector`` interface, which
                may be used to record log files and push item data.

        Raises:
            ValueError
                If the requested backend is not valid.
        """
        backend = backend or cls._DEFAULT_BACKEND

        cls._require_backend(backend)

        factory = cls._BACKENDS[backend]
        instance = factory()
        return CollectorProxy(instance)

    @classmethod
    def register_backend(cls, name, factory):
        """Register a new pushcollector backend, or update/remove an existing
        backend.

        Parameters:
            name (str)
                The name of a backend. This should be a brief unique identifying
                string for programmatic use.

            factory (callable)
                A callable used to create new instances of the backend.
                When invoked, this callable must return an object which implements
                the :class:`~pushcollector.Collector` interface.

                Alternatively, if ``None`` is provided, the backend of the given
                ``name`` is unregistered and may no longer be used.

        Raises:
            TypeError
                If ``factory`` is not callable and not ``None``.
        """
        if factory is not None and not callable(factory):
            raise TypeError("expected None or callable, got: %s" % repr(factory))

        if factory is None:
            if cls._DEFAULT_BACKEND == name:
                # Unregistered backend cannot remain the default.
                cls.set_default_backend(None)
            cls._BACKENDS.pop(name, None)
        else:
            cls._BACKENDS[name] = factory

    @classmethod
    def set_default_backend(cls, name):
        """Set the default pushcollector backend.

        Parameters:
            name (str)
                The name of a backend registered with the library,
                or ``None`` to reset the default backend to the library's
                initial default.

        Raises:
            ValueError
                If there is no registered backend of the requested name.
        """
        name = name or cls._INITIAL_BACKEND
        cls._require_backend(name)
        cls._DEFAULT_BACKEND = name

    @classmethod
    def _require_backend(cls, name):
        if name not in cls._BACKENDS:
            raise ValueError("No registered pushcollector backend: '%s'" % name)


Collector.register_backend("local", LocalCollector)
Collector.register_backend("dummy", DummyCollector)
