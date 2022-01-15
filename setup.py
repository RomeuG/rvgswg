import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='rvgswg',
    version='0.1.0',
    description='My personal static website generator.',
    long_description=long_description,
    scripts=['rvgswg.py'],
    author='Romeu Gomes',
    author_email='romeu.bizz@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[
        'joblib>=1.1.0',
    ],
    classifiers=[],
)
