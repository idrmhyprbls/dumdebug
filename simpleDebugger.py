# purpose:     prints a variable debugging xterm window using a separate
#              subprocess. communicating is via pipes, data is transferred
#              with pickles. the window is updated when the update
#              function of a NewWindow instance is called. multiple
#              windows my be invoked by creating multiple instances
#              (handles) of the NewWindow class
# os:          linux
# python ver:  2.4+
# permissions: must have write permission on /tmp/
# notes:       there must be some delay between successive calls to update,
#              otherwise the debugging window won't be allowed enough time to
#              update via its pipes (requires file open/r/w/close), that
#              must be no less than ~2ms
# usage:       import simpleDebugger
#              debug_window = simpleDebugger.NewWindow()
#              debug_window.update(locals())
# bugs:        read/write operation of pipes misses frames without a 3ms delay
# future:      use curses to make window more dynamic and versatile

import os
import subprocess
import sys
import time
import cPickle as pickle

class WindowHandler(object):

   # remembers total window count in order to assign pipe names
   windowCount = 0

class NewWindow(WindowHandler):

   def __init__(self):
      number = WindowHandler.windowCount
      self.pipe = '/tmp/simpleDebugger' + str(number) + '.pipe'
      self.subp = None

      try:
         # create pipe
         (lambda: os.mkfifo(self.pipe), lambda: None)[os.path.exists( \
            self.pipe)]()

         try:
            # open new xterm running debugger in a separate process
            options = ['xterm','+sb','+hold','+aw', '-geometry', '118x62', \
               '-bg','black','-fg','green','-T', self.pipe, \
               '+ah', '+bc', '-cr', 'black', '-uc', '-e','python',  \
               './simpleDebugger.py', str(number)]
            self.subp = subprocess.Popen(options, shell=False)

         except:

            try:
               os.remove(self.pipe) 

            except:
               raise
            print "sD> Error: debugger window %d subprocess not started, \
ignoring all calls!" % number

      except:
         print "sD> Error: Could not create FIFO for window %d, ignoring \
all calls!" % number

      WindowHandler.windowCount += 1

   # usage 1: .update(locals())
   # usage 2: .update({'c':c,'x':x})
   # usage 3: .update(mkDict(locals(),'c','x'))
   # purpose: writes pickled data to the pipe, updating debug window.
   #          function return True so may be used in a while loop. the
   #          debug parameter also allows for an artificial delay if you
   #          expect to make repeated successive calls and want to see
   #          realtime, uninterrupted, debug data
   def update(self, variables = {}, delay = 0.0):

      try:
         # non-blocking named pipe
         sout = os.open(self.pipe,os.O_RDWR|os.O_NONBLOCK) 
         try: 
            # send a pickle via named pipe
            os.write(sout,pickle.dumps(sorted([(str(k),str(v),str(type(v))) \
               for (k, v) in variables.items()]))) 

         finally: 
            os.close(sout) # stay safe
            if delay > 0.0:
               time.sleep(delay)

      except OSError: 
         # pass if the pipe doesn't exist
         pass 

      return True 

# usage: returns a new dictionary using the args found in the passed dict
def makeVarDict(l = {}, *args):

   d = {}
   for item in args:
      try:
         d[item] = l.pop(item)
      except KeyError:
         continue
   return d

# main is run only from the xterm window, which is called in a subprocess
# upon invokation of a NewWindow
def main():

   args = sys.argv
   number = None
   output = ''

   if len(args) != 2:
      print "sD> Error: Argument count to subprocess is wrong, is %d should \
be 1!" % (len(args) - 1)
      sys.exit()
   try:
      number = int(args[1])

   except ValueError:
      print "sD> Error: None-integer %s was passed to subprocess!" % \
         str(args[1])
      sys.exit()

   pipe = '/tmp/simpleDebugger' + str(number) + '.pipe'

   while True: 

      try:
         sin = open(pipe,'r') # blocking

         try:
            # clear screen before print, do this after the blocking read!
            subprocess.call('clear')
            # print a header and a de-pickled var list in columns
            output = "SimpleDebugger\n".rjust(48) + "="*80 + '\n' + \
               '\n'.join("%s: %s %s= %s" % \
               (str(c+1).replace('-1','#')[:2].ljust(2), \
               e[0][:15].ljust(16), \
               e[2][:28].strip('<').strip('>').ljust(29), \
               e[1].replace('\n','\n' + ''.rjust(52))) for (c, e) in \
               ([(-2,('VARIABLE','VALUE','TYPE'))] + \
               list(enumerate(pickle.load(sin))))) + '\n' + "="*80 + '\n' + \
               "sD> PAUSE/EXIT: <Ctrl-C>" + '\n'
            sys.stdout.write(output)
            sys.stdout.write("sD> ")
            sys.stdout.flush()
         finally: sin.close() # stay safe and close pipe

      # paused
      except KeyboardInterrupt: 
         try:
            choice = raw_input("\nsD> EXIT: <Ctrl-C | D> | Q | E  -  \
CONTINUE: <ENTER>  -  SAVE: S\nsD> ")
            if choice:
               if choice[0].upper() == 'Q' or choice[0].upper() == 'E':
                  raise KeyboardInterrupt
               elif choice[0].upper() == 'S':
                  lt = time.localtime()
                  fn = "sD_snap_" + str(lt.tm_year) + str(lt.tm_mon) + \
                       str(lt.tm_mday) + str(lt.tm_hour) + str(lt.tm_min) + \
                       str(lt.tm_sec) + ".txt"
                  try:
                     fh = open(fn, 'w')
                     try:
                        fh.write(output)
                     finally:
                        fh.close()
                     print "sD> Snapped screen to '%s'." % fn
                     print "sD> Continuing..."
                     time.sleep(2)
                  except:
                     print "sD> Error: File could not be written to!"
                     time.sleep(1.5)
                  # continue
               else:
                  # continue
	          print "sD> Continuing..."
                  time.sleep(1)
            else:
	       print "sD> Continuing..."
               time.sleep(1)

         # breaks look upon 2 consecutive ^C's
         except (KeyboardInterrupt, EOFError):
            try:
               os.remove(pipe) 
            except OSError:
               print "sD> Error: could not find pipe %s to delete!" % pipe
               raise
            print "\nsD> This window may be closed now..."
            break

      except IOError:
         print "sD> Error: Could not find pipe %s!" % pipe
         raise

if __name__ == "__main__":
      main()

