import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

with open('requirements.txt') as f:
     requirements = f.readlines()

setuptools.setup(
    name="stratus-api-core",  # Replace with your own username
    version="0.0.28",
    author="adara",
    author_email="dot@adara.com",
    description="An API stratus_api for simplified development",
    long_description="",
    long_description_content_type="text/markdown",
    include_package_data=True,
    setup_requires=['pytest-runner'],
    url="https://bitbucket.org/adarainc/stratus-api-core",
    packages=['stratus_api.core'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=[
        requirements
    ]
)
