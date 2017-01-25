#!/usr/bin/python
""" Clear 'catalog.db' and populate it with some data.
Run this script without any parameters to add default categories to db.
Use -i (or --items) argument to register a fake user and add some articles. 
"""

import os, sys, getopt

if os.path.isfile('./catalog.db'):
    os.remove('catalog.db')

from db_scheme import Item, Category, User

categories = [
    {'image': 'youtube.png', 'title': 'YouTube Videos', 'color': '#BA2B2A'},
    {'image': 'dribbble.png', 'title': 'Dribbble Arts', 'color': '#E94C89'},
    {'image': '', 'title': 'Icons', 'color': '#ffd180'},
    {'image': '', 'title': 'Guidelines', 'color': '#ff5722'},
    {'image': '', 'title': 'Colors', 'color': '#cddc39'},
    {'image': '', 'title': 'Frameworks', 'color': '#9c27b0'}
]

items = {
    'dribbble-arts': [
        {
            'image': 'https://d13yacurqjgara.cloudfront.net/users/30252/screenshots/1790652/google-dribbble_teaser.png',
            'title': 'Google Search - redesign attempt, part 1',
            'text': "Designer Aurelien Salomon imagined what Google search would look like if it were redesigned using Google's own Material Design language.\nGone is Google search's iconic sparseness, and in its place is the colorful, beautifully animated UX of Android L, Android Wear, and other Google products.",
            'author': 'Aurelien Salomon',
            'source': 'https://dribbble.com/shots/1790652-Google-Material-exploration'
        }
    ],
    'icons': [
        {
            'image':'',
            'title': 'Some icon set',
            'text': 'Incredible icon set, download and enjoy',
            'author': 'John Smith',
            'source': 'https://johnsmith.com/icon-set'
        }
    ]
}

def main(argv, program_name):
    def print_help():
        print program_name + ' [-i]'

    need_items = False

    try:
        opts, args = getopt.getopt(argv,"i",["items"])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--items"):
            need_items = True

    # first add categories
    add_categories()

    # add items only if necessary
    if need_items:
        add_items()

def add_categories():
    Category.add_all(categories)

def add_items():
    email = 'admin@domain.com'
    username = 'Administrator'
    user = User.create(email=email, username=username, picture='')

    for category_path in items:
        category = Category.get_one(category_path)

        for item in items[category_path]:
            Item.add(user, category, Item(**item))

if __name__ == "__main__":
   main(sys.argv[1:], sys.argv[:1][0])
