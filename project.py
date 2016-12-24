from flask import Flask, render_template, request, redirect, url_for, flash,\
                  jsonify

app = Flask(__name__)

@app.route('/')
def redirect_to_main():
    return redirect(url_for('show_catalog'))

@app.route('/catalog')
def show_catalog():
    return 'catalog page with a list of categories'

@app.route('/catalog/<string:category_name>')
def show_category(category_name):
    return 'some category selected with name ' + category_name

@app.route('/catalog/<string:category_name>/add')
def add_item(category_name):
    return 'item creation page'

@app.route('/catalog/<string:category_name>/<string:item_name>')
def show_item(category_name, item_name):
    return 'show some item on the page'

@app.route('/catalog/<string:category_name>/<string:item_name>/edit')
def edit_item(category_name, item_name):
    return 'edit some item'

@app.route('/catalog/<string:category_name>/<string:item_name>/delete')
def delete_item(category_name, item_name):
    return 'delete some item'


if __name__ == '__main__':
    app.secret_key = 'j9in938j2-fin9348u-r2jefw'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
