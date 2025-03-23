import json
import os
import re
from collections import Counter

TEXT_FILE = "texts.txt"
FOLDER = "word_versions"  # Папка для хранения версий словарей
MAIN_JSON = "words.json"  # Основной файл со всеми словами

def read_text(file_path):
    """Читает текст из файла, если файл существует."""
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return ""
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read().strip()
        if not text:
            print(f"Файл {file_path} пуст.")
        return text

def extract_russian_words(text):
    """Извлекает только русские слова, исключая числа и слова на других языках."""
    words = re.findall(r"\b[а-яёА-ЯЁ]+\b", text.lower())  # Только русские буквы
    return words

def get_latest_json_file(folder):
    """Определяет последний файл wordsX.json и возвращает его путь."""
    if not os.path.exists(folder):
        os.makedirs(folder)  # Создаём папку, если её нет
        return None  # Файлов ещё нет
    
    files = [f for f in os.listdir(folder) if f.startswith("words") and f.endswith(".json")]
    if not files:
        return None  # Нет файлов в папке

    # Находим последний файл по номеру (words1.json -> words2.json и т.д.)
    numbers = [int(f[5:-5]) for f in files if f[5:-5].isdigit()]
    latest_number = max(numbers, default=0)
    return os.path.join(folder, f"words{latest_number}.json")

def get_new_json_path(folder):
    """Создаёт путь для нового wordsX.json, увеличивая номер файла."""
    latest_file = get_latest_json_file(folder)
    if latest_file is None:
        return os.path.join(folder, "words1.json")  # Первый файл

    latest_number = int(os.path.basename(latest_file)[5:-5])
    return os.path.join(folder, f"words{latest_number + 1}.json")

def read_json(file_path):
    """Читает JSON-файл, если он существует, иначе возвращает пустой словарь."""
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Ошибка чтения {file_path}. Файл поврежден или пуст. Создаём новый...")
    return {}

def update_json(word_counts, folder):
    """Создаёт новую версию файла, дополняя последнюю."""
    latest_file = get_latest_json_file(folder)
    data = read_json(latest_file) if latest_file else {}

    # Обновляем данные
    for word, count in word_counts.items():
        data[word] = data.get(word, 0) + count

    # Определяем путь для новой версии
    new_file_path = get_new_json_path(folder)
    
    # Записываем в новый файл
    with open(new_file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"Создан новый файл: {new_file_path}")

    return data  # Возвращаем обновленный словарь для использования в words.json

def update_main_json(data):
    """Создаёт или обновляет words.json, сортируя слова по частоте."""
    sorted_words = sorted(data.items(), key=lambda x: x[1], reverse=True)
    words_list = [word for word, _ in sorted_words]

    with open(MAIN_JSON, "w", encoding="utf-8") as file:
        json.dump({"words": words_list}, file, ensure_ascii=False, indent=4)

    print(f"Обновлён файл: {MAIN_JSON}")

def main():
    text = read_text(TEXT_FILE)
    if not text:
        return  # Если текста нет, прерываем выполнение
    
    words = extract_russian_words(text)
    if not words:
        print("Не найдено русских слов в тексте.")
        return

    word_counts = Counter(words)
    updated_data = update_json(word_counts, FOLDER)

    # Обновляем основной words.json
    update_main_json(updated_data)

if __name__ == "__main__":
    main()
