import logging
import copy

class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   From http://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/ 
   We use this to capture NIDAQ output that gets sent to stderr.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''
 
   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())

   def flush(self):
       # no need to do anything on flush because logging is synchronous
       pass


class TeeStreams(object):
   """Send output for one stream to multiple streams, like 'tee'"""
   _streamList = None
   def __init__(self, stream1, stream2):
      self._streamList = []
      self._streamList.append(stream1)
      self._streamList.append(stream2)
   def write(self, data):
      for s in self._streamList:
         if s is not None:
            s.write(data)
   def flush(self):
      for s in self._streamList:
         if s is not None:
            s.flush()

class TeeStreamsBlockable(TeeStreams):
   """Extends TeeStreams to allow blocking/unblocking streams (temporarily discarding their output)"""
   _streamListOrig = None
   def __init__(self, stream1, stream2):
      super(TeeStreamsBlockable, self).__init__(stream1, stream2)
      self._streamListOrig = copy.copy(self._streamList)
   def blockStream(self, streamN):
      if streamN < 0 or streamN >= len(self._streamList):
         raise RuntimeError('Unknown stream number %d' % streamN)
      self._streamList[streamN] = None
   def unblockStream(self, streamN):
      if streamN < 0 or streamN >= len(self._streamList):
         raise RuntimeError('Unknown stream number %d' % streamN)
      self._streamList[streamN] = self._streamListOrig[streamN]


