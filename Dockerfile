FROM python:3.9.7

RUN apt-get update

WORKDIR /waldowallpaper

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./waldowallpaper .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]