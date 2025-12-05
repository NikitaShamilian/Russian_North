import time       # чтобы делать паузы в бесконечном цикле
import os         # чтобы узнавать время последнего изменения файла
import uuid       # для генерации уникальных идентификаторов записей
from sentence_transformers import SentenceTransformer   # создаёт векторы из текста
from qdrant_client import QdrantClient                  # клиент для подключения к Qdrant Cloud
from qdrant_client.models import PointStruct            # формат одной записи ("точки") в базе
from qdrant_client.http.models import VectorParams     # настройки коллекции в Qdrant
from PyPDF2 import PdfReader 

# Путь до файла, за которым программа будет следить
FILE_PATH = "/home/oxana/Desktop/БАЗА_ДАННЫХ_КОМПАНИИ__РУССКИЙ_СЕВЕР_.pdf"

# Название коллекции в базе Qdrant
COLLECTION = "Russian_North_Collection"

# Создаём подключение к Qdrant Cloud
qdrant_client = QdrantClient(
    url="https://63c4a6fa-847f-49ce-801a-b3edebdaefa2.europe-west3-0.gcp.cloud.qdrant.io:6333", 
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.zk7ObI9pXmTfjg6riNrlrWekNP2_OoXuKbs1mEvQxOE",
)

# Это языковая модель от Hugging Face.
# Она преобразует текст в вектор — набор чисел, отражающих смысл.
model = SentenceTransformer("all-MiniLM-L6-v2")

# Коллекция — это контейнер, в котором хранятся векторы.
# size=384 — длина вектора для выбранной модели.
# distance="Cosine" — метрика похожести.

qdrant_client.recreate_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(
        size=384,
        distance="Cosine"
    )
)

def upload_text():
    # --- Читаем PDF специальным методом ---
    reader = PdfReader(FILE_PATH)

    # объединяем текст со всех страниц
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    # --- преобразуем текст в вектор ---
    vector = model.encode(text).tolist()

    # --- формируем точку (point), которую сохраним в Qdrant ---
    point = PointStruct(
        id=str(uuid.uuid4()),     # создаём уникальный ID записи
        vector=vector,            # сам вектор (список чисел)
        payload={                 # полезная нагрузка (дополнительные данные)
            "text": text          # сам текст, чтобы потом можно было его прочитать)
        }
    )

    # --- добавляем запись в коллекцию ---
    qdrant_client.upsert(
        collection_name=COLLECTION,
        points=[point]  # список из одной записи
    )

    # --- выводим сообщение ---
    print("Обновлено в Qdrant!")  # пользователь видит, что данные обновлены

# Сначала узнаём, когда в последний раз файл меняли (в секундах)
last_modified = os.path.getmtime(FILE_PATH)

print("Слежение за изменениями файла")
# При старте сразу один раз загружаем текст
upload_text()

# и каждые 3 секунды проверять, изменился ли файл.
while True:
    # Проверяем текущее время изменения файла
    new_time = os.path.getmtime(FILE_PATH)

    # Если оно не совпадает с предыдущим — файл был сохранён
    if new_time != last_modified:
        print("Файл изменился, обновляем базу")
        upload_text()             # снова загружаем текст в Qdrant
        last_modified = new_time  # обновляем время "последнего изменения"

    # Небольшая пауза, чтобы не перегружать процессор
    time.sleep(3)