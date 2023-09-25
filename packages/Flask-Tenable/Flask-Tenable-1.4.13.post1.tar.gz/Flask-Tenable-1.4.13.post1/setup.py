from setuptools import setup


def long_description() -> str:
    with open('README.md', mode='r') as f:
        return f.read()


setup(
    name='Flask-Tenable',
    version='1.4.13.post1',
    packages=['flask_tenable'],
    url='https://github.com/felix-zenk/flask-tenable',
    license='MIT',
    author='Felix Zenk',
    author_email='felix.zenk@web.de',
    description=(
        'Flask-Tenable is a thin wrapper for pyTenable '
        'that enables the easy integration of pyTenable into flask applications.'
    ),
    long_description=long_description(),
    long_description_content_type='text/markdown',
    project_urls={
        'Source': 'https://github.com/felix-zenk/flask-tenable',
        'Documentation': f"https://pytenable.readthedocs.io/en/stable/",
    },
    python_requires='>=3.6, <4',
)
