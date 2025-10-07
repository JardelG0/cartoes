#!/bin/bash
set -e

cd /usr/local/lsws/Example/html/demo

echo "🔄 Atualizando repositório..."
sudo -u www-data git pull origin main

echo "📦 Atualizando dependências..."
source venv/bin/activate
pip install -r requirements.txt --quiet

echo "🗃 Aplicando migrações..."
python manage.py migrate --noinput

echo "🎨 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "♻️ Reiniciando serviço..."
sudo systemctl restart creditmanager

echo "✅ Deploy concluído com sucesso!"
