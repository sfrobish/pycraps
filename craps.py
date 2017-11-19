#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  craps.py
#
#  Copyright 2016 Steven Frobish <sfrobish@sfrobish>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from __future__ import division
from random import randrange

import os

import matplotlib.pyplot as plt
import numpy as np

import json
import getopt

import copy


def initboard(board):
  board["passbet"]         = 0
  board["passoddsbet"]     = 0
  board["passpay"]         = 0
  board["passoddspay"]     = 0
  board["dontpassbet"]     = 0
  board["dontpassoddsbet"] = 0
  board["dontpasspay"]     = 0
  board["dontpassoddspay"] = 0
  board["comelinebet"]     = 0
  board["comelinepay"]     = 0
  board["comebet"]         = np.zeros((12,))
  board["comeoddsbet"]     = np.zeros((12,))
  board["comepay"]         = np.zeros((12,))
  board["comeoddspay"]     = np.zeros((12,))
  board["dontcomebet"]     = np.zeros((12,))
  board["dontcomeoddsbet"] = np.zeros((12,))
  board["dontcomepay"]     = np.zeros((12,))
  board["dontcomeoddspay"] = np.zeros((12,))
  # Place bets are assumed 'to win'
  board["placebet"]        = np.zeros((12,))
  board["placepay"]        = np.zeros((12,))
  # Not messing with commission bets
  #board["laybet"]          = np.zeros((12,))
  #board["laypay"]          = np.zeros((12,))
  #board["buybet"]          = np.zeros((12,))
  #board["buypay"]          = np.zeros((12,))
  board["hard4bet"]        = 0
  board["hard4pay"]        = 0
  board["hard6bet"]        = 0
  board["hard6pay"]        = 0
  board["hard8bet"]        = 0
  board["hard8pay"]        = 0
  board["hard10bet"]       = 0
  board["hard10pay"]       = 0
  # Single roll bets ignored for now (because only suckers play them)


def initshooterstats(shooter):

  shooter["lowstreak"]  = 999
  shooter["highstreak"] = 0
  shooter["numtosses"]  = 0
  shooter["numrounds"]  = 0
  shooter["streakdist"] = np.zeros((75,))
  shooter["totwagered"] = 0
  shooter["totpaid"]    = 0


def placebets(board, button, roll):

  passcomewager = 5
  passcomeodds = passcomewager * 2
  passcomeincr = passcomewager
  placewager = 5

  if button == 'off':
    if board["passbet"] == 0:
      board["passbet"] = passcomewager
  else:
    if board["passoddsbet"] == 0:
      board["passoddsbet"] = passcomeodds

    board["comelinebet"] = passcomewager

    for x in [4, 5, 6, 8, 9, 10]:
      # First try to put place bets down, but only if no come bet is established
      if x != button and board["placebet"][x-1] == 0 and board["comebet"][x-1] == 0:
        if x in [4, 10]:
          board["placebet"][x-1] = 5
        elif x in [5, 9]:
          board["placebet"][x-1] = 5
        elif x in [6, 8]:
          board["placebet"][x-1] = 6

    # Next try to add comeodds
    if roll != button and board["comebet"][roll-1] != 0:
      if board["comeoddsbet"][roll-1] == 0:
        board["comeoddsbet"][roll-1] = passcomeodds
      else:
        board["comeoddsbet"][roll-1] += passcomeincr


def addboards(board, board2):

  for key in board.keys():
    if isinstance(board[key], list):
      for x in board[key]:
        board[key][x] += board2[key][x]
    else:
      board[key] += board2[key]


def clearboardpays(board):

  board["passpay"]         = 0
  board["passoddspay"]     = 0
  board["dontpasspay"]     = 0
  board["dontpassoddspay"] = 0
  board["comelinepay"]     = 0
  board["comepay"]         = np.zeros((12,))
  board["comeoddspay"]     = np.zeros((12,))
  board["dontcomepay"]     = np.zeros((12,))
  board["dontcomeoddspay"] = np.zeros((12,))
  board["placepay"]        = np.zeros((12,))
  board["hard4pay"]        = 0
  board["hard6pay"]        = 0
  board["hard8pay"]        = 0
  board["hard10pay"]       = 0

