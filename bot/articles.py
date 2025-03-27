import logging
import aiofiles
from pathlib import Path
from .config import ARTICLES_PATH, IMAGES_PATH

logger = logging.getLogger(__name__)

async def load_article(article_name):
    logger.info(f"Начата загрузка статьи: {article_name}")
    file_path = ARTICLES_PATH / f"{article_name}.txt"

    if not file_path.exists():
        logger.warning(f"Файл статьи не найден: {file_path}")
        return [{"text": "Статья не найдена.", "image": None}]

    try:
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
            file_content = await f.read()
        logger.info(f"Статья '{article_name}' успешно прочитана из файла: {file_path}")
    except Exception as e:
        logger.exception(f"Ошибка при чтении файла {file_path}: {e}")
        return [{"text": "Ошибка при загрузке статьи.", "image": None}]

    parts = file_content.split("[PART]")
    processed_parts = []

    for index, part in enumerate(parts, start=1):
        lines = part.strip().split("\n")
        text_lines = []
        image = None

        for line in lines:
            if line.startswith("[IMAGE]"):
                image_name = line.replace("[IMAGE]", "").strip()
                image_path = IMAGES_PATH / image_name

                if image_path.exists():
                    image = image_name
                    logger.debug(f"Обнаружено изображение в части {index}: {image}")
                else:
                    logger.warning(f"Изображение '{image_name}' не найдено для статьи '{article_name}' (часть {index})")
                    image = None
            else:
                text_lines.append(line)

        processed_part = {"text": "\n".join(text_lines), "image": image}
        processed_parts.append(processed_part)
        logger.debug(f"Обработана часть {index}: длина текста {len(processed_part['text'])} символов")

    logger.info(f"Статья '{article_name}' обработана на {len(processed_parts)} частей.")
    return processed_parts
