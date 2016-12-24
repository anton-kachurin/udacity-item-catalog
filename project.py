from flask import Flask, render_template, request, redirect, url_for, flash,\
                  jsonify

app = Flask(__name__)

@app.route('/')
def redirect_to_main():
    return redirect(url_for('show_catalog'))

@app.route('/catalog')
def show_catalog():
    return 'catalog page with a list of categories'



if __name__ == '__main__':
    app.secret_key = 'j9in938j2-fin9348u-r2jefw'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
