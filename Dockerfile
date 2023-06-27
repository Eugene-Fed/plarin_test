FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y git python3-pip

COPY main.py /plarin_test/main.py
COPY requirements.txt /plarin_test/requirements.txt

# !!! ВАЖНО !!! - задать параметры в файле docker/_env. Подробнее в README.md
COPY docker/_env /plarin_test/.env
COPY docker/start.sh /start.sh

RUN cd /plarin_test && pip3 install -r requirements.txt
RUN chmod 0777 /start.sh

CMD ["/start.sh"]
