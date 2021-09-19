from setuptools import setup

setup(
    name="jesse-picker",
    version='0.2',
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        jesse-picker=jessepicker.__init__:cli
    ''',
)
