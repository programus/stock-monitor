FROM python:3.11-slim as base
# RUN apk add --no-cache gcc g++ cmake libxml2-dev libxslt-dev
RUN apt-get update && apt-get install -y build-essential libxml2-dev libxslt-dev cron
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN crontab -u root ./crontab
CMD [ "cron", "-f" ]