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

# ==========================================
# CREAR SUPERUSUARIO
# ==========================================
echo "👤 Creando superusuario..."
python manage.py shell -c "
from django.contrib.auth.models import User
from django.db import connection

# Verificar que la tabla existe
with connection.cursor() as cursor:
    cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='auth_user')\")
    table_exists = cursor.fetchone()[0]
    
    if not table_exists:
        print('❌ La tabla auth_user no existe - las migraciones fallaron')
        exit(1)

# Crear o actualizar superusuario
username = 'superinventix'
password = 'Solo/leveling/br50.'
email = 'super@inventix.com'

user, created = User.objects.get_or_create(username=username, defaults={'email': email})
user.set_password(password)
user.is_superuser = True
user.is_staff = True
user.save()

# Verificar que se guardó
verification = User.objects.get(username=username)
print(f'✅ Superusuario {username} verificado - ID: {verification.id}')
print(f'   Superuser: {verification.is_superuser}')
print(f'   Staff: {verification.is_staff}')
"

echo "✅ Build completado exitosamente!"