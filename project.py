from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify, session, make_response, g

import os, random, string, json, httplib2, requests

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from db_scheme import Category, Item, User
from db_scheme import NotAuthorized, NotAuthenticated, NotFound

# constants for Google Plus oAuth2
G_SECRETS_FILE = 'g_client_secrets.json'
g_client_secrets = json.loads(open(G_SECRETS_FILE, 'r').read())
G_CLIENT_ID = g_client_secrets['web']['client_id']
REDIRECT_URI = 'postmessage'

# constansts for Facebook aAuth2
FB_SECRETS_FILE = 'fb_client_secrets.json'
fb_client_secrets = json.loads(open(FB_SECRETS_FILE, 'r').read())
FB_CLIENT_ID = fb_client_secrets['web']['app_id']

app = Flask(__name__)

def json_result(message, code=401):
    """ Generate JSON response with given message and HTTP code """
    response = make_response(json.dumps(message), code)
    response.headers['Content-Type'] = 'application/json'

    return response

def json_not_found():
    return json_result('no results found', 404)

def field_list():
    """ List of required fields of an article """
    return [
        {'name': 'title', 'label': 'Title'},
        {'name': 'author', 'label': 'Author'},
        {'name': 'source', 'label': 'Source URL'},
        {'name': 'image', 'label': 'Illustration URL'},
        {'name': 'text', 'label': 'Content', 'textarea': 1}
    ]

def extend_fields_with_value(fields, title, author, source, image, text):
    for field in fields:
        if field['name'] == 'title':
            field['value'] = title
        if field['name'] == 'author':
            field['value'] = author
        if field['name'] == 'source':
            field['value'] = source
        if field['name'] == 'image':
            field['value'] = image
        if field['name'] == 'text':
            field['value'] = text

def is_url(url):
    """ Check if given string is a valid URL """
    url = url.lower()
    return url.startswith('http://') or url.startswith('https://')

def check_request_fields(fields):
    """ Get parameters from `request` object and check it's validity;
    return error message if it's invalid;
    otherwise, extend `fields` object with parameter values and return `None`.
    """
    title = request.form.get('title')
    author = request.form.get('author')
    source = request.form.get('source')
    image = request.form.get('image')
    text = request.form.get('text')

    extend_fields_with_value(fields=fields, title=title, author=author,
                             source=source, image=image, text=text)

    error = ''

    if not title or not author or not text or not source or not image:
        error = 'All fields are required'
    if not is_url(image):
        error = 'Please provide a valid image URL'
    if not is_url(source):
        error = 'Please provide a valid link to the original article'

    if error:
        return error
    else:
        return None

@app.before_request
def before_request():
    """ Set g.current_user property before any view function will run """
    if 'email' in session:
        # user is logged in, use its email to get user from db
        # User.create will make sure not to create duplicate entry in db
        g.current_user = User.create(username=session.get('username'),
                                     email=session.get('email'),
                                     picture=session.get('picture'))
    else:
        g.current_user = None

@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    session['state'] = state

    return render_template('login.html',
                            state_str=state,
                            g_client_id=G_CLIENT_ID,
                            fb_client_id=FB_CLIENT_ID,
                            redirect_uri = REDIRECT_URI)

@app.route('/gconnect', methods=["POST"])
def gconnect():
    if request.args.get('state') != session.get('state'):
        return json_result('Invalid state parameter')

    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets(G_SECRETS_FILE, scope='')
        oauth_flow.redirect_uri = REDIRECT_URI
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return json_result('Failed to upgrade the authorization code')

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    access_token_error = result.get('error')
    if access_token_error is not None:
        return json_result(access_token_error, 500)

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return json_result("Token's user ID doesn't match given user ID")

    if result['issued_to'] != G_CLIENT_ID:
        return json_result("Token's client ID doesn't match given client ID")

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if gplus_id == stored_gplus_id and stored_access_token is not None:
        session['access_token'] = access_token
        return json_result('User is already connected', 200)

    session['provider'] = 'google'
    session['access_token'] = access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    return 'welcome, ' + session.get('username')

