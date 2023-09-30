from setuptools import setup

setup(
    name='StdTool',
    version='0.1.5',
    packages=['StdTool', 'StdTool.iolib', 'StdTool.runlib', 'StdTool.syslib'],
    url='',
    license='Apache License 2.0',
    author='MosRat',
    author_email='whl2075928012@gmail.com',
    description='Some tools for daily use',
    install_requires=['tqdm']
)
