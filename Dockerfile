FROM python:3.9

RUN apt-get update

RUN pip install --upgrade pip

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app


# Install pip requirements
COPY ./requirements.txt /app
RUN pip install -r /app/requirements.txt

RUN python -m spacy download en_core_web_trf

ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV CODE_CHECKS_PATH="/app/scraper/app/"