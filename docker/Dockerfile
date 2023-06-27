FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y git python3-pip
RUN git clone -b main https://github.com/Eugene-Fed/plarin_test.git
COPY _env /plarin_test/.env
COPY start.sh /start.sh
RUN cd /plarin_test && pip3 install -r requirements.txt
RUN chmod 0777 /start.sh
CMD ["/start.sh"]
