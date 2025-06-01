"""
Script para configurar la base de datos PostgreSQL
Ejecutar este script después de crear la base de datos en PostgreSQL
"""

import os
import django
from django.core.management import execute_from_command_line

def setup_database():
    """
    Configura la base de datos y ejecuta las migraciones
    """
    print("Configurando la base de datos PostgreSQL...")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_trabajos.settings')
    django.setup()
    
    try:
        # Crear migraciones
        print("Creando migraciones...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # Aplicar migraciones
        print("Aplicando migraciones...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("¡Base de datos configurada correctamente!")
        print("\nPara crear un superusuario, ejecuta:")
        print("python manage.py createsuperuser")
        
    except Exception as e:
        print(f"Error al configurar la base de datos: {e}")
        print("\nAsegúrate de que:")
        print("1. PostgreSQL esté instalado y ejecutándose")
        print("2. La base de datos 'sistema_trabajos_db' exista")
        print("3. Las credenciales en settings.py sean correctas")
        print("4. psycopg2-binary esté instalado: pip install psycopg2-binary")

if __name__ == '__main__':
    setup_database()
