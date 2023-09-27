# GitLab Security Reports Presenter

_Provide build information and pretty-printed GitLab security reports in a CI pipeline_

---
> **⚠ Exposes found weaknesses and vulnerabilities**

> Publishing scan results can pose a security risk,
> consider using **glsr-present** in trusted environments only.

---


## Installation from PyPI

```
pip install glsr-present
```

[Jinja2](https://pypi.org/project/Jinja2/) (Version 3.1.2 or newer)
is required and will be installed as an indirect dependency if not installed yet.

Installation in a virtual environment is strongly recommended.


## Usage

Output of `python3 -m glsr_present --help`:

```
usage: glsr_present [-h] [--version] [-d | -v | -q]
                    [-b TEMPLATE_NAME | -f TEMPLATE_PATH] [-l] [-n]
                    [-o DESTINATION]

Provide build information and pretty-printed GitLab security reports in a CI
pipeline

options:
  -h, --help            show this help message and exit
  --version             print version and exit
  -l, --list-templates  list available templates and exit
  -n, --dry-run         no action (dry run): do not write any files
  -o DESTINATION, --output-directory DESTINATION
                        write files to directory DESTINATION (default: docs)

Logging options:
  control log level (default is WARNING)

  -d, --debug           output all messages (log level DEBUG)
  -v, --verbose         be more verbose (log level INFO)
  -q, --quiet           be more quiet (log level ERROR)

Template option:
  Select a builtin template or one from the file system for the overview
  page

  -b TEMPLATE_NAME, --builtin-template TEMPLATE_NAME
                        use the built-in template TEMPLATE_NAME (default:
                        build-info.md.j2)
  -f TEMPLATE_PATH, --template-file TEMPLATE_PATH
                        use the template from file TEMPLATE_PATH
```


## Further reading

Please see the documentation at <https://blackstream-x.gitlab.io/glsr-present>
for detailed usage information.

If you found a bug or have a feature suggestion,
please open an issue [here](https://gitlab.com/blackstream-x/glsr-present/-/issues)

