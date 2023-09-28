from setuptools import setup, find_packages

setup(
    name="mkdocs-roamlinks-plugin-extra",
    version="0.3.4",
    description="Fork of @Jackiexiao mkdocs-roamlinks-plugin package with added support for special chars.",
    long_description="A MkDocs plugin that autogenerates relative links and convert roamlike links for foam and obsidian between markdown pages.",
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
            "roamlinks = mkdocs_roamlinks_plugin.plugin:RoamLinksPlugin",
        ]
    },
)
