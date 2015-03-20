#
# Autogenerated by Thrift Compiler (0.9.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:new_style
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None



class Tariff(object):
  """
  Attributes:
   - number
   - c_tar
   - summ_tar
   - date_b
   - date_e
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'number', None, None, ), # 1
    (2, TType.STRING, 'c_tar', None, None, ), # 2
    (3, TType.DOUBLE, 'summ_tar', None, None, ), # 3
    (4, TType.I64, 'date_b', None, None, ), # 4
    (5, TType.I64, 'date_e', None, None, ), # 5
  )

  def __init__(self, number=None, c_tar=None, summ_tar=None, date_b=None, date_e=None,):
    self.number = number
    self.c_tar = c_tar
    self.summ_tar = summ_tar
    self.date_b = date_b
    self.date_e = date_e

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
        if ftype == TType.I32:
          self.number = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.c_tar = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.DOUBLE:
          self.summ_tar = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.I64:
          self.date_b = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.I64:
          self.date_e = iprot.readI64();
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
    oprot.writeStructBegin('Tariff')
    if self.number is not None:
      oprot.writeFieldBegin('number', TType.I32, 1)
      oprot.writeI32(self.number)
      oprot.writeFieldEnd()
    if self.c_tar is not None:
      oprot.writeFieldBegin('c_tar', TType.STRING, 2)
      oprot.writeString(self.c_tar)
      oprot.writeFieldEnd()
    if self.summ_tar is not None:
      oprot.writeFieldBegin('summ_tar', TType.DOUBLE, 3)
      oprot.writeDouble(self.summ_tar)
      oprot.writeFieldEnd()
    if self.date_b is not None:
      oprot.writeFieldBegin('date_b', TType.I64, 4)
      oprot.writeI64(self.date_b)
      oprot.writeFieldEnd()
    if self.date_e is not None:
      oprot.writeFieldBegin('date_e', TType.I64, 5)
      oprot.writeI64(self.date_e)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.number is None:
      raise TProtocol.TProtocolException(message='Required field number is unset!')
    if self.c_tar is None:
      raise TProtocol.TProtocolException(message='Required field c_tar is unset!')
    if self.summ_tar is None:
      raise TProtocol.TProtocolException(message='Required field summ_tar is unset!')
    if self.date_b is None:
      raise TProtocol.TProtocolException(message='Required field date_b is unset!')
    if self.date_e is None:
      raise TProtocol.TProtocolException(message='Required field date_e is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Error(object):
  """
  Attributes:
   - code
   - message
  """

  thrift_spec = (
    None, # 0
    (1, TType.I16, 'code', None, None, ), # 1
    (2, TType.STRING, 'message', None, None, ), # 2
  )

  def __init__(self, code=None, message=None,):
    self.code = code
    self.message = message

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
        if ftype == TType.I16:
          self.code = iprot.readI16();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.message = iprot.readString();
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
    oprot.writeStructBegin('Error')
    if self.code is not None:
      oprot.writeFieldBegin('code', TType.I16, 1)
      oprot.writeI16(self.code)
      oprot.writeFieldEnd()
    if self.message is not None:
      oprot.writeFieldBegin('message', TType.STRING, 2)
      oprot.writeString(self.message)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.code is None:
      raise TProtocol.TProtocolException(message='Required field code is unset!')
    if self.message is None:
      raise TProtocol.TProtocolException(message='Required field message is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Result(object):
  """
  Attributes:
   - number
   - c_tar
   - error
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'number', None, None, ), # 1
    (2, TType.STRING, 'c_tar', None, None, ), # 2
    (3, TType.STRUCT, 'error', (Error, Error.thrift_spec), None, ), # 3
  )

  def __init__(self, number=None, c_tar=None, error=None,):
    self.number = number
    self.c_tar = c_tar
    self.error = error

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
        if ftype == TType.I32:
          self.number = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.c_tar = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRUCT:
          self.error = Error()
          self.error.read(iprot)
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
    oprot.writeStructBegin('Result')
    if self.number is not None:
      oprot.writeFieldBegin('number', TType.I32, 1)
      oprot.writeI32(self.number)
      oprot.writeFieldEnd()
    if self.c_tar is not None:
      oprot.writeFieldBegin('c_tar', TType.STRING, 2)
      oprot.writeString(self.c_tar)
      oprot.writeFieldEnd()
    if self.error is not None:
      oprot.writeFieldBegin('error', TType.STRUCT, 3)
      self.error.write(oprot)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.number is None:
      raise TProtocol.TProtocolException(message='Required field number is unset!')
    if self.c_tar is None:
      raise TProtocol.TProtocolException(message='Required field c_tar is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class SQLException(TException):
  """
  Attributes:
   - message
   - code
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'message', None, None, ), # 1
    (2, TType.I32, 'code', None, None, ), # 2
  )

  def __init__(self, message=None, code=None,):
    self.message = message
    self.code = code

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
        if ftype == TType.STRING:
          self.message = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.code = iprot.readI32();
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
    oprot.writeStructBegin('SQLException')
    if self.message is not None:
      oprot.writeFieldBegin('message', TType.STRING, 1)
      oprot.writeString(self.message)
      oprot.writeFieldEnd()
    if self.code is not None:
      oprot.writeFieldBegin('code', TType.I32, 2)
      oprot.writeI32(self.code)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __str__(self):
    return repr(self)

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class InvalidArgumentException(TException):
  """
  Attributes:
   - message
   - code
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'message', None, None, ), # 1
    (2, TType.I32, 'code', None, None, ), # 2
  )

  def __init__(self, message=None, code=None,):
    self.message = message
    self.code = code

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
        if ftype == TType.STRING:
          self.message = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.code = iprot.readI32();
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
    oprot.writeStructBegin('InvalidArgumentException')
    if self.message is not None:
      oprot.writeFieldBegin('message', TType.STRING, 1)
      oprot.writeString(self.message)
      oprot.writeFieldEnd()
    if self.code is not None:
      oprot.writeFieldBegin('code', TType.I32, 2)
      oprot.writeI32(self.code)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __str__(self):
    return repr(self)

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)