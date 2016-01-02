"""
Application that runs catalog application
"""
import json
import random
import string
import os
import uuid

from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, make_response
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import requests

# IMPORTS FOR SAVING IMAGES
from werkzeug import secure_filename
from database_setup import Category, Base, Item, User

app = Flask(__name__)

engine = create_engine(
    ('postgres://mxjecomshjznqn:Ky9M6DXhTdpW3CV2sCFlUJExht@ec2-54-83-204-159.co'
     'mpute-1.amazonaws.com:5432/d6iivi4caaqog9'))
# engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
db_session = sessionmaker(bind=engine)
session = db_session()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

UPLOAD_FOLDER = 'static/img/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_OBJECT_TYPES = set(['category', 'item', 'user'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# JSON API endpoints for catalog data
@app.route('/catalog/JSON')
def catalog_json():
    """JSON endpoint that returns all categories"""
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/catalog/<int:category_id>/JSON')
def category_json(category_id):
    """JSON endpoint returns all items in category"""
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(category_items=[i.serialize for i in items])


@app.route('/catalog/<int:category_id>/<int:item_id>/JSON')
def category_item_json(category_id, item_id):
    """JSON endpoint returns information about a single item"""
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


@app.route('/')
@app.route('/catalog')
def show_catalog():
    """Shows main catalog page"""
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('publicCatalog.html', categories=categories)
    else:
        return render_template('catalog.html', categories=categories)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def new_category():
    """Page to create new categories"""
    if 'username' not in login_session:
        return redirect(url_for('show_login'))

    if request.method == 'POST':
        current_user = session.query(User).filter_by(id=login_session['user_id']).one()

        category_to_add = Category(
            user=current_user,
            name=request.form['name'],
            picture=add_image(request.files['image-file'], 'category')
            )

        session.add(category_to_add)
        flash('New category "%s" successfully created' % category_to_add.name)
        session.commit()

        return redirect(url_for('show_catalog'))
    else:
        return render_template('newCategory.html')


# change category name or image
@app.route('/catalog/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    """Page to edit a category"""
    category_to_edit = session.query(Category).filter_by(id=category_id).one()

    if 'username' not in login_session:
        return redirect(url_for('show_login'))

    if category_to_edit.user_id != login_session['user_id']:
        return '''
        <script>function myFunction() {alert('You are not authorized to delete 
        this category. Please create your own category in order to delete.');}
        </script><body onload='myFunction()''>
        '''
    if request.method == 'POST':
        if request.form['name']:
            category_to_edit.name = request.form['name']

        image_file = request.files['image_file']
        path = add_image(image_file, 'category')
        if path:
            category_to_edit.picture = path

        session.add(category_to_edit)
        session.commit()
        flash('You have edited "{}"'.format(category_to_edit.name))
        return redirect(url_for('show_catalog'))
    else:
        return render_template('editCategory.html', category=category_to_edit)


@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
def delete_category(category_id):
    """Page to delete a category (also deletes all items under it)"""
    category_to_delete = session.query(Category).filter_by(id=category_id).one()
    items_to_delete = session.query(Item).filter_by(category=category_to_delete)
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    if category_to_delete.user_id != login_session['user_id']:
        return '''
        <script>function myFunction() {alert('You are not authorized to delete 
        this category. Please create your own category in order to delete.');}
        </script><body onload='myFunction()''>
        '''
    if request.method == 'POST':
        if category_to_delete.picture:
            delete_image(category_to_delete.picture)
        for item in items_to_delete:
            if item.picture:
                delete_image(item.picture)

        session.delete(category_to_delete)
        session.commit()
        flash('You have deleted "{}"'.format(category_to_delete.name))
        return redirect(url_for('show_catalog'))
    else:
        return render_template('deleteCategory.html',
                               category=category_to_delete)


@app.route('/catalog/<int:category_id>')
def show_category(category_id):
    """Shows the page for a specific category"""
    category = session.query(Category).filter_by(id=category_id).one()
    category_items = session.query(Item).filter_by(category_id=category_id)
    return render_template('category.html',
                           category=category,
                           items=category_items)


@app.route('/catalog/<int:category_id>/new', methods=['GET', 'POST'])
def new_item(category_id):
    """Shows page for creating a new item"""
    # if no one is logged in, let the user log in
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    category = session.query(Category).filter_by(id=category_id).one()

    # if the category's owner is not the person currently logged in, deny
    # request to create new item
    if category.user_id != login_session['user_id']:
        return '''
            <script>function myFunction() {alert('You are not authorized
            to edit this category. Please create your own category in order to
            edit.');}</script><body onload='myFunction()''>
        '''

    if request.method == 'POST':

        item_to_add = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=category.id,
            picture=add_image(request.files['image-file'], 'item')
            )

        session.add(item_to_add)
        session.commit()
        flash('You have added "{}"'
              ' to "{}"'.format(item_to_add.name, category.name))
        return redirect(url_for('show_category', category_id=category_id))
    else:
        return render_template('newItem.html', category=category)


