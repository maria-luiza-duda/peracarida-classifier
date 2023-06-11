from django.shortcuts import render, redirect
from django.views import View
from minio import Minio
import os
import pika
from .forms import RecordForm
from backend.models import Record

# Configurações do MinIO
minio_endpoint = '192.168.0.102:9000'
minio_access_key = 'admin'
minio_secret_key = 'password'
minio_temp_bucket = 'temp'
minio_bucket = 'peracarida'

# Conectar ao MinIO
minio_client = Minio(minio_endpoint, access_key=minio_access_key, secret_key=minio_secret_key, secure=False)


class RegisterRecordView(View):
    template_name = 'registerrecord.html'
    form_class = RecordForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                record = form.save()  # Save the record to the database
                print(record)  # Print the saved record for debugging purposes
                return redirect('frontend:registerrecord')
            except Exception as e:
                print(e)  # Print any exceptions that occur during saving
        else:
            print(form.errors)  # Print validation errors

        return render(request, self.template_name, {'form': form})

class HomeView(View):
    def get(self, request):
        carouselImages = [
            { 'url': 'frontend/static/img/Campylaspis sp5.jpg' },
            { 'url': 'frontend/static/img/05b7602088d4a044cd3ea6b9a81f35f8.jpg' },
            { 'url': 'frontend/static/img/images (16)' },
            { 'url': 'frontend/static/img/images (17).jpg' },
            { 'url': 'frontend/static/img/images_7.jpg' },
        ]
        return render(request, 'home.html', {'carouselImages': carouselImages})

class UploadView(View):
    def get(self, request):
        form = RecordForm()
        return render(request, 'upload.html', {'form': form})

    def post(self, request):
        form = RecordForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            # Fazer o upload da imagem para o MinIO na pasta temporária
            try:
                filename = file.name
                temp_path = os.path.join(minio_temp_bucket, filename)
                minio_client.put_object(minio_temp_bucket, temp_path, file, length=file.size)
            except Exception as err:
                print(err)
                return render(request, 'upload.html', {'form': form})

            return redirect('frontend:analyze', temp_path=temp_path)

        return render(request, 'upload.html', {'form': form})

class ResultsView(View):
    def get(self, request):
        image_url = 'path/to/image.jpg'
        # Obter os resultados da classificação
        classification_results = {'class1': 0.4, 'class2': 0.6}
        return render(request, 'results.html', {'image_url': image_url, 'classification_results': classification_results})

class AnalyzeView(View):
    template_name = 'analyze.html'

    def post(self, request):
        # Verificar se foi enviado um arquivo
        if 'image' not in request.FILES:
            return redirect('analyze')

        # Salvar a imagem do usuário em um arquivo temporário
        user_image = request.FILES['image']
        user_image_path = os.path.join(minio_temp_bucket, 'user_image.jpg')
        with open(user_image_path, 'wb') as f:
            f.write(user_image.read())

        # Fazer upload da imagem do usuário para o MinIO
        try:
            minio_client.fput_object(minio_bucket, user_image_path, user_image_path)
        except Exception as err:
            print(err)

        # Conectar ao RabbitMQ e enviar a mensagem com o caminho da imagem
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='analise')
        channel.basic_publish(exchange='', routing_key='analise', body=user_image_path)
        connection.close()

        return redirect('analyze')

    def get(self, request):
        return render(request, self.template_name)