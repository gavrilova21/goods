FROM python:3.7

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /user
WORKDIR /user
ADD requirements.txt /user/
RUN pip install -r requirements.txt


COPY user_service /user/user_service
WORKDIR /user/user_service