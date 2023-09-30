from setuptools import setup, find_packages, Extension

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

with open("README.md", "r",encoding="utf-8") as fh:
    README_description = fh.read()

with open("CHANGELOG.md", "r",encoding="utf-8") as fh:
    CHANGELOG_description = fh.read()

with open("USAGE.md", "r",encoding="utf-8") as fh:
    USAGE_description = fh.read()

setup(
    name='convertpngs',
    version='0.0.4',
    description='a module about converting pngs to gif or video in simplified ways.',
    long_description=README_description + '\n\n' + USAGE_description + '\n\n' + CHANGELOG_description,
    long_description_content_type='text/markdown',
    url='',
    author='CYC',
    author_email='vichouro@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords= ['convertpngs','png','gif','video','mp4','opencv','pillow','animation','convert','pngs','png2gif','png2video','png2mp4','png2avi','png2mp4','png2video'],
    packages=find_packages(),
    install_requires=['opencv-python','Pillow'],
)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

