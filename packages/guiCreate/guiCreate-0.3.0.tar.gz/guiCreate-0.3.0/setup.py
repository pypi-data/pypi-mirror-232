from setuptools import setup, find_packages


setup(
    name="guiCreate",
    version='0.3.0',
    author="Folumo (Ominox_)",
    author_email="<ominox_@folumo.com>",
    description='Making gui apps/games',
    long_description_content_type="text/markdown",
    long_description='Easy way to create gui. (first import ScreenManager and use .Mainloop function)',
    packages=find_packages(),
    install_requires=['pygame'],
    keywords=['python', 'gui', 'app', 'game'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
