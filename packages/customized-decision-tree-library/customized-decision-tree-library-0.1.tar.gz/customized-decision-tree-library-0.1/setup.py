from setuptools import setup, find_packages

setup(
    name='customized-decision-tree-library',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
    ],
    author='Kumari Pinki',
    author_email='kumaripinki@iitgn.ac.in',
    description='A customized decision tree library',
    url='https://github.com/PinkiKumari22/customised_decision_tree-0.1.git',
    classifiers=[
        'Programming Language :: Python :: 3.10',
    ],
)
