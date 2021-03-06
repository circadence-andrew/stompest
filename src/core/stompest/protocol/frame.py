# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from stompest.six import binaryType, textType

from stompest.protocol.spec import StompSpec
from stompest.protocol.util import escape

class StompFrame(object):
    """This object represents a STOMP frame.
    
    :param command: A valid STOMP command.
    :param headers: The STOMP headers (represented as a :class:`dict`), or :obj:`None` (no headers).
    :param body: The frame body. The bodywill be cast as a binary string :class:`str` (Python 2) or :class:`bytes` (Python 3).
    :param rawHeaders: The raw STOMP headers (represented as a collection of (header, value) pairs), or :obj:`None` (no raw headers).
    :param version: A valid STOMP protocol version, or :obj:`None` (equivalent to the :attr:`DEFAULT_VERSION` attribute of the :class:`~.StompSpec` class).
        
    .. note :: The frame's attributes are internally stored as arbitrary Python objects. The frame's :attr:`version` attribute controls the wire-level encoding of its :attr:`command` and :attr:`headers` (depending on STOMP protocol version, this may be ASCII or UTF-8), while its :attr:`body` is not encoded at all (it's just cast as a :class:`str`).
    
    **Example**:
    
    >>> from stompest.protocol import StompFrame, StompSpec
    >>> frame = StompFrame(StompSpec.SEND, rawHeaders=[('foo', 'bar1'), ('foo', 'bar2')])
    >>> frame
    StompFrame(command='SEND', rawHeaders=[('foo', 'bar1'), ('foo', 'bar2')])
    >>> bytes(frame)
    b'SEND\\nfoo:bar1\\nfoo:bar2\\n\\n\\x00'
    >>> dict(frame)
    {'command': 'SEND', 'rawHeaders': [('foo', 'bar1'), ('foo', 'bar2')]}
    >>> frame.headers
    {'foo': 'bar1'}
    >>> frame.headers = {'foo': 'bar3'}
    >>> frame.headers
    {'foo': 'bar1'}
    >>> frame.unraw()
    >>> frame
    StompFrame(command=u'SEND', headers={'foo': 'bar1'})
    >>> bytes(frame)
    b'SEND\\nfoo:bar1\\n\\n\\x00'
    >>> frame.headers = {'foo': 'bar4'}
    >>> frame.headers
    {'foo': 'bar4'}
    >>> frame = StompFrame(StompSpec.SEND, rawHeaders=[('some french', b'fen\xc3\xaatre'.decode('utf-8'))], version=StompSpec.VERSION_1_0)
    >>> bytes(frame)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    UnicodeEncodeError: 'ascii' codec can't encode character '\xea' in position 3: ordinal not in range(128)
    >>> frame.version = StompSpec.VERSION_1_1
    >>> bytes(frame)
    b'SEND\\nsome french:fen\\xc3\\xaatre\\n\\n\\x00'
    >>> import codecs
    >>> c = codecs.lookup('utf-8')
    >>> c.decode(binaryType(frame))
    ('SEND\nsome french:fenêtre\n\n\x00', 28)
    
    """
    INFO_LENGTH = 20
    _KEYWORDS_AND_FIELDS = [('headers', '_headers', {}), ('body', 'body', b''), ('rawHeaders', 'rawHeaders', None), ('version', 'version', StompSpec.DEFAULT_VERSION)]

    def __init__(self, command, headers=None, body=b'', rawHeaders=None, version=None):
        self.version = version

        self.command = command
        self.headers = headers
        self.body = body
        self.rawHeaders = rawHeaders

    def __eq__(self, other):
        """Two frames are considered equal if, and only if, they render the same wire-level frame, that is, if their string representation is identical."""
        return self.__str__() == other.__str__()

    __hash__ = None

    def __iter__(self):
        yield ('command', self.command)
        for (keyword, field, default) in self._KEYWORDS_AND_FIELDS:
            value = getattr(self, field)
            if value != default:
                yield (keyword, getattr(self, field))

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join(
            ('%s=%s' % (keyword, repr(value)))
            for (keyword, value) in self
        ))

    def __bytes__(self):
        return self.__str__()

    def __str__(self):
        """Render the wire-level representation of a STOMP frame."""
        headers = sorted(self.headers.items()) if self.rawHeaders is None else self.rawHeaders
        headers = ''.join('%s:%s%s' % (self._escape(textType(key)), self._escape(textType(value)), StompSpec.LINE_DELIMITER) for (key, value) in headers)
        return self._encode(StompSpec.LINE_DELIMITER).join([self._encode(self.command), self._encode(headers), b''.join([self.body, self._encode(StompSpec.FRAME_DELIMITER)])])

    def __unicode__(self):
        return self._decode(self.__str__())

    def info(self):
        """Produce a log-friendly representation of the frame (show only non-trivial content, and truncate the message to INFO_LENGTH characters)."""
        headers = self.headers and 'headers=%s' % self.headers
        body = self.body[:self.INFO_LENGTH]
        if body not in self.body:
            body = '%s...' % body
        body = body and ('body=%s' % repr(body))
        version = 'version=%s' % self.version
        info = ', '.join(i for i in (headers, body, version) if i)
        return '%s frame [%s]' % (self.command, info)

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = StompSpec.version(value)

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = textType(value)

    @property
    def headers(self):
        return self._headers if (self.rawHeaders is None) else dict(reversed(self.rawHeaders))

    @headers.setter
    def headers(self, value):
        self._headers = dict(value or {})

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = binaryType(value)

    def unraw(self):
        """If the frame has raw headers, copy their deduplicated version to the :attr:`headers` attribute, and remove the raw headers afterwards."""
        if self.rawHeaders is None:
            return
        self.headers = self.headers
        self.rawHeaders = None

    @property
    def _codec(self):
        return StompSpec.codec(self.version)

    def _decode(self, bytestring):
        return self._codec.decode(bytestring)[0]

    def _encode(self, text):
        return self._codec.encode(text)[0]

    def _escape(self, text):
        return escape(self.version)(self.command, text)

class StompHeartBeat(object):
    """This object represents a STOMP heart-beat. Its string representation (via :meth:`__str__`) renders the wire-level STOMP heart-beat."""
    __slots__ = ('version',)

    def __eq__(self, other):
        return isinstance(other, StompHeartBeat)

    __hash__ = None

    def __bool__(self):
        return False

    def __nonzero__(self):
        return self.__bool__()

    def __repr__(self):
        return '%s()' % self.__class__.__name__

    def __bytes__(self):
        return self.__str__()

    def __str__(self):
        return StompSpec.LINE_DELIMITER.encode()

    def __unicode__(self):
        return self.__str__().decode()

    def info(self):
        return 'heart-beat'