def jsonify(board):

  newboard                    = copy.deepcopy(board)
  newboard["comebet"]         = board["comebet"].tolist()
  newboard["comepay"]         = board["comepay"].tolist()
  newboard["comeoddsbet"]     = board["comeoddsbet"].tolist()
  newboard["comeoddspay"]     = board["comeoddspay"].tolist()
  newboard["dontcomebet"]     = board["dontcomebet"].tolist()
  newboard["dontcomepay"]     = board["dontcomepay"].tolist()
  newboard["dontcomeoddsbet"] = board["dontcomeoddsbet"].tolist()
  newboard["dontcomeoddspay"] = board["dontcomeoddspay"].tolist()
  newboard["placebet"]        = board["placebet"].tolist()
  newboard["placepay"]        = board["placepay"].tolist()
  return newboard

def paybets(curboard, totboard, button, roll):

  if roll == button:
    # Pass line bet
    totboard["passbet"] += curboard["passbet"]
    totboard["passpay"] += curboard["passbet"] * 2
    curboard["passbet"] = 0

    # Pass odds bet
    totboard["passoddsbet"] += curboard["passoddsbet"]
    if roll in [4, 10]:
      totboard["passoddspay"] += curboard["passoddsbet"] + (curboard["passoddsbet"] * 2)
    elif roll in [5, 9]:
      totboard["passoddspay"] += curboard["passoddsbet"] + (curboard["passoddsbet"] * (3/2))
    elif roll in [6, 8]:
      totboard["passoddspay"] += curboard["passoddsbet"] + (curboard["passoddsbet"] * (6/5))
    curboard["passoddsbet"] = 0

    # If a come bet exists move it the number that was just hit
    curboard["comebet"][roll-1] = curboard["comelinebet"]
    curboard["comelinebet"] = 0

  elif button == 'off' and roll in [7, 11]:
    totboard["passbet"] += curboard["passbet"]
    totboard["passpay"] += curboard["passbet"] * 2
    totboard["comelinebet"] += curboard["comelinebet"]
    totboard["comelinepay"] += curboard["comelinebet"] * 2
    curboard["passbet"] = 0
    curboard["comelinebet"] = 0

  elif button == 'off' and roll in [2, 3, 12]:
    totboard["passbet"] += curboard["passbet"]
    curboard["passbet"] = 0
    totboard["comelinebet"] += curboard["comelinebet"]
    curboard["comelinebet"] = 0

  elif button == 'off' and roll in [4, 5, 6, 8, 9, 10]:
    # This doesn't make sense at first, but 'place' bets get paid after the button is hit
    # For example, come out 6, place 8, roll 6 (button == off), roll 8 (place winner)
    totboard["placebet"][roll-1] += curboard["placebet"][roll-1]
    if roll in [4, 10]:
      totboard["placepay"][roll-1] += curboard["placebet"][roll-1] + (curboard["placebet"][roll-1] * (9/5))
    elif roll in [5, 9]:
      totboard["placepay"][roll-1] += curboard["placebet"][roll-1] + (curboard["placebet"][roll-1] * (7/5))
    elif roll in [6, 8]:
      totboard["placepay"][roll-1] += curboard["placebet"][roll-1] + (curboard["placebet"][roll-1] * (7/6))
    # Clear place bet
    curboard["placebet"][roll-1] = 0

  elif button != 'off' and roll == 7:
    # Collect the losing bets
    totboard["passbet"] += curboard["passbet"]
    totboard["passoddsbet"] += curboard["passoddsbet"]
    curboard["passbet"] = 0
    curboard["passoddsbet"] = 0
    for x in range(12):
      totboard["placebet"][x-1] += curboard["placebet"][x-1]
      curboard["placebet"][x-1] = 0
      totboard["comebet"][x-1] += curboard["comebet"][x-1]
      totboard["comeoddsbet"][x-1] += curboard["comeoddsbet"][x-1]
    # Pay the comelinebet
    totboard["comelinebet"] += curboard["comelinebet"]
    totboard["comelinepay"] += curboard["comelinebet"] * 2

  elif button != 'off' and roll == 11:
    # Pay the comeline only
    totboard["comelinebet"] += curboard["comelinebet"]
    totboard["comelinepay"] += curboard["comelinebet"] * 2
    
  elif button != 'off' and roll in [4, 5, 6, 8, 9, 10]:
    # Pay the place/come
    totboard["placebet"][roll-1] += curboard["placebet"][roll-1]
    totboard["comebet"][roll-1] += curboard["comebet"][roll-1]
    totboard["comepay"][roll-1] += curboard["comebet"][roll-1] * 2
    totboard["comeoddsbet"][roll-1] += curboard["comeoddsbet"][roll-1]
    if roll in [4, 10]:
      totboard["placepay"][roll-1] += curboard["placebet"][roll-1] + (curboard["placebet"][roll-1] * (9/5))
      totboard["comeoddspay"][roll-1] += curboard["comeoddsbet"][roll-1] + (curboard["comeoddsbet"][roll-1] * 2)
    elif roll in [5, 9]:
      totboard["placepay"][roll-1] += curboard["placebet"][roll-1] + (curboard["placebet"][roll-1] * (7/5))
      totboard["comeoddspay"][roll-1] += curboard["comeoddsbet"][roll-1] + (curboard["comeoddsbet"][roll-1] * (3/2))
    elif roll in [6, 8]:
      totboard["placepay"][roll-1] += curboard["placebet"][roll-1] + (curboard["placebet"][roll-1] * (7/6))
      totboard["comeoddspay"][roll-1] += curboard["comeoddsbet"][roll-1] + (curboard["comeoddsbet"][roll-1] * (6/5))
    curboard["placebet"][roll-1] = 0
    # Now deal with the come line bet moving.  placebets will have to add odds
    curboard["comebet"][roll-1] = curboard["comelinebet"]
    curboard["comelinebet"] = 0


