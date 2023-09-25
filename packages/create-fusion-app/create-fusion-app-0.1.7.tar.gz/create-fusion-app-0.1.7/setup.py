from setuptools import setup, find_packages

setup(
    name='create-fusion-app',
    version='0.1.7',
    packages=find_packages(),
    package_data={'create_fusion_app': ['modules/*']},
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'fusion = create_fusion_app.main:main',
        ],
    },
    author='Matthew Ford',
    author_email='matthew@symbiotic.love',
    description='Create Fusion App creates a specifically formatted React/Redux app called a Fusion app.',
    license='MIT',
)
