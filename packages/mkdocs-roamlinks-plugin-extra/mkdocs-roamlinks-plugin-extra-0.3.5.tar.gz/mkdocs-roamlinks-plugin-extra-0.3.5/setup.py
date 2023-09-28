from setuptools import setup, find_packages


def load_readme():
    with open("README.md") as f:
        readme = f.read()
    f.close()
    return readme


setup(
    name="mkdocs-roamlinks-plugin-extra",
    version="0.3.5",
    description="Fork of @Jackiexiao mkdocs-roamlinks-plugin package with added support for special chars.",
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    keywords="mkdocs",
    url="https://github.com/harttraveller/mkdocs-roamlinks-plugin-extra",
    author="harttraveller",
    license="MIT",
    python_requires=">=3.6",
    install_requires=[
        "mkdocs>=1.0.4",
    ],
    extras_require={"dev": ["pytest"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": [
            "roamlinks_extra = mkdocs_roamlinks_plugin_extra.plugin:RoamLinksPlugin",
        ]
    },
)
