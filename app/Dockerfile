FROM python:3

# create project's directory
RUN mkdir /sightspotter
RUN mkdir /sightspotter/db
RUN mkdir /sightspotter/app

# add credentials to container
COPY app/secret.env /sightspotter/app/secret.env

# add database to container
COPY db/sightspotter.sqlite3 /sightspotter/db/sightspotter.sqlite3

# build from setup
ADD setup.py /sightspotter
ADD src/sightspotter /sightspotter/src/sightspotter
RUN cd /sightspotter && python setup.py develop

WORKDIR /

CMD exec sightspotter poll --test

