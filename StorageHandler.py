#!/usr/bin/python3

import sqlite3
from datetime import date, timedelta

class UnknownProduct( Exception ):
    def __init__( self, *args, **kwargs ):
        Exception.__init__( self, *args, **kwargs )

class UnknownItem( Exception ):
    def __init__( self, *args, **kwargs ):
        Exception.__init__( self, *args, **kwargs )

class ItemUnderflow( Exception ):
    def __init__( self, *args, **kwargs ):
        Exception.__init__( self, *args, **kwargs )

class StorageHandler():
    """Handles the SQLite database. Use it in a 'with' statement."""
    
    def __init__( self, database ):
        """'database' is the filepath where the database should be."""
        self.dbPath = database
        self.db = None

    def __enter__( self ):
        self.db = sqlite3.connect( self.dbPath )
        return self

    def __exit__( self, excType, excValue, traceback ):
        self.db.commit()
        self.db.close()

    def CreateDB( self ):
        """Creates the needed database structure. Call this only at first start."""
        c = self.db.cursor()

        c.execute( '''CREATE TABLE products (
                        "gtin" INTEGER NOT NULL,
                        "name" TEXT NOT NULL,
                        "size" TEXT,
                        "validDaysAfterOpening" INTEGER);''' )
        c.execute( "INSERT INTO products ( 'gtin', 'name', 'size', 'validDaysAfterOpening' ) VALUES ( '4029764001807', 'Club Mate', '0,5 L', 5 );" )

        c.execute( '''CREATE TABLE "items" (
                        "id"             INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        "gtin"           INTEGER NOT NULL,
                        "origBestBefore" TEXT,
                        "bestBefore"     TEXT,
                        "fillStatus"     INTEGER NOT NULL
                        );''' )
        c.execute( "INSERT INTO items ( 'gtin', 'origBestBefore', 'bestBefore', 'fillStatus' ) VALUES ( '4029764001807', '2016-06-16', '2016-06-16', 100 );" )
        c.execute( "INSERT INTO items ( 'gtin', 'origBestBefore', 'bestBefore', 'fillStatus' ) VALUES ( '4029764001807', '2016-06-23', '2016-06-23', 100 );" )
        self.db.commit()

    def AddProduct( self, gtin, name, size, validDaysAfterOpening ):
        """Add a new product.
        'gtin' is the article number, see https://en.wikipedia.org/wiki/Global_Trade_Item_Number.
        'name' is the name of the product.
        'size' is the packaging size, e.g. '1 l'.
        'validDaysAfterOpening' is the number of days that the product is eatable after you first opened the packaging."""
        c = self.db.cursor()
        c.execute( "INSERT INTO products ( 'gtin', 'name', 'size', 'validDaysAfterOpening' ) VALUES ( ?, ?, ?, ? );", ( gtin, name, size, validDaysAfterOpening ) )
        self.db.commit()

    def AddItem( self, gtin, bestBefore ):
        """Add an item.
        'gtin' is the article number. If the producte is unknown, UnknownProduct will be raised.
        'bestBefore' is the best before date."""
        if not type( bestBefore ) is date:
            raise ValueError
        c = self.db.cursor()
        c.execute( "SELECT COUNT(*) FROM products WHERE gtin=?", (gtin,) )
        if c.fetchone()[0] == 1: # product exists
            bb_str = bestBefore.strftime( "%Y-%m-%d" )
            c.execute( "INSERT INTO items ( 'gtin', 'origBestBefore', 'bestBefore', 'fillStatus' ) VALUES ( ?, ?, ?, 100 );", ( gtin, bestBefore, bb_str ) )
            self.db.commit()
        else:
            raise UnknownProduct

    def Consume( self, percent, gtin ):
        """Lower the fill status of an item. If there is an open item with this GTIN,
        this item will be consumed. If no item is open, the one with the lowest bestBefore
        date will be opened.
        'percent' must be between 1 and 100 and says how much of the product was consumed.
        If percent is higher than the fillStatus of the item, ItemUnderflow will be raised.
        'gtin' is the article number. If no item with this number is available, UnknownItem will be raised."""
        if percent < 1 or percent > 100:
            raise ValueError
        c = self.db.cursor()
        item_id = None
        item_status = None
        c.execute( "SELECT i.id, i.gtin, i.bestBefore, i.fillStatus, p.validDaysAfterOpening FROM items i, products p WHERE i.gtin=p.gtin AND i.gtin=? AND i.fillStatus>0 ORDER BY i.fillStatus ASC, i.bestBefore ASC LIMIT 1", (gtin,) )
        fetched = c.fetchall()
        if len(fetched) == 1:
            item_id = fetched[0][0]
            item_status = fetched[0][3]
        else:
            raise UnknownItem

        if item_status < percent:
            raise ItemUnderflow

        new_state = item_status - percent
        if item_status == 100:
            new_best_before = date.today() + timedelta( days=fetched[0][4] )
            c.execute( "UPDATE items SET fillStatus=?, bestBefore=? WHERE id=?;", ( new_state, new_best_before, item_id ) )
        else:
            c.execute( "UPDATE items SET fillStatus=? WHERE id=?;", ( new_state, item_id ) )
        self.db.commit()

    def GetItems( self, order='', ascending=True, maxLines=0 ):
        """Returns a list of tuples, representing the current item list."""
        s = "SELECT i.gtin, p.name, p.size, i.fillStatus, i.bestBefore FROM items i, products p WHERE i.gtin=p.gtin AND i.fillStatus>0 ORDER BY "

        asc = "DESC"
        if asc:
            asc = "ASC"

        if order == "name":
            s += "p.name " + asc + ", i.bestBefore ASC"
        elif order == "fillStatus":
            s += "i.fillStatus " + asc + ", i.bestBefore ASC"
        elif order == "bestBefore":
            s += "i.bestBefore " + asc
        elif order == "":
            s += "i.bestBefore ASC"
        else:
            raise ValueError
        
        if maxLines > 0:
            s += " LIMIT " + str(int(maxLines))
        s += ";"

        c = self.db.cursor()
        c.execute( s )
        ret = []
        fetched = c.fetchall()
        for row in fetched:
            t = ( row[1], row[2], row[3], row[4] )
            ret.append( t )
        return ret

if __name__ == "__main__":
    with StorageHandler( "./test.db" ) as db:
        db.CreateDB()
        db.GetItems( "fillStatus" )
