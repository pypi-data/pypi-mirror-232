# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mussel']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['mussel = mussel:mussel']}

setup_kwargs = {
    'name': 'mussel',
    'version': '1.0.0',
    'description': 'Build Python executable for any environment with pyinstaller',
    'long_description': '<p align="center">\n    <img alt="Mussel-Python" title="Mussel-Python" src="docs/images/banner_light.png#gh-dark-mode-only" width="450">\n    <img alt="Mussel-Python" title="Mussel-Python" src="docs/images/banner.png#gh-light-mode-only" width="450">\n</p>\n<div align="center">\n  <b><i>Python for any environment</i></b>\n<hr>\n\n</div>\n\n# Overview\n\nMussel Python is a versatile tool designed to streamline the process of creating standalone \nPython applications with **pyinstaller** within a standardized environment.\n\n# Features\n\n* **Isolated Build Environment:** Utilize Docker to build standalone Python application (with its dependencies), ensuring a consistent and isolated build environment.\n\n* **Dependency Management:** Easily manage Python package dependencies and versions within your mussel app, avoiding conflicts and ensuring reproducibility.\n\n* **Build Automation:** Streamline the build process, making it easy to share and deploy your Python applications.\n\n* **Portability:** Python application built with mussel-python runs consistently across different operating systems and environments.\n\n# Getting Started\n\n## Prerequisites\n\nBefore you begin, make sure you have the following prerequisites installed on your system:\n\n* Docker ([Install Docker Engine](https://docs.docker.com/engine/install/))\n* `mussel`\n  * Install with `pip install mussel`\n\n## Write your first mussel standalone app\n\n### 1. Define your Python application code\n\nScript above will print Python & OpenSSL version\n\n```python\nimport sys\nimport ssl\n\nif __name__ == \'__main__\':\n    print("Python", sys.version)\n    print(ssl.OPENSSL_VERSION)\n```\n\n### 2. Build your standalone app with mussel-python\n\n**Usage**\n```shell\nmussel --python <VERSION> (--source PATH) [pyinstaller options]\n```\n\nFor detailed information on pyinstaller options, please reach https://pyinstaller.org/en/stable/usage.html#options\n\nExample below will build a single file standalone executable (`-F`) from a python script `my-app.py`\n```bash\n$ mussel --python 3.10 -F my-app.py\n```\n\n### 3. Run your standalone executable\n\nExecutable files are by default created within a `dist` directory.\n\n```shell\n$ ./dist/my-app\nPython 3.10.12 (main, Sep 29 2023, 07:32:58) [GCC 4.8.4]\nOpenSSL 3.1.3 19 Sep 2023\n\n# Try with ubuntu:14.04 container\n$ docker run --rm -v ./dist/my-app:/my-app ubuntu:14.04 /my-app\nPython 3.10.12 (main, Sep 29 2023, 07:32:58) [GCC 4.8.4]\nOpenSSL 3.1.3 19 Sep 2023\n\n# Try with more recent distro... ubuntu:22.04\n$ docker run --rm -v ./dist/my-app:/my-app ubuntu:22.04 /my-app\nPython 3.10.12 (main, Sep 29 2023, 07:32:58) [GCC 4.8.4]\nOpenSSL 3.1.3 19 Sep 2023\n\n# Fedora 40 ?\n$ docker run --rm -v ./dist/my-app:/my-app fedora:40 /my-app\nPython 3.10.12 (main, Sep 29 2023, 07:32:58) [GCC 4.8.4]\nOpenSSL 3.1.3 19 Sep 2023\n\n# alpine ?\n$ docker run --rm -v ./dist/my-app:/my-app alpine:latest sh -c "apk add libc6-compat gcompat ; ./my-app"\n...\nOK: 8 MiB in 19 packages\nPython 3.10.12 (main, Sep 29 2023, 07:32:58) [GCC 4.8.4]\nOpenSSL 3.1.3 19 Sep 2023\n```\n\n# License\n\nThis project is licensed under the MIT License.\n\n# Acknowledgments\n\n* Inspired by the need for standalone & environment agnostic Python application.\n* Built with [Docker](https://www.docker.com/) and [pysintaller](https://pyinstaller.org/en/stable/index.html).\n\n# Contact\n\nFor questions or feedback, please contact [contact@tmahe.dev](mailto:contact@tmahe.dev).\n\nHappy coding!',
    'author': 'Thomas Mahé',
    'author_email': 'contact@tmahe.dev',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
