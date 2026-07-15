#!/bin/bash
echo "🚀 Iniciando build de Inventix..."

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios
mkdir -p staticfiles
mkdir -p media

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Aplicar migraciones
python manage.py migrate

# Crear superusuario automáticamente con tus credenciales
echo "👤 Creando superusuario superinventix..."
python manage.py shell -c "
from django.contrib.auth.models import User
from django.db import connection

# Verificar si la tabla auth_user existe
with connection.cursor() as cursor:
    cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='auth_user')\")
    exists = cursor.fetchone()[0]
    
    if exists:
        if not User.objects.filter(username='superinventix').exists():
            User.objects.create_superuser(
                'superinventix', 
                'super@inventix.com', 
                'Solo/leveling/br50.'
            )
            print('✅ Superusuario creado: superinventix')
        else:
            print('ℹ️ Superusuario superinventix ya existe')
    else:
        print('⚠️ La tabla auth_user no existe, las migraciones no se aplicaron correctamente')
"

echo "✅ Build completado exitosamente!"
