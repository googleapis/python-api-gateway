# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import io
import os

import setuptools  # type: ignore

name = "google-cloud-api-gateway"
version = "1.2.2"
description = "API Gateway client library"
release_status = "Development Status :: 5 - Production/Stable"
url = "https://github.com/googleapis/python-api-gateway"
dependencies = [
    "google-api-core[grpc] >= 2.8.0, <3.0.0dev",
    "proto-plus >= 1.15.0, <2.0.0dev",
    "protobuf >= 3.19.0, <4.0.0dev",
]

package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, "README.rst")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name=name,
    version=version,
    description=description,
    long_description=readme,
    author="Google LLC",
    author_email="googleapis-packages@google.com",
    license="Apache 2.0",
    url=url,
    packages=[
        package
        for package in setuptools.PEP420PackageFinder.find()
        if package.startswith("google")
    ],
    namespace_packages=("google", "google.cloud"),
    platforms="Posix; MacOS X; Windows",
    include_package_data=True,
    install_requires=dependencies,
    python_requires=">=3.7",
    classifiers=[
        release_status,
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)
