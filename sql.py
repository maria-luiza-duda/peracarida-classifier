import os
import django

# Definir a variável de ambiente DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classifier.settings')

# Carregar as configurações do Django
django.setup()

# Agora você pode importar e usar os modelos do Django
from backend.models import Record


def query_records():
    # Query all records
    records = Record.objects.all()
    print(records)
    # Check if any records were found
    if records:
        # Process the records
        for record in records:
            print(record.field1, record.field2)
    else:
        print("Nenhum registro encontrado.")
