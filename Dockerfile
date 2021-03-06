FROM ubuntu:18.04
RUN apt-get update -y
RUN apt-get install python3.6 python3-pip python3-dev -y
RUN apt-get install curl -y
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install setuptools==41.0.0
RUN pip3 install -U pip wheel
RUN pip3 install -r requirements.txt
COPY i3_export_drive.py /app/
COPY credentials.json /app/credentials.json
COPY test.json /app/test.json
COPY test.txt /app/test.txt
ENTRYPOINT ["/usr/bin/python3", "i3_export_drive.py"]
