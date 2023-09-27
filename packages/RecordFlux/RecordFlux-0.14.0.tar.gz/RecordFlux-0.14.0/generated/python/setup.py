


from setuptools import setup, find_packages


setup(
    name='Librflxlang',
    version='0.13.1.dev35+gca7f2ee9a',
    packages=['librflxlang'],
    package_data={
        'librflxlang':
            ['*.{}'.format(ext) for ext in ('dll', 'so', 'so.*', 'dylib')]
            + ["py.typed"],
    },
    zip_safe=False,
)
