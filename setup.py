from setuptools import setup, find_packages
args = dict(
    name = 'tcg-web-editor',
    version = '0.1',
    zip_safe = False,
    packages = find_packages(),
    install_requires=[
        'TCGdex',
        'pokedex',
        'pyramid',
        'pyramid_debugtoolbar',
        'waitress',
        'markupsafe',
        'mako',
    ],

    entry_points="""\
      [paste.app_factory]
      main = tcg_web_editor.main:make_app
      """,
)

if __name__ == '__main__':
    setup(**args)
