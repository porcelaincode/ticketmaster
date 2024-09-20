FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

RUN wget -N https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5672

CMD ["python", "script.py"]
