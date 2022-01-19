FROM python:3.9.7
RUN apt-get update
WORKDIR /B1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 9000
CMD ["python", "app.py"]