import setuptools

setuptools.setup(
    name='dataflow_xent',
    description='Package to be used inside cross entropy beam pipeline',
    version='0.0.2',
    install_requires=['apache-beam[gcp]==2.50.0', 'pandas', 'EntropyHub==0.2', 'db-dtypes', 'scikit-learn'],
    packages=setuptools.find_packages(include=['dataflow_xent']),
    python_requires=">=3.7, <4"
 )