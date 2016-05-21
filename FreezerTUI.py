#!/usr/bin/python3

import os
import re
from datetime import *
from StorageHandler import *
import tui

class FreezerTUI():
    def __init__( self, db ):
        self.db = db

    def PrintHelp( self ):
        print( "Kommandos:" )
        print( "" )

    def PrintItems( self ):
        h = tui.GetTerminalHeight()
        items = self.db.GetItems( maxLines=h-3)
        print( "Produkt    |  Größe | Status | haltbar bis" )
        print( "===========================================" )
        for item in items:
            s  = tui.Resize( item[0],            10, True  ) + " | "
            s += tui.Resize( item[1],             6, False ) + " | "
            s += tui.Resize( str(item[2]) + '%',  6, False ) + " | "
            s += tui.Resize( item[3],            10, True  )
            print(s)

    def Str2Date( self, dateStr ):
        try:
            return datetime.strptime( dateStr, "%Y-%m-%d" ).date()
        except:
            return datetime.strptime( dateStr, "%Y%m%d" ).date()

    def Run( self ):
        try:
            self.PrintHelp()
            self.PrintItems()
            consume_mode = True
            while True:
                try:
                    cmd = input("> ")
                    print()
                    if cmd == "fill":
                        consume_mode = False
                        print( "Nachschub-Modus." )
                    elif cmd == "consume":
                        consume_mode = True
                        print( "Konsum-Modus." )
                    elif re.match( "^[0-9]{8,15}$", cmd ):
                        if consume_mode:
                            self.db.Consume( 25, cmd )
                            self.PrintItems()
                        else:
                            bb = input( "Best before (YYYY-MM-DD)? > " )
                            self.db.AddItem( cmd, self.Str2Date(bb) )
                            self.PrintItems()
                    else:
                        print( "Unbekanntes Kommando." )
                except UnknownItem:
                    print( "Item nicht gefunden." )


        except KeyboardInterrupt:
            pass