def shooterstats(shooter, lenroll):

  shooter["numtosses"] += lenroll
  shooter["numrounds"] += 1
  shooter["streakdist"][lenroll] += 1
  if lenroll < shooter["lowstreak"]:
    shooter["lowstreak"] = lenroll
  if lenroll > shooter["highstreak"]:
    shooter["highstreak"] = lenroll


def decidebutton(button, roll):

  if button == 'off':
    if roll in [4, 5, 6, 8, 9, 10]:
      button = roll
  elif button == roll:
    button = 'off'
  elif roll == 7:
    button = 'crap'

  return button


def diceroll(dicedist):
  sum = 0
  for i in range(2):
    sum += randrange(1,7)
  dicedist["n"] += 1
  dicedist["rolls"][sum-1] += 1
  return sum

def printboard(board, button):
  boxnums = [ 4, 5, 6, 8, 9, 10]
  print "-" * 60
  print "PASS\t\t" + str(board["passbet"])
  print "PASSODDS\t" + str(board["passoddsbet"])
  print "COME\t\t" + str(board["comelinebet"])
  print "\t\tPLACE\tCOME\tCOMEODDS"
  for x in boxnums:
    if x == button:
      print ("BUTTON ->" + str(x) + "\t" + 
             str(int(board["placebet"][x-1])) + "\t" + 
             str(int(board["comebet"][x-1])) + "\t" + 
             str(int(board["comeoddsbet"][x-1]))
            )  
    else:
      print ("         " + str(x) + "\t" + 
             str(int(board["placebet"][x-1])) + "\t" +
             str(int(board["comebet"][x-1])) + "\t" + 
             str(int(board["comeoddsbet"][x-1]))
            )


