#!/bin/bash
echo "🚀 Iniciando build de Inventix..."

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios
mkdir -p staticfiles
mkdir -p media

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# ==========================================
# APLICAR MIGRACIONES PRIMERO
# ==========================================
echo "🗄️ Aplicando migraciones..."
python manage.py migrate

# ==========================================
# CREAR SUPERUSUARIO DESPUÉS DE LAS MIGRACIONES
# ==========================================
echo "👤 Creando superusuario superinventix..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='superinventix').exists():
    User.objects.create_superuser(
        'superinventix', 
        'super@inventix.com', 
        'Solo/leveling/br50.'
    )
    print('✅ Superusuario creado: superinventix')
else:
    print('ℹ️ Superusuario superinventix ya existe')
"

echo "✅ Build completado exitosamente!"