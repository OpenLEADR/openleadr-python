![Test Suite](https://github.com/OpenLEADR/openleadr-python/workflows/Test%20Suite/badge.svg)
 [![Test Coverage](https://openleadr.org/coverage/badge.svg)](https://openleadr.org/coverage)
 ![PyPI Downloads](https://img.shields.io/pypi/dm/openleadr?color=lightblue&label=PyPI%20Downloads)
 [![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/4317/badge)](https://bestpractices.coreinfrastructure.org/projects/4317)

![OpenLEADR](https://openleadr.org/images/lf-logo.png)

OpenLEADR is a Python 3 module that provides a convenient interface to OpenADR
systems. It contains an OpenADR Client that you can use to talk to other OpenADR
systems, and it contains an OpenADR Server (VTN) with convenient integration
possibilities.

It currently implements the OpenADR 2.0b specification.

## Documentation

You can find documentation here: https://openleadr.org/docs.


## Credits

OpenLEADR would not have been possible without the support from ElaadNL Foundation and the Linux Foundation Energy. Click the logos below to learn more about them.

[![ElaadNL Logo](https://openleadr.org/images/elaad-logo.png)](https://elaad.nl)

[![LF Energy Logo](https://openleadr.org/images/lf-energy-logo.png)](https://lfenergy.org)

## Contributing

If you'd like to help make OpenLEADR better, you can do so in the following ways:


### File bug report or feature request

We keep track of all bugs and feature requests on [Github Issues](https://github.com/openleadr/openleadr-python/issues). Please search the already close issues to see if your question was asked before.

You're also very welcome to leave comments on existing issues with your ideas on how to improve OpenLEADR.


### File a pull request

We'd love for you to contribute code to the project. We'll take a look at all pull requests, no matter their state. Please note though, that we will only accept pull requests if they meet at least the following criteria:

- Your code style is flake8 compliant (with a maximum line length of 127 characters)
- You provide tests for your new code and your code, and you amend any previous tests that fail if they are impacted by your code change
- Your pull request refers to an Issue on our issue tracker, so that we and other people can see what problem is being solved.
- You sign off your commits (`git commit -s`), to indicate that your contribution complies with our license and does not violate anybody else's copyright.

That said, please don't let the above requirements discourage you from filing a pull requests. If you don't meet all of the above requirements, we'll help you fix the remaining things to get it into shape.


### Security issues

Let it be clear that this code base is still in a development stage, and we don't yet recommend using it for mission critical applications or applications where security is paramount.

That said, we do try to make OpenLEADR as secure as can be to work with. If you find a security vulnerability in OpenLEADR, please let us know at security AT openleadr DOT org. We will get back to you within 72 hours to follow up. We are committed to the following steps:

- Security vulnerabilities with a known fix will be addressed as soon as possible. This means that work on other things will be put on hold until the security issue is fixed.
- If a fix is not readily available, we will publish a warning that describes the vulnerable situation and, if possible, any mitigating steps that users of OpenLEADR can take.
- After any security issue is fixed, we will publish information on it in the Changelog.


## Developing

We recommend the following development setup for working with OpenLEADR (this is on Linux / macOS):

```bash
git clone https://github.com/openleadr/openleadr-python
cd openleadr-python
python3 -m venv python_env
./python_env/bin/pip3 install -e .
./python_env/bin/pip3 install -r dev_requirements.txt
```

To run the test suite, you can use the following command:

```bash
./python_env/bin/python3 -m pytest -v test/
```

