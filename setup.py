from setuptools import setup

setup(
    name="jesse-picker",
    version='0.1',
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        jesse-picker=jessepicker.__init__:cli
    ''',
)
