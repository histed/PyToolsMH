import logging

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

 