def printtot(board):

  boxnums = [ 4, 5, 6, 8, 9, 10]
  print "\t\tWAGERED\tPAID"
  print "PASS\t\t" + str(board["passbet"]) + "\t" + str(board["passpay"])
  print "PASSODDS\t" + str(board["passoddsbet"]) + "\t" + str(board["passoddspay"])
  print "COME\t\t" + str(board["comelinebet"]) + "\t" + str(board["comelinepay"])
  totbet = int(board["passbet"]) + int(board["passoddsbet"]) + int(board["comelinebet"])
  totpay = int(board["passpay"]) + int(board["passoddspay"]) + int(board["comelinepay"])
  print "\t\tPLACE WAGERED\tPLACE PAID\tCOME WAGERED\tCOME PAID\tODDS WAGERED\tODDS PAID"
  for x in boxnums:
    print ("\t" + str(x) + "\t" + 
           str(int(board["placebet"][x-1])) + "\t\t" + str(int(board["placepay"][x-1])) + "\t\t" +
           str(int(board["comebet"][x-1])) + "\t\t" + str(int(board["comepay"][x-1])) + "\t\t" +
           str(int(board["comeoddsbet"][x-1])) + "\t\t" + str(int(board["comeoddspay"][x-1]))
          )
    totbet += int(board["placebet"][x-1]) + int(board["comebet"][x-1]) + int(board["comeoddsbet"][x-1])
    totpay += int(board["placepay"][x-1]) + int(board["comepay"][x-1]) + int(board["comeoddspay"][x-1])
  print "GRAND TOTAL WAGERED = " + str(totbet)
  print "            PAID    = " + str(totpay)
  print "NET                 = " + str(totpay - totbet)


def plotshooterdist(shooter):

  plt.title = "Streak Distribution"
  plt.xlabel = "Streak Length"
  plt.ylable = "Occurrences"

  a = np.arange(1,76)
  plt.plot(np.arange(1, 76), shooter["streakdist"], 'ro')
  plt.show()


def main(argv):
  try:
    optlist, arglist = getopt.getopt(argv[1:], "n:o:vp", ["numshooters=", "outputfile=", "verbose", "plot"])
  except getopt.GetoptError as err:
    print str(err)
    usage()
    sys.exit(2)
  # Defaults
  verbose = False
  numrounds = 1
  f = open(os.devnull, 'w')
  plotshots = False
  for o, a in optlist:
    if o in ['-v', "--verbose"]:
      verbose = True
    elif o in ["-n", "--numshooters"]:
      if a.isdigit():
        numrounds = int(a)
      else:
        print "Numshooters should be an integer"
        sys.exit(2)
    elif o in ["-o", "--outputfile"]:
      f = open(arglist[0], 'w')
    elif o in ["-p", "--plot"]:
      plotshots = True

  board = {}
  initboard(board)
  totboard = {}
  initboard(totboard)
  oboard = {}
  initboard(oboard)
  dicedist = {'n':0, 'rolls' : [0] * 12}
  shooter = {}
  initshooterstats(shooter)
  button = 'off'
  roll = 0
  for i in range(int(numrounds)):
    shootertoss = 0
    initboard(totboard)
    initboard(board)
    while button != 'crap':
      placebets(board, button, roll)
      if verbose : printboard(board, button) 
      roll = diceroll(dicedist)
      if verbose : print "ROLL = " + str(roll)
      paybets(board, totboard, button, roll)
      button = decidebutton(button, roll)
      shootertoss += 1

    button = 'off'
    shooterstats(shooter, shootertoss)
    addboards(oboard, totboard)
    jsonboard = jsonify(totboard)
    json.dump(jsonboard, f)
    if verbose:
      print "-" * 60
      print "Roll length = " + str(shootertoss)
      printtot(totboard)

  print "-" * 60
  print "Total Shooters = " + str(shooter["numrounds"])
  print "Average Shooter Tosses = " + str(shooter["numtosses"] / shooter["numrounds"])
  printtot(oboard)
  
  if plotshots : plotshooterdist(shooter)
  if verbose : print dicedist
  

def usage():
  print "Usage:  craps.py [ -v ] [ --verbose ] [ -n number ] [ --numshooters number ]"
  print "Options: "
  print "\t-v|--verbose"
  print "\t\tDisplay verbose messaging including the board state at each toss"
  print "\t-n|--numshooters n"
  print "\t\tEnter the number of shooters to simulate Default = 1"
  print "\t-o|--outputfile <file>"
  print "\t\tFile to write shooter detail output"
  print "\t-p|--plot"
  print "\t\tPlot the shooter distribution"


if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))
