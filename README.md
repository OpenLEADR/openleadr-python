[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/4317/badge)](https://bestpractices.coreinfrastructure.org/projects/4317)

![OpenLEADR](logo.png)

OpenLEADR is a Python 3 module that provides a convenient interface to OpenADR
systems. It contains an OpenADR Client that you can use to talk to other OpenADR
systems, and it contains an OpenADR Server (VTN) with convenient integration
possibilities.

## Documentation

You can find documentation here: https://openleadr.elaad.io/docs

## Contributing

At this moment, we're finishing off a first usable version. After version 0.5.0,
new bug reports and pull requests are most welcome.

## Developing

```bash
git clone https://github.com/openleadr/openleadr-python
cd openleadr-python
python3 -m venv python_env
./python_env/bin/pip3 install -e .
./python_env/bin/pip3 install -r dev_requirements.txt
```

## Running conformance tests

```bash
./python_env/bin/python3 -m pytest test/conformance
```

