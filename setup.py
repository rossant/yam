from setuptools import setup

setup(
    name='yam',
    version='0.1.dev0',
    py_modules=['yam'],
    entry_points={
        'console_scripts': [
            'yam=yam:main',
        ],
    }
)
