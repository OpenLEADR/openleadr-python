FROM python:3.8.0
ADD . /OPENLEADER-PYTHON
WORKDIR /OPENLEADER-PYTHON
RUN pip3 install --upgrade setuptools
RUN pip3 install virtualenv
RUN virtualenv python_env --python=python3.8
RUN . python_env/bin/activate
RUN pip3 install "Flask[async]"
RUN pip3 install -r dev_requirements.txt
CMD ["python", "./main.py"]