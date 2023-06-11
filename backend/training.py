from minio import Minio
import io
import pika
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.optimizers import Adam
from minio.error import ResponseError

# Configurações do MinIO
minio_endpoint = '192.168.0.102:9000'
minio_access_key = 'admin'
minio_secret_key = 'password'
minio_bucket = 'peracarida'
minio_temp_folder = 'temp'

# Conectar ao MinIO
minio_client = Minio(minio_endpoint, access_key=minio_access_key, secret_key=minio_secret_key, secure=False)

# Função para carregar as imagens do MinIO
def load_image_from_minio(image_path):
    try:
        data = minio_client.get_object(minio_bucket, image_path)
        image_data = data.read()
        image = tf.image.decode_image(image_data, channels=3)
        image = tf.image.resize(image, (150, 150))
        image = image.numpy().astype(np.float32) / 255.0
        return image
    except ResponseError as err:
        print(err)

# Função para fazer upload da imagem do usuário para a pasta temporária no MinIO
def upload_user_image_to_minio(user_image):
    try:
        image_data = tf.io.read_file(user_image)
        image = tf.image.decode_image(image_data, channels=3)
        image = tf.image.resize(image, (150, 150))
        image_data = tf.image.encode_jpeg(image, format='rgb')
        image_path = f'{minio_temp_folder}/user_image.jpg'  # Define o nome do arquivo para a imagem do usuário
        minio_client.put_object(minio_bucket, image_path, io.BytesIO(image_data.numpy()), len(image_data.numpy()), 'image/jpeg')
        return image_path
    except ResponseError as err:
        print(err)

# Carregar todas as imagens do MinIO para treinamento
all_data = []
all_targets = []
all_image_paths = []

# Consultar o MinIO para obter a lista de objetos (imagens) no bucket
objects = minio_client.list_objects(minio_bucket, recursive=True)

def get_target_label(image_path):
    # Extrair o rótulo do caminho da imagem
    label = image_path.split('/')[1]
    return label

for obj in objects:
    image_path = obj.object_name
    image = load_image_from_minio(image_path)
    all_data.append(image)
    all_targets.append(get_target_label(image_path))
    all_image_paths.append(image_path)

all_data = np.array(all_data)
all_targets = np.array(all_targets)

# Definir o modelo da CNN
model = Sequential([
    Conv2D(32, 3, input_shape=(150,150,3), activation='relu'),
    MaxPooling2D(),
    Conv2D(16, 3, activation='relu'),
    MaxPooling2D(),
    Conv2D(16, 3, activation='relu'),
    MaxPooling2D(),
    Flatten(),
    Dense(512, activation='relu'),
    Dense(256, activation='relu'),
    Dense(5, activation='softmax')
])
model.summary()

# Definir os hiperparâmetros
batch_size = 16
input_shape = (150, 150, 3)
random_state = 42
alpha = 1e-5
epoch = 10

# Compilar e treinar o modelo
model.compile(optimizer=Adam(learning_rate=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(all_data, all_targets, epochs=10, batch_size=32)

# Salvar o modelo treinado
model.save('model.h5')

def train_model():
    # Conectar ao RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Criar uma fila para receber mensagens
    channel.queue_declare(queue='analise')

    # Função para lidar com as mensagens recebidas
    def callback(ch, method, properties, body):
        # Carregar o modelo treinado
        model = tf.keras.models.load_model('model.h5')

        # Fazer a predição da imagem do usuário
        user_image_path = body.decode()
        user_image = load_image_from_minio(user_image_path)
        prediction = model.predict(np.array([user_image]))
        predicted_class = np.argmax(prediction)

        # Atualizar os dados de treinamento com a imagem do usuário e o rótulo predito
        all_data = np.append(all_data, [user_image], axis=0)
        all_targets = np.append(all_targets, [str(predicted_class)])

        # Treinar novamente o modelo com os dados atualizados
        model.fit(all_data, all_targets, epochs=10, batch_size=32)

        # Salvar o modelo treinado atualizado
        model.save('model_updated.h5')

        # Enviar mensagem com o nome do arquivo do modelo atualizado
        channel.basic_publish(exchange='', routing_key='treinamento', body='model_updated.h5')

        # Confirmar o processamento da mensagem
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Definir a função de callback para lidar com as mensagens recebidas
    channel.basic_consume(queue='analise', on_message_callback=callback)

    # Aguardar e processar as mensagens recebidas
    channel.start_consuming()

# Chamar a função de treinamento quando receber uma mensagem para iniciar o treinamento
train_model()
