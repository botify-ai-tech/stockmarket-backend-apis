FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app        

COPY requirements.txt .

RUN apt update
RUN  apt-get install git -y

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 
EXPOSE 8000