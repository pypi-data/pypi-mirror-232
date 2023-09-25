from setuptools import setup, find_packages

setup(
    name='create-fusion-app',
    version='0.1.12',
    packages=find_packages(),
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'fusion = main:main',
        ],
    },
    author='Matthew Ford',
    author_email='matthew@symbiotic.love',
    description='Create Fusion App creates a specifically formatted React/Redux app called a Fusion app.',
    license='MIT',
)
