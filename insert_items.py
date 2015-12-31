from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User
from application import addItemImage, addCategoryImage, addUserImage

engine = create_engine('postgres://mxjecomshjznqn:Ky9M6DXhTdpW3CV2sCFlUJExht@ec2-54-83-204-159.compute-1.amazonaws.com:5432/d6iivi4caaqog9')
#engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)

session = DBSession()

session.query(Item).delete()
session.query(Category).delete()
session.commit()

User1 = User(name="Alan Gou", email="goutechnology@gmail.com")
session.add(User1)
session.commit()

Category1 = Category(name = "Fridge Stuff", user = User1)
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

Category2 = Category(name = "Laundry Room", user = User1)
session.add(Category2)
session.commit()
Item1 = Item(name = "Detergent", description = "Used for making my clothes clean.", category  = Category2)
session.add(Item1)
Item2 = Item(name = "Beach ball", description = "What the hell is this doing here, honestly.", category  = Category2)
session.add(Item2)

session.commit()

Category3 = Category(name = "Closet", user = User1)
session.add(Category3)
session.commit()
Item1 = Item(name = "Flannel button-down", description = "A nice button-down from J.Crew", category  = Category3)
session.add(Item1)
Item2 = Item(name = "Undefinable socks", description = "What the hell are these.", category  = Category3)
session.add(Item2)
Item3 = Item(name = "Long-forgotten sweater", description = "Were you even alive when this was made?", category  = Category3)
session.add(Item3)

session.commit()

Category4 = Category(name = "Bathroom", user = User1)
session.add(Category4)
session.commit()
Item1 = Item(name = "Soap", description = "Of course.", category  = Category4)
session.add(Item1)
Item2 = Item(name = "Empty shampoo bottle", description = "This is a little depressing.", category  = Category4)
session.add(Item2)
Item3 = Item(name = "Giant scrubber", description = "Definitely a useful piece of equipment", category  = Category4)
session.add(Item3)
Item4 = Item(name = "Book from 3 weeks ago", description = "So this is where you left it!", category  = Category4)
session.add(Item4)

session.commit()

print("Added categories and items!")


