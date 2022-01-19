FROM python:3.9.7
RUN apt-get update
WORKDIR /B3
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 9002
CMD ["python", "main.py"]