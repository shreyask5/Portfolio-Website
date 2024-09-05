FROM python:3.9-slim
WORKDIR /flask
COPY . .
RUN pip3 install flask
CMD [ "flask" , "run" , "--host=0.0.0.0" ]
