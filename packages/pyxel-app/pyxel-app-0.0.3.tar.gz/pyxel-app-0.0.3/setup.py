from setuptools import setup, find_packages

setup(
    name='pyxel-app',
    version='0.0.3',
    packages=find_packages(),
    package_data={'PyxelApp': ['template/*']},
    install_requires=[
        'Click',
        'pyxel-universal-font',
    ],
    entry_points={
        "console_scripts":[
            "pyxel_app=PyxelApp.pyxel_app:pyxel_app",
        ],
    },    
    author="naoyashi",
    author_email="n.koba0427@gmail.com",
    description="Extension tool to create molds for pyxel applications with a single command",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/n-koba0427/PyxelApp",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: Japanese",
    ],
)

