from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

Category1 = Category(name = "Fridge Stuff")
session.add(Category1)
session.commit()
Item1 = Item(name = "Onions", description = "A bag of nice, red onions", category  = Category1)
session.add(Item1)
Item2 = Item(name = "Carrots", description = "A bunch of goddamn carrots, just sitting there in a bag.", category  = Category1)
session.add(Item2)
Item3 = Item(name = "Sizetrac", description = "You don't want to know what this is.", category  = Category1)
session.add(Item3)
Item4 = Item(name = "Olive oil", description = "For everything.", category  = Category1)
session.add(Item4)
Item5 = Item(name = "Family pack of Wegman's strip steak", description = "Number one protein source", category  = Category1)
session.add(Item5)

session.commit()

Category2 = Category(name = "Laundry Room")
session.add(Category2)
session.commit()
Item1 = Item(name = "Detergent", description = "Used for making my clothes clean.", category  = Category2)
session.add(Item1)
Item2 = Item(name = "Beach ball", description = "What the hell is this doing here, honestly.", category  = Category2)
session.add(Item2)

session.commit()

print("Added categories and items!")


