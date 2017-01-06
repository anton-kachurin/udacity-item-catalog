from flask import Flask, render_template, request, redirect, url_for, flash,\
                  jsonify, session, make_response
import random, string, json, httplib2, requests

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from db_scheme import Category, Item

SECRETS_FILE = 'client_secrets.json'
client_secrets = json.loads(open(SECRETS_FILE, 'r').read())
CLIENT_ID = client_secrets['web']['client_id']
REDIRECT_URI = 'postmessage'

app = Flask(__name__)

def json_result(message, code=401):
    response = make_response(json.dumps(message), code)
    response.headers['Content-Type'] = 'application/json'

    return response

@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    session['state'] = state

    return render_template('login.html',
                            state_str=state, client_id=CLIENT_ID,
                            redirect_uri = REDIRECT_URI)

@app.route('/gconnect', methods=["POST"])
def gconnect():
    if request.args.get('state') != session.get('state'):
        return json_result('Invalid state parameter')

    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets(SECRETS_FILE, scope='')
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

    if result['issued_to'] != CLIENT_ID:
        return json_result("Token's client ID doesn't match given client ID")

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if gplus_id == stored_gplus_id and stored_access_token is not None:
        return json_result('User is already connected', 200)

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

@app.route('/gdisconnect')
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

        return json_result('Successfully disconnected', 200)
    else:
        return json_result('Failed to revoke token for given user', 400)


@app.route('/')
def redirect_to_main():
    return redirect(url_for('show_catalog'))

@app.route('/catalog')
def show_catalog():
    categories = Category.get_all()
    return str(len(categories))

@app.route('/catalog/<string:category_label>')
def show_category(category_label):
    return 'some category selected with name ' + category_label

@app.route('/catalog/<string:category_label>/<string:item_label>')
def show_item(category_label, item_label):
    return 'show some item on the page'

@app.route('/catalog/<string:category_label>/add',
           methods=['GET', 'POST'])
def add_item(category_label):
    return 'item creation page'

@app.route('/catalog/<string:category_label>/<string:item_label>/edit',
           methods=['GET', 'POST'])
def edit_item(category_label, item_label):
    return 'edit some item'

@app.route('/catalog/<string:category_label>/<string:item_label>/delete',
           methods=['GET', 'POST'])
def delete_item(category_label, item_label):
    return 'delete some item'


if __name__ == '__main__':
    app.secret_key = 'j9in938j2-fin9348u-r2jefw'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