@app.route('/catalog/<int:category_id>/<int:item_id>')
def show_item(category_id, item_id):
    """Shows page for a specific item"""
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html', category=category, item=item)


@app.route('/catalog/<int:category_id>/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(category_id, item_id):
    """Shows page for editing an item"""
    if 'username' not in login_session:
        return redirect(url_for('show_login'))

    category = session.query(Category).filter_by(id=category_id).one()
    edited_item = session.query(Item).filter_by(id=item_id).one()

    if category.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to edit this item. Please create your own category in order to"
                " edit.');}</script><body onload='myFunction()''>")

    if request.method == 'POST':
        edited_item.name = request.form['name']

        image_file = request.files['image_file']
        edited_item.picture = add_image(image_file, 'item')

        edited_item.description = request.form['description']

        session.add(edited_item)
        session.commit()

        flash('You have edited "{}"'
              ' to "{}"'.format(edited_item.name, category.name))

        return redirect(url_for('show_category',
                                category_id=category_id,
                                item_id=item_id))
    else:
        return render_template('editItem.html',
                               category=category,
                               item=edited_item)


@app.route('/catalog/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def delete_item(category_id, item_id):
    """Page to delete an item"""
    if 'username' not in login_session:
        return redirect(url_for('show_login'))

    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()

    if category.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to edit this item. Please create your own category in order to"
                " edit.');}</script><body onload='myFunction()''>")

    if request.method == 'POST':
        if item.picture:
            delete_image(item.picture)
        session.delete(item)
        session.commit()
        flash('You have deleted "{}"'
              ' from "{}"'.format(item.name, category.name))

        return redirect(url_for('show_category', category_id=category_id))
    else:
        return render_template('deleteItem.html', category=category, item=item)


def add_image(image_file, object_type):
    """Adds an image to the file system of the appropriate type"""
    if (image_file and
            is_allowed_filename(image_file.filename) and
            is_valid_type(object_type)):
        extension = extract_file_extension(image_file.filename)

        # generate unique filename
        filename = "{}.{}".format(str(uuid.uuid4()), extension)
        filename = secure_filename(filename)

        path = os.path.join(app.config['UPLOAD_FOLDER'], object_type, filename)
        image_file.save(path)
        # add '/' to make filepath absolute
        return '/' + path
    else:
        return None


def delete_image(filepath):
    """Removes an image from the filesystem"""
    # remove first '/' to make filepath relative
    os.remove(filepath[1:])


def is_valid_type(object_type):
    """Tests if the specified object_type is valid"""
    return object_type in ALLOWED_OBJECT_TYPES


def extract_file_extension(filename):
    """Returns the extension of the file's filename"""
    extension = filename.split('.')[1]
    return extension


def is_allowed_filename(filename):
    """Tests if the uploaded file's filename is legitimate"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_user(login_session):
    """Adds a new user to the database"""
    new_user = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    """Returns the user's info"""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    """Returns the user's id, otherwise returns None"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/login')
def show_login():
    """Shows the login page"""
    state = (''.join(random.choice(string.ascii_uppercase  + string.digits)
                     for x in xrange(32)))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connects user using a Google account"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    http = httplib2.Http()
    result = json.loads(http.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id


    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'


    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = []

    output.append('<h1>Welcome, ')
    output.append(login_session['username'])
    output.append('!</h1>')
    output.append('<img src="')
    output.append(login_session['picture'])
    output.append(('" style="width:300px;height:300px;border-radius:150px;'
                   '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'))
    flash("You are now logged in")
    return ('').join(output)


@app.route('/gdisconnect')
def gdisconnect():
    """Disconnects user if using a Google account"""
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    http = httplib2.Http()
    result = http.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Connects to a Facebook account"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type=fb_exchang'
           'e_token&client_'
           'id={0}&client_secret={1}&fb_exchange_token={2}').format(
               app_id, app_secret, access_token)

    http = httplib2.Http()
    result = http.request(url, 'GET')[1]

    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout,
    # let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = []

    output.append('<h1>Welcome, ')
    output.append(login_session['username'])
    output.append('!</h1>')
    output.append('<img src="')
    output.append(login_session['picture'])
    output.append(('" style="width:300px;height:300px;border-radius:150px;'
                   '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'))
    flash("You are now logged in")
    print "done!"
    return ('').join(output)


@app.route('/fbdisconnect')
def fbdisconnect():
    """Disconnects user if logged in using Facebook"""
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    http = httplib2.Http()
    result = http.request(url, 'DELETE')[1]
    return result


@app.route('/disconnect')
def disconnect():
    """Disconnects the user from the application"""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('show_catalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('show_catalog'))

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    # setting host to 0.0.0.0 tells app to listen on all public IP addresses
