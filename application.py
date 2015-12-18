from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/')
@app.route('/catalog')
def showCatalog():
    categories = session.query(Category).all()
    first_category = None
    if len(categories) > 0:
        first_category = categories[0]
    first_category_items = None
    if first_category:
        first_category_items = session.query(Item).filter_by(category_id = first_category.id)
        return render_template('catalog.html', categories = categories, first_category_items = first_category_items)
    else:
        return render_template('catalog.html', categories = categories)

@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        print("This is a request: {}".format(request))
        print("Request form: {}".format(request.form))
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()

        return redirect(url_for('showCatalog'))
    else:
        return render_template('newCategory.html')

@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    category_to_delete = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(category_to_delete)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteCategory.html', category=category_to_delete)

@app.route('/catalog/<int:category_id>')
def showCategory(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    category_items = session.query(Item).filter_by(category_id = category_id)
    return render_template('category.html', category = category, items = category_items)

@app.route('/catalog/<int:category_id>/new', methods=['GET', 'POST'])
def newItem(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], description=request.form['description'], category_id=category.id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('newItem.html', category=category)


@app.route('/catalog/<int:category_id>/<int:item_id>')
def showItem(category_id, item_id):
    category = session.query(Category).filter_by(id = category_id).one()
    item = session.query(Item).filter_by(id = item_id).one()
    return render_template('item.html', category = category, item = item)

@app.route('/catalog/<int:category_id>/<int:item_id>/edit', methods=['GET','POST'])
def editItem(category_id, item_id):
    category = session.query(Category).filter_by(id = category_id).one()
    editedItem = session.query(Item).filter_by(id = item_id).one()
    if request.method == 'POST':
        editedItem.name = request.form['name']
        editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showCategory', category_id = category_id, item_id = item_id))
    else:
        return render_template('editItem.html', category=category, item=editedItem)



@app.route('/catalog/<int:category_id>/<int:item_id>/delete', methods=['GET','POST'])
def deleteItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id = item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('deleteItem.html', category=category, item=item)

@app.route('/login')
def showLogin():
    pass

@app.route('/disconnect')
def disconnect():
    pass

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
    # setting host to 0.0.0.0 tells app to listen on all public IP addresses