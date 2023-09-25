FROM python:3.9
WORKDIR /app

COPY requirements.txt ./

# install FreeTDS and dependencies
RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y \
 && apt-get install freetds-dev -y \
 && apt-get install freetds-bin -y \
 && apt-get install tdsodbc -y \
 && apt-get install --reinstall build-essential -y

# populate "ocbcinst.ini" as this is where ODBC driver config sits
RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini


ENV RASA_USER='apiuser'
ENV RASA_USER_PW='123@rsi'
RUN echo ${RASA_USER}

WORKDIR /app

# Create the app user
RUN bash -c 'useradd -s /bin/bash -p ${RASA_USER_PW} -d /home/${RASA_USER} -m -U -G sudo ${RASA_USER}'
RUN bash -c 'mkdir -p /app /home/${RASA_USER}/.local/bin'

COPY . .

#Pip command without proxy setting
RUN pip install -r requirements.txt

ENV HOME=/app

#RUN chmod 777 /app
RUN chgrp -R ${RASA_USER} /app 
RUN chmod -R 770 /app

ENV HOME=/app

USER ${RASA_USER}

CMD ["uvicorn" , "api:api" , "--host", "0.0.0.0", "--port", "8000"]