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

<<<<<<< HEAD
# ==========================================
# CREAR SUPERUSUARIO
# ==========================================
echo "👤 Creando superusuario..."
=======
# Crear superusuario automáticamente con tus credenciales
echo "👤 Creando superusuario superinventix..."
>>>>>>> 591b9d07d321cf51d9dab7897300d51c62c58c0d
python manage.py shell -c "
from django.contrib.auth.models import User
from django.db import connection

<<<<<<< HEAD
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
=======
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
>>>>>>> 591b9d07d321cf51d9dab7897300d51c62c58c0d
