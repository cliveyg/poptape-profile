FROM python:3.10-alpine
# as base                                                                                                

# these modules enable us to build bcrypt
RUN apk --no-cache add --virtual build-dependencies gcc g++ make libffi-dev openssl-dev

# install openssl
RUN  apk update \
  && apk add openssl \
  && rm -rf /var/cache/apk/* \

RUN apk update && apk add postgresql-dev python3-dev musl-dev
# add bash etc as alpine version doesn't have these
RUN apk add linux-headers 
RUN apk add --no-cache bash gawk sed grep bc coreutils
RUN apk --no-cache add libpq

COPY manage.py /profile/
COPY profile.py /profile/
COPY requirements.txt /profile/
COPY app /profile/app
WORKDIR /profile

RUN mkdir -p /profile/log

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 8070 available to the world outside this container
EXPOSE 8070

# if -u flag in CMD below doesn't work 
# then uncomment this to see python
# print statements in docker logs
ENV PYTHONUNBUFFERED=0

# Run app.py when the container launches
CMD ["gunicorn", "-b", "0.0.0.0:8070", "profile:app"]
