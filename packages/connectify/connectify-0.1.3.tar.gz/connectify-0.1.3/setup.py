import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="connectify",
    version="0.1.3",
    author="Vitali Muladze",
    author_email="muladzevitali@gmail.com",
    description="Different Python I/O handlers",
    long_description=long_description,
    install_requires=("slack_sdk==3.22.0",
                      "python-dotenv==1.0.0"),
    long_description_content_type="text/markdown",
    url="https://github.com/muladzevitali/connectify",
    project_urls={
        "Bug Tracker": "https://github.com/muladzevitali/connectify/issuesL",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=("connectify",
              "connectify.slack_services"
              ),

    python_requires=">=3.8"
)
