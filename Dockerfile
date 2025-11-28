# 1. Usa uma imagem base do Python
FROM python:3.9-slim

# 2. Instala dependências do sistema necessárias para o Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Instala o Google Chrome Stable
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# 4. Configura a pasta de trabalho
WORKDIR /app

# 5. Copia os arquivos do seu PC para o servidor
COPY . /app

# 6. Instala as bibliotecas Python (Flask, Selenium, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# 7. Comando para iniciar o site (usa Gunicorn para produção)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]