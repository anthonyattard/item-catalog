from models import Base, User, Category, Item
from flask import Flask, jsonify, request, url_for, abort, g
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import desc

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


@auth.verify_password
def verify_password(username_or_token, password):
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(username = username_or_token)
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/token')
# @auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        print "missing arguments"
        abort(400) 
        
    if session.query(User).filter_by(username = username).first() is not None:
        print "existing user"
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'message':'user already exists'}), 200
        
    user = User(username = username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({ 'username': user.username }), 201


@app.route('/')
def showAllCategoriesLatestItems():
    # return "This will show all categories with the latest items"
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(9)
    html = ""
    html += "<h1>Categories</h1>"
    for category in categories:
        html += category.name + "<br>"

    html += "<h1>Latest Items</h1>"
    for item in items:
        html += item.name + "<br>"


    return html
    # return categories[0].name
    # if 'username' not in login_session:
    #     return render_template('publicrestaurants.html', restaurants=restaurants, session=login_session)
    # else:
    #     return render_template('restaurants.html', restaurants=restaurants, session=login_session)


@app.route('/catalog/<string:category_name>/items')
def showCategory(category_name):
    print category_name
    # return "This will show all items in a category"
    category = session.query(Category).filter_by(name=category_name).one()

    items = session.query(Item).filter_by(category=category).all()
    
    html = ""
    html += "<h1>Items</h1>"
    for item in items:
        html += item.name + "<br>"

    return html


@app.route('/catalog/<category_name>/<int:item_id>')
# @auth.login_required
def showItem(category_name, item_id):
    # return "This will show an item"
    item = session.query(Item).filter_by(id=item_id).one()

    html = ""
    html += item.name + "<br>"
    html += item.description

    return html



    

@app.route('/catalog/new', methods = ['GET', 'POST'])
# @auth.login_required
def newItem():
    if request.method == 'GET':
        return "This will render a form to add a new item"
    if request.method == 'POST':
        return "This will add a new item to the database"


@app.route('/catalog/<item_name>/edit', methods = ['GET', 'POST'])
# @auth.login_required
def editItem(item_name):
    if request.method == 'GET':
        return "This will render a form to edit an item"
    if request.method == 'POST':
        return "This will commit the item edit to the database"


@app.route('/catalog/<item_name>/delete', methods = ['GET', 'POST'])
# @auth.login_required
def deleteItem(item_name):
    if request.method == 'GET':
        return "This will render a form to delete an item"
    if request.method == 'POST':
        return "This will delete an item from the database"


@app.route('/catalog.json')
def catalogJSON():
    return "This will return the catalog in JSON format"


@app.route('/catalog/<category>.json')
def categoryJSON(category):
    return "This will return a specific category and its items in JSON format"


@app.route('/catalog/<category>/<item_name>.json')
def itemJSON(category, item_name):
    return "This will return an item in JSON format"


if __name__ == '__main__':
    app.debug = True
    #app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='0.0.0.0', port=5000)
    