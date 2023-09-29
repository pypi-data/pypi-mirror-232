# stem-rate

[![PyPi](https://img.shields.io/pypi/v/stem-rate.svg)](https://pypi.org/project/stem-rate)

-----

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
- [Contributors](#contributors)
- [License](#license)

## Installation

To install `stem-rate`, you can use pip:

```console
pip install stem-rate
```

## Usage

### Command Line Interface

You can use `stem-rate` from the command line to add a fixed local clock stem model to BEAST1 XML files. 

**Basic usage**

```bash
stem_rate flc --xml "your_input.xml" --stem "stem_value" --output "your_output.xml"
```

**Arguments and Options**

- `--xml, -x`: Path to the BEAST XML file.
- `--stem, -s`: Group sequences containing this value to define a stem.
- `--fasta, -f` (Optional): Sequences to add to XML in FASTA format. Dates must be in decimal year format.
- `--delimiter, -d` (Optional): Delimiter for date in FASTA header. Default is `|`.
- `--position, -p` (Optional): Position of date in FASTA header. Default is -1.
- `--output, -o`: Path to the output BEAST XML file.
- `--version, -v` (Optional): Print the version and exit.

For example, if you want to add sequences from a FASTA file and specify a date delimiter, you can run:

```bash
stem_rate flc --xml "your_input.xml" --stem "stem_value" --fasta "your_fasta.fasta" --delimiter "|" --position -1 --output "your_output.xml"
```

## Contributors

- [Wytamma Wirth](mailto:wytamma.wirth@me.com)

## License

`stem-rate` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.