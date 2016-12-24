from flask import Flask, render_template, request, redirect, url_for, flash,\
                  jsonify
from db_scheme import Category, Item

app = Flask(__name__)

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

@app.route('/catalog/<string:category_label>/add')
def add_item(category_label):
    return 'item creation page'

@app.route('/catalog/<string:category_label>/<string:item_label>')
def show_item(category_label, item_label):
    return 'show some item on the page'

@app.route('/catalog/<string:category_label>/<string:item_label>/edit')
def edit_item(category_label, item_label):
    return 'edit some item'

@app.route('/catalog/<string:category_label>/<string:item_label>/delete')
def delete_item(category_label, item_label):
    return 'delete some item'


if __name__ == '__main__':
    app.secret_key = 'j9in938j2-fin9348u-r2jefw'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
