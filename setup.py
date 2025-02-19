from setuptools import find_packages, setup

import versioneer

with open("requirements.txt") as install_requires_file:
    install_requires = install_requires_file.read().strip().split("\n")

with open("requirements-dev.txt") as dev_requires_file:
    dev_requires = dev_requires_file.read().strip().split("\n")

with open("README.md") as readme_file:
    readme = readme_file.read()

extras_require = {
    "blob_storage": ["azure-storage-blob"],
    "cosmos_db": ["azure-cosmos"],
    "ml_datastore": ["azureml-core"],
}
extras_require["all_extras"] = sorted(
    {lib for key in extras_require.values() for lib in key if key != "dev"}
)
extras_require["dev"] = dev_requires + extras_require["all_extras"]

setup(
    name="prefect-azure",
    description="Prefect tasks and subflows for interacting with Azure",
    license="Apache License 2.0",
    author="Prefect Technologies, Inc.",
    author_email="help@prefect.io",
    keywords="prefect",
    url="https://github.com/PrefectHQ/prefect-azure",
    long_description=readme,
    long_description_content_type="text/markdown",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(exclude=("tests", "docs")),
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "prefect.collections": [
            "AzureBlobStorageCredentials = prefect_azure.credentials",
            "AzureCosmosDbCredentials = prefect_azure.credentials",
            "AzureMlCredentials = prefect_azure.credentials",
            "prefect_azure = prefect_azure",
            "prefect_azure_container_instance = prefect_azure.container_instance",
        ]
    },
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
    ],
)