def gdisconnect():
    # only disconnect a connected user
    access_token = session.get('access_token')
    if access_token is None:
        return json_result('Current user is not connected')

    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           %  access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if(result['status'] == '200'):
        del session['username']
        del session['picture']
        del session['email']
        del session['access_token']
        del session['gplus_id']
        del session['provider']

        return json_result('Successfully disconnected', 200)
    else:
        return json_result('Failed to revoke token for given user', 400)

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != session.get('state'):
        return json_result('Invalid state parameter')

    access_token = request.data

    app_secret = fb_client_secrets['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        FB_CLIENT_ID, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)

    session['provider'] = 'facebook'
    session['username'] = data['name']
    session['email'] = data['email']
    session['fb_id'] = data['id']

    # Strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    session['picture'] = data["data"]["url"]

    return 'welcome, ' + session.get('username')

def fbdisconnect():
    # Only disconnect a connected user.
    fb_id = session.get('fb_id')
    access_token = session.get('access_token')

    if fb_id is None:
        return json_result('Current user is not connected')

    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (fb_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    data = json.loads(result)

    if 'success' in data and data['success'] == True:
        del session['username']
        del session['picture']
        del session['email']
        del session['access_token']
        del session['fb_id']
        del session['provider']

        return json_result('Successfully disconnected', 200)
    else:
        return json_result('Failed to revoke token for given user', 400)

@app.route('/force_logout', methods=["POST"])
def force_logout():
    """ Make server to clean session data for current user when
    regular disconnect fails. This will allow to get new oAuth credentials
    later, i.e to relogin
    """
    del session['username']
    del session['picture']
    del session['email']
    del session['access_token']
    del session['provider']
    if 'fb_id' in session:
        del session['fb_id']
    if 'gplus_id' in session:
        del session['gplus_id']

    return json_result('Forced to disconnect', 200)

@app.route('/logout', methods=["POST"])
def disconnect():
    """ Recognize what authorization option is currently being used,
    and try to revoke authorization via corresponding provider
    """
    if 'provider' in session:
        provider = session.get('provider')

        if provider == 'facebook':
            return fbdisconnect()

        elif provider == 'google':
            return gdisconnect()

        else:
            return json_result('Internal error', 500)

    else:
        return json_result('Current user is not connected')

@app.route('/')
def redirect_to_main():
    return redirect(url_for('show_catalog'))

@app.route('/catalog')
def show_catalog():
    categories = Category.get_all()

    return render_template('catalog.html', categories=categories)

@app.route('/catalog/<string:category_path>')
def show_category(category_path):
    category = Category.get_one(category_path)
    items = Item.get_all(category)

    return render_template('items.html', category=category, items=items)

@app.route('/catalog/<string:category_path>/<string:item_label>')
def show_article(category_path, item_label):
    category = Category.get_one(category_path)
    item = Item.get_one(category, item_label)

    return render_template('article.html', category=category, item=item)

@app.route('/catalog/<string:category_path>/add',
           methods=['GET', 'POST'])
def add_item(category_path):
    category = Category.get_one(category_path)
    fields = field_list()

    if request.method == 'GET':
        return render_template('add.html', fields=fields, category=category)
    else:
        error = check_request_fields(fields)

        if error:
            return render_template('add.html', fields=fields,
                                               category=category,
                                               error=error)
        else:
            obj = {}
            for field in fields:
                obj[field['name']] = field['value']

            error = Item.add(g.current_user, category, Item(**obj))

            if error:
                return render_template('add.html', fields=fields,
                                                   category=category,
                                                   error=error)
            else:
                return redirect(url_for('show_category',
                                        category_path=category.path))

@app.route('/catalog/<string:category_path>/<string:item_label>/edit',
           methods=['GET', 'POST'])
def edit_item(category_path, item_label):
    category = Category.get_one(category_path)
    item = Item.get_one(category, item_label)
    fields = field_list()

    if request.method == 'GET':
        title = item.title
        author = item.author
        source = item.source
        image = item.image
        text = item.text

        extend_fields_with_value(fields=fields, title=title, author=author,
                                 source=source, image=image, text=text)

        return render_template('add.html', fields=fields, category=category)
    else:
        error = check_request_fields(fields)

        if error:
            return render_template('add.html', fields=fields,
                                               category=category,
                                               error=error)
        else:
            obj = {}
            for field in fields:
                obj[field['name']] = field['value']

            error = item.edit(g.current_user, obj)

            if error:
                return render_template('add.html', fields=fields,
                                                   category=category,
                                                   error=error)
            else:
                return redirect(url_for('show_category',
                                        category_path=category.path))

@app.route('/catalog/<string:category_path>/<string:item_label>/delete',
           methods=['POST'])
def delete_item(category_path, item_label):
    category = Category.get_one(category_path)
    item = Item.get_one(category, item_label)
    item.delete(g.current_user)

    return json_result('deleted successfully', 200)

# JSON endpoints
@app.route('/JSON/catalog')
def all_categories_JSON():
    categories = Category.get_all()

    return jsonify(categoryList=[category.serialized
                                for category in categories])

@app.route('/JSON/catalog/<string:category_path>')
def items_of_category_JSON(category_path):
    try:
        category = Category.get_one(category_path)
        items = Item.get_all(category)

        return jsonify(itemList=[item.serialized for item in items])
    except NotFound:
        return json_not_found()

@app.route('/JSON/catalog/<string:category_path>/<string:item_label>')
def item_JSON(category_path, item_label):
    try:
        category = Category.get_one(category_path)
        item = Item.get_one(category, item_label)

        return jsonify(item.serialized)
    except NotFound:
        return json_not_found()

@app.errorhandler(NotFound)
def not_found(e):
    error = "404. Nothing is found for this URL"
    return render_template('403-404.html', error=error), 404

@app.errorhandler(NotAuthorized)
def not_found(e):
    error = "403. You can't perform this action"
    return render_template('403-404.html', error=error), 403

@app.errorhandler(NotAuthenticated)
def not_found(e):
    return render_template('401.html'), 401

APP_CONFIG_FILE = 'config' #.py

if os.path.isfile(APP_CONFIG_FILE + '.py'):
    app.config.from_object(APP_CONFIG_FILE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
