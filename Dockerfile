FROM python:3.9
ADD . /code
WORKDIR . /code
RUN pip3 install -r requirements.txt
ENV CONF_RESTSQL_PATH="/code" CONF_LOGGER_PATH="/code"
RUN ["python","/code/RestSQLServer/manage.py","runserver","0.0.0.0:8000"]