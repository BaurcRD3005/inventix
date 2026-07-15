#!/bin/bash
# ==========================================
# SCRIPT DE CONSTRUCCIÓN PARA RENDER
# ==========================================

echo "🚀 Iniciando build de Inventix..."
echo "========================================"

# 1. Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# 2. Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p staticfiles
mkdir -p media

# 3. Recolectar archivos estáticos
echo "🎨 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# 4. Aplicar migraciones a la base de datos
echo "🗄️ Aplicando migraciones..."
python manage.py migrate

# 5. Crear superusuario si no existe (opcional)
echo "👤 Creando superusuario (si no existe)..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@inventix.com', 'admin123')
    print('✅ Superusuario creado: admin/admin123')
else:
    print('ℹ️ Superusuario ya existe')
"

echo "========================================"
echo "✅ Build completado exitosamente!"
echo "🚀 La aplicación está lista para ejecutarse"