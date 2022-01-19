FROM python:3.9.7
RUN apt-get update
WORKDIR /B2
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 9001
CMD ["python", "main.py"]