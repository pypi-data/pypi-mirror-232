# GitLab Security Reports - Presenter

_Provide build information and pretty-printed GitLab security reports in a CI pipeline_


## Requirements

[Jinja2](https://pypi.org/project/Jinja2/) (Version 3.1.2 or newer)


## Installation

```
pip install glsr-present
```

Installation in a virtual environment is strongly recommended.


## Usage

Output of `python3 -m glsr_present --help`:

```
usage: glsr_present [-h] [--version] [-d | -v | -q] [-l] [-n]
                    [-o OUTPUT_DIRECTORY] [-t TEMPLATE]

Provide build information and pretty-printed GitLab security reports in a CI
pipeline

options:
  -h, --help            show this help message and exit
  --version             print version and exit
  -l, --list-templates  list available templates and exit
  -n, --dry-run         no action (dry run): do not write any files
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        output directory (default: docs)
  -t TEMPLATE, --template TEMPLATE
                        template for the overview page (default: build-
                        info.md.j2)

Logging options:
  control log level (default is WARNING)

  -d, --debug           output all messages (log level DEBUG)
  -v, --verbose         be more verbose (log level INFO)
  -q, --quiet           be more quiet (log level ERROR)
```


## Further reading

Please see the documentation at <https://blackstream-x.gitlab.io/glsr-present>
for detailed usage information.

If you found a bug or have a feature suggestion,
please open an issue [here](https://gitlab.com/blackstream-x/glsr-present/-/issues)

