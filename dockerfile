FROM python:3.8.0
ADD . /OPENLEADR-PYTHON
WORKDIR /OPENLEADR-PYTHON
EXPOSE 5000
RUN pip3 install "Flask[async]"
RUN pip3 install -r dev_requirements.txt
CMD ["python", "./main.py"]