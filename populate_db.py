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
    {'image': 'dribbble.png', 'title': 'Dribbble Shots', 'color': '#E94C89'},
    {'image': '', 'title': 'Icons', 'color': '#ffd180'},
    {'image': '', 'title': 'Guidelines', 'color': '#ff5722'},
    {'image': '', 'title': 'Colors', 'color': '#cddc39'},
    {'image': '', 'title': 'Frameworks', 'color': '#9c27b0'}
]

items = {
    'dribbble-shots': [
        {
            'image': 'https://d13yacurqjgara.cloudfront.net/users/30252/screenshots/1790652/google-dribbble_teaser.png',
            'title': 'Google Search - redesign attempt',
            'text': "Designer Aurelien Salomon imagined what Google search would look like if it were redesigned using Google's own Material Design language.\nGone is Google search's iconic sparseness, and in its place is the colorful, beautifully animated UX of Android L, Android Wear, and other Google products.",
            'author': 'Aurelien Salomon',
            'source': 'https://dribbble.com/shots/1790652-Google-Material-exploration'
        }
    ],
    'icons': [
        {
            "author": "Google",
            "image": "http://google.github.io/material-design-icons/www/images/icons-library.png",
            "source": "http://google.github.io/material-design-icons/#getting-icons",
            "text": "Material design system icons are simple, modern, friendly, and sometimes quirky. Each icon is created using our design guidelines to depict in simple and minimal forms the universal concepts used commonly throughout a UI. Ensuring readability and clarity at both large and small sizes, these icons have been optimized for beautiful display on all common platforms and display resolutions.",
            "title": "Material Design Icons"
        }
    ],
    'colors': [
        {
            "author": "materialpalette.com authors",
            "image": "https://lh3.googleusercontent.com/-NwoSm7uxX_U/VeW9zSxVYOI/AAAAAAAAAQA/FEBIEe918s0/w506-h342/FireShot%2BCapture%2B1%2B-%2BMaterial%2BDesign%2BColor%2BPalette_%2B-%2Bhttp___www.materialpalette.com_light-blue_cyan.png",
            "source": "https://www.materialpalette.com",
            "text": "Easy-to-use palette generator. Very well designed user interface creates a slick experience. Colors of your choice will be combined into a small design concept and you can edit your selection by choosing different color options.",
            "title": "Material Design Palette"
        },
        {
            "author": "materialpalette.com authors",
            "image": "http://4.bp.blogspot.com/-OzwXWc9MR8c/Vt53CVgeE-I/AAAAAAAAALs/S65a6Ju4uzg/s1600/material.PNG",
            "source": "https://www.materialpalette.com/colors",
            "text": "All colors for everyday material design in one screen. Just click on the base color stripe to see all possible shades with it's HEX values.",
            "title": "Material Design Colors"
        },
        {
            "author": "Santhosh Sundar",
            "image": "https://lh3.googleusercontent.com/Ai1JEdyP6v0dSWxpS5toRq2YZo4t0u9lGCWJzzagrm69om-N9y6jo-8jvtCiqqvTSOHtlb1N=s1280-h800-e365",
            "source": "https://chrome.google.com/webstore/detail/simple-material-design-pa/onaeadclbaeleijcfmmhopgmmmpedifa",
            "text": "A no-nonsense palette for Google's Material Design Colors that you can access right within the browser without having to leave the tab and even offline. \r\n\r\nAvailable in HEX, RGB and RGBA color models.",
            "title": "Simple Material Design Palette Chrome Extension"
        }
    ],
    "frameworks": [
        {
            "author": "Call-Em-All",
            "image": "http://cdn.tutorialzine.com/wp-content/uploads/2016/02/material_ui.png",
            "source": "http://www.material-ui.com/",
            "text": "Material-UI is a rich set of React components implementing Material Design principles. This is a very polished library featuring pixel-perfect CSS styles and animations. There are also two separate themes for users to choose from \u2013 dark and light.",
            "title": "Material-UI"
        },
        {
            "author": "Polymer authors",
            "image": "http://cdn.tutorialzine.com/wp-content/uploads/2016/02/6_polymer.png",
            "source": "https://www.polymer-project.org",
            "text": "It\u2019s a library for building fast, reusable web components which then you can import in your projects. Polymer offers a big selection of ready-to-use elements, organized in seven categories. One of them is called Paper and is full of Material Design components.",
            "title": "Polymer"
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
