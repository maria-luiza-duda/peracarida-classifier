from django.shortcuts import render
from backend.models import Record
from django.views import View
from django.shortcuts import redirect
from .minio import upload_image
from django.http import HttpResponse
import pika
from django.conf import settings

# Conectar ao RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Criar uma fila para receber mensagens
channel.queue_declare(queue='treinamento')

# Definir a função de callback para processar as mensagens recebidas
def callback(ch, method, properties, body):
    # Lógica para processar a mensagem recebida
    print(f'Recebido: {body}')

# Registrar a função de callback para receber as mensagens
channel.basic_consume(queue='treinamento', on_message_callback=callback, auto_ack=True)

# Iniciar o consumo das mensagens
channel.start_consuming()

def home(request):
    return render(request, '/frontend/templates/home.html')

def register(request):
    if request.method == 'POST':
        # lógica para processar o formulário de registro
        # criar um novo objeto Record com base nos dados do formulário
        # salvar o objeto no banco de dados
        return redirect('register')  # redirecionar para a página inicial após o registro

    return render(request, '/frontend/templates/register.html')

def upload(request):
    if request.method == 'POST':
        file = request.FILES['file']  # assume que o campo de upload de arquivo tem o nome 'file'
        file_path = 'caminho/para/salvar/o/arquivo'  # defina o caminho onde você deseja salvar o arquivo localmente
        # salve o arquivo localmente
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # faça o upload da imagem para o MinIO
        minio_file_path = upload_image(file_path)

        # lógica adicional para salvar o caminho do arquivo no banco de dados, se necessário

        return redirect('results')  # redirecionar para a página de resultados após o upload

    return render(request, '/frontend/templates/upload.html')

def results(request):
    # lógica para obter os resultados do modelo/classificador
    # você precisará recuperar as informações relevantes do banco de dados
    # e passá-las para o template results.html

    context = {
        # informações relevantes para a exibição dos resultados
    }

    return render(request, '/frontend/templates/results.html', context)

def download_chart(request):
    # lógica para gerar o gráfico de barras como uma imagem PNG
    # salve o gráfico como um arquivo PNG em algum diretório temporário

    file_path = 'path/to/bar/chart.png'

    # leia o arquivo PNG e retorne-o como resposta HTTP para download
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="bar_chart.png"'
        return response
