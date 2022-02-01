FROM python:3.8
USER root

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install pytest
RUN pip install pytest-cov
RUN pip install senkalib
RUN pip install pylint
RUN pip install black