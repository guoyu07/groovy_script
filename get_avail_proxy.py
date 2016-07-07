#!/usr/bin/env python
################################################################
#
#  Look up the parameters for a UPC, if it requires a proxy number
#  to generate a card, try making one NOT already in the card table
#
################################################################

import os.path, re
import subprocess, types
import sys, getpass
import getopt, random

class DBConnect:
   def __init__(self,
                db_host=None,
                user_name='',
                password='',
                db_name='cps_dbs'):
      self.dbHost = db_host
      self.userName = user_name
      self.pw = password
      self.defaultDatabase = db_name

   def ready(self):
      return self.dbHost and self.userName

   def setHost(self, db_host):
      self.dbHost = db_host

   # this forces a "use" on each execute
   def setDatabase(self, db_name):
      self.defaultDatabase = db_name
      
   def setUser(self, user_name, password=None):
      self.userName = user_name
      self.pw = password

   def execute(self, action, user_name = None, password = None):
      if not self.ready():
         print 'DBConnect connection params not set, execute failed'
         return None
      if user_name:
         self.userName = user_name
      if password:
         self.pw = password
      if not self.userName:
         print 'DBConnect missing database server login parameters, execute failed'
         return None
      if not action:
         print 'DBConnect no action specified'
         return None

      # build up the command line
      dbName = ''
      if self.defaultDatabase:
         dbName = 'use {0}; '.format(self.defaultDatabase)
         
      mysqlCmd = ['mysql', '-P', '3306', '-h', self.dbHost,
                  '-u', self.userName, '-p',
                  '--execute={0}{1}'.format(dbName, action)]
      
      proc = subprocess.Popen(mysqlCmd, stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

      results, errors = proc.communicate()
      if errors:
         errorHeader = ''
         if type(errors) == types.StringType:
            for line in errors.split('\n'):
               scrub = line.replace('Enter password: ', '')
               if len(scrub) > 0:
                  if not errorHeader:
                     errorHeader = 'Database returned error message:'
                     print errorHeader
                  print '{}'.format(scrub)
         else:
            print '\n'.join(errors)
      if type(results) == types.StringType:
         return self.parseReturn(results)
      else:
         print 'DBConnect: complex return type not handled'
      return None
   # end execute

   # internal method, consume the results and try to package it
   # Assume the first "row" consists of column names:
   # Col1 <tab > Col2 <tab> Col3
   # Then each row has the row values, tab-separated
   # make each row into a dictionary, column name for the key:
   # { 'Col1' : 'val1', 'Col2' : 'val2', 'Col3' : 'val3' }
   # Return a tuple, containing the list of column names, and a
   # list of the dictionaries
   # That busy nuff ferya?
   def parseReturn(self, results):
      parts = results.split('\n')
      if not parts[-1]:
         parts.pop()
      if not len(parts):
         return ((), ())
      headings = parts[0].split('\t')
      if len(headings) == 1 and not headings[0]:
         headings = [ ]
      rows = list(())
      for row in parts[1:]:
         vals = row.split('\t')
         if len(vals) < len(headings):
            continue
         retRow = dict(())
         valIndex = 0
         for val in vals:
            retRow[headings[valIndex]] = val
            valIndex += 1
         if len(retRow) > 0:
            rows.append(retRow)
      return (headings, rows)

# end class DBConnect

# A utility to print the results above in some common setup
def printResults(results):
   starter = ''
   for head in results[0]:
      print '{0}{1}'.format(starter, head),
      starter = '| '
   if starter:
      print
   for row in results[1]:
      starter = ''
      for head in results[0]:
         print '{0}{1}'.format(starter, row[head]),
         starter = '| '
      if starter:
         print

   print 'Result table contains {0} columns and {1} rows'.format(len(results[0]),
                                                                 len(results[1]))

# check digit calc
def checkDigit(card):
   sum = 0
   double = 1
   for dig in card[-1::-1]:
      if double:
         work = int(dig) * 2
         if work > 9:
            sum += int(work / 10) + (work % 10)
         else:
            sum += int(work)
         double = 0
      else:
         sum += int(dig)
         double = 1
   sum *= 9
   return sum % 10

# make a proxy card number, check the db
def makeProxyCard(conn, binVal, rangeVal, length):
   tries = 0
   while True:
      returnVal = binVal + rangeVal
      returnVal += ''.join(random.sample('0123456789', int(length) - len(returnVal) - 1))
      dig = checkDigit(returnVal)
      tries += 1
      res = conn.execute('select proxy_card_number from card where proxy_card_number = {0}{1}'.format(returnVal, dig))
      if not res[0]:
         return '{0}{1}'.format(returnVal, dig)
      if tries % 10 == 0:
         print('Looked for {0} proxy numbers, continuing'.format(tries))
   
#### MAIN
import cps_utils
    
Usage = '%s: [ -h ] [ -d ] --host=<db_hostname> --username=<user_name> <UPC>' % sys.argv[0]

try:
   options, args = getopt.getopt(sys.argv[1:], 'dh', ['debug', 'help', 'host=', 'username='])
except getopt.GetoptError as e:
   print('Error reading the command line: \'{0}\''.format(str(e)))
   sys.exit(2)

DBHost = None
Username = None
for (option, argument) in options:
   if option == '-h' or option == '--help':
      print(Usage)
      sys.exit(0)
   elif option == '-d' or option == '--debug':
      DebugFlag = True
   elif option == '--host':
      DBHost = argument
   elif option == '--username':
      Username = argument
   else:
      print('Error reading the command line, argument \'{0}\' not understood'.format(option))
      sys.exit(1)

if not DBHost or not Username:
   sys.exit(Usage)
   
if len(args) != 1:
   sys.exit('UPC not found\n' + Usage)

Connection = DBConnect(DBHost, Username, None)
res = Connection.execute('SELECT upc, proxy_bin, proxy_range, proxy_card_number_length, proxy_gen_type FROM product_config WHERE upc = \'{0}\''.format(args[0]))

if not res:
   sys.exit('No information found for UPC {}'.format(args[0]))
headings = res[0]
data = res[1][0]
if data['proxy_gen_type'] == 'REQUIRE_PROXY':
   print(makeProxyCard(Connection, data['proxy_bin'], data['proxy_range'], data['proxy_card_number_length']))

