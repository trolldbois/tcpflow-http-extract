#!/usr/bin/env python 

import sys
import argparse
import cStringIO
import httplib 

class HttpReplyException(Exception):
  pass

class FileSocket(file):
  @classmethod
  def make(cls, fname, pos):
    me = cls(fname,'rb')
    me.currentpos = pos
    me.seek(pos)
    #print 'file positionned at offset %d'%(me.currentpos) 
    return me
  def makefile(self, mode, bufsize):
    return self
  def close(self):
    self.currentpos = self.tell()
  def getCurrentPos(self):
    return self.currentpos
  
def getFilename(fname,pos):
  return '%s.contentatoffset.%d'%(fname,pos)

def readHeaders(response, fs, fname, data, pos):

  response.begin()
  headers = response.getheaders()
  content = response.read()
  print 'HTTPmethod', response.version, response.status, response.reason

  length = len(content)
  if length == 0 :
    print 'no content to extract'
  else:
    outfname = getFilename(fname,pos)
    file(outfname,'wb').write(content)
    print 'extracted %d bytes to %s'%(length, outfname)

  return fs.getCurrentPos()


def extract(opts):
  fname = opts.tcpflow.name
  data = opts.tcpflow.read()
  pos = 0
  
  while pos < len(data):
    fs = FileSocket.make(fname, pos)
    response = httplib.HTTPResponse(fs)
    if not data[pos:].startswith('HTTP') :
      print 'offset %d Does not start with HTTP.'%(pos, data[pos:pos+10])
      break
    pos = readHeaders(response, fs, fname, data,pos)
  
  
def argparser():
  """
    Builds the argparse tree.
    See the command line --help .
  """
  rootparser = argparse.ArgumentParser(prog='tcpflow-extract-http', description='Extract http files from flow.')
  rootparser.add_argument('--debug', dest='debug', action='store_const', const=True, help='setLevel to DEBUG')
  rootparser.add_argument('tcpflow', type=argparse.FileType('r'), help='src tcpflow')
  rootparser.set_defaults(func=extract)
  return rootparser

def main(argv):
  parser = argparser()
  opts = parser.parse_args(argv)
  opts.func(opts)



if __name__ == '__main__': 
  main(sys.argv[1:])
