from setuptools import setup, find_packages

setup(
    name="simple-scheduler",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@university.ac.uk",
    description="A minimal Tkinter-based worker scheduling widget",
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        # e.g. "tkcalendar>=1.6.1" if you ever need it
    ],
    entry_points={
        'console_scripts': [
            'simple-scheduler = main:main',  # if you wrap main.py in a main() function
        ],
    },
)
