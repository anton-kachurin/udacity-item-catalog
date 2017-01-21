from db_scheme import Category

categories = [
    {
        'image': 'youtube.png',
        'title': 'YouTube Videos',
        'color': '#BA2B2A',
    },
    {
        'image': 'dribbble.png',
        'title': 'Dribbble Arts',
        'color': '#E94C89',
    },
    {
        'image': '',
        'title': 'Icons',
        'color': '#ffd180',
    },
    {
        'image': '',
        'title': 'Guidelines',
        'color': '#ff5722',
    },
    {
        'image': '',
        'title': 'Colors',
        'color': '#cddc39',
    },
    {
        'image': '',
        'title': 'Frameworks',
        'color': '#9c27b0',
    },
]

Category.add_all(categories)
