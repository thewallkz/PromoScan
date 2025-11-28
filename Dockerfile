# 1. Usa uma imagem base do Python
FROM python:3.9-slim

# 2. Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Instala o Google Chrome Stable (MÉTODO NOVO CORRIGIDO)
# Baixa a chave e salva na pasta correta sem usar apt-key
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub > /usr/share/keyrings/google-chrome-keyring.pub \
    && echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.pub] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# 4. Configura a pasta de trabalho
WORKDIR /app

# 5. Copia os arquivos do seu PC para o servidor
COPY . /app

# 6. Instala as bibliotecas Python
RUN pip install --no-cache-dir -r requirements.txt

# 7. Comando para iniciar o site
#TIMEOUT DE 120 SEGUNDOS (2 minutos)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "app:app"]