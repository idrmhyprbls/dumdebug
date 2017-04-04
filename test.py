#!/bin/env python

from simpleDebugger import *
import time

class Class(object):
   def __init__(self):
      self.x = 'Hello'
      self.c = self.x.count('o')
      self.l = len(self.x)
      self.y = [self.c,self.l]
   def __str__(self):
      return "x:%s, y:%s" % (self.x,self.y)
   def update(self):
      self.yself.x

def main():
   print "START"
   doubles = 0
   passnum = 0
   even = False
   C = Class()
   try:
      while loop(vars()):
         passnum += 1
         doubles += 2
         if passnum % 2:
            even = False
         else:
            even = True
         if even:
            C.x += C.x[-1]
         if passnum < 75:
            time.sleep(.05)
            continue
         else:
            break
   except:
      raise
   print "END"

if __name__ == "__main__":
   main()
