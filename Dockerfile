# Following manual https://docs.docker.com/language/python/build-images/
FROM python:3.9.10-slim

# set work directory
WORKDIR /usr/sales_helper_bot/

# copy requirements
COPY requirements.txt requirements.txt

# install requirements and copy sources
RUN pip3 install -r requirements.txt
COPY . .

# run
CMD [ "python3", "bot.py"]
