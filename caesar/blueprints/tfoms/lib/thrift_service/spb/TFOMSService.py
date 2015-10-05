# -*- encoding: utf-8 -*-
#
# Autogenerated by Thrift Compiler (0.9.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:new_style,utf8strings
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class Iface(object):
  def getRegistry(self, begInterval, endInterval):
    """
    Parameters:
     - begInterval
     - endInterval
    """
    pass


class Client(Iface):
  def __init__(self, iprot, oprot=None):
    self._iprot = self._oprot = iprot
    if oprot is not None:
      self._oprot = oprot
    self._seqid = 0

  def getRegistry(self, begInterval, endInterval):
    """
    Parameters:
     - begInterval
     - endInterval
    """
    self.send_getRegistry(begInterval, endInterval)
    return self.recv_getRegistry()

  def send_getRegistry(self, begInterval, endInterval):
    self._oprot.writeMessageBegin('getRegistry', TMessageType.CALL, self._seqid)
    args = getRegistry_args()
    args.begInterval = begInterval
    args.endInterval = endInterval
    args.write(self._oprot)
    self._oprot.writeMessageEnd()
    self._oprot.trans.flush()

  def recv_getRegistry(self, ):
    (fname, mtype, rseqid) = self._iprot.readMessageBegin()
    if mtype == TMessageType.EXCEPTION:
      x = TApplicationException()
      x.read(self._iprot)
      self._iprot.readMessageEnd()
      raise x
    result = getRegistry_result()
    result.read(self._iprot)
    self._iprot.readMessageEnd()
    if result.success is not None:
      return result.success
    if result.intervalException is not None:
      raise result.intervalException
    raise TApplicationException(TApplicationException.MISSING_RESULT, "getRegistry failed: unknown result");


class Processor(Iface, TProcessor):
  def __init__(self, handler):
    self._handler = handler
    self._processMap = {}
    self._processMap["getRegistry"] = Processor.process_getRegistry

  def process(self, iprot, oprot):
    (name, type, seqid) = iprot.readMessageBegin()
    if name not in self._processMap:
      iprot.skip(TType.STRUCT)
      iprot.readMessageEnd()
      x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
      oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
      x.write(oprot)
      oprot.writeMessageEnd()
      oprot.trans.flush()
      return
    else:
      self._processMap[name](self, seqid, iprot, oprot)
    return True

  def process_getRegistry(self, seqid, iprot, oprot):
    args = getRegistry_args()
    args.read(iprot)
    iprot.readMessageEnd()
    result = getRegistry_result()
    try:
      result.success = self._handler.getRegistry(args.begInterval, args.endInterval)
    except InvalidDateIntervalException as intervalException:
      result.intervalException = intervalException
    oprot.writeMessageBegin("getRegistry", TMessageType.REPLY, seqid)
    result.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()


# HELPER FUNCTIONS AND STRUCTURES

class getRegistry_args(object):
  """
  Attributes:
   - begInterval
   - endInterval
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'begInterval', None, None, ), # 1
    (2, TType.I64, 'endInterval', None, None, ), # 2
  )

  def __init__(self, begInterval=None, endInterval=None,):
    self.begInterval = begInterval
    self.endInterval = endInterval

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I64:
          self.begInterval = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I64:
          self.endInterval = iprot.readI64();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('getRegistry_args')
    if self.begInterval is not None:
      oprot.writeFieldBegin('begInterval', TType.I64, 1)
      oprot.writeI64(self.begInterval)
      oprot.writeFieldEnd()
    if self.endInterval is not None:
      oprot.writeFieldBegin('endInterval', TType.I64, 2)
      oprot.writeI64(self.endInterval)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class getRegistry_result(object):
  """
  Attributes:
   - success
   - intervalException
  """

  thrift_spec = (
    (0, TType.STRUCT, 'success', (Registry, Registry.thrift_spec), None, ), # 0
    (1, TType.STRUCT, 'intervalException', (InvalidDateIntervalException, InvalidDateIntervalException.thrift_spec), None, ), # 1
  )

  def __init__(self, success=None, intervalException=None,):
    self.success = success
    self.intervalException = intervalException

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 0:
        if ftype == TType.STRUCT:
          self.success = Registry()
          self.success.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 1:
        if ftype == TType.STRUCT:
          self.intervalException = InvalidDateIntervalException()
          self.intervalException.read(iprot)
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('getRegistry_result')
    if self.success is not None:
      oprot.writeFieldBegin('success', TType.STRUCT, 0)
      self.success.write(oprot)
      oprot.writeFieldEnd()
    if self.intervalException is not None:
      oprot.writeFieldBegin('intervalException', TType.STRUCT, 1)
      self.intervalException.write(oprot)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
