import os
import requests
import time
import datetime
import random
import base64
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
import openai
from rembg import remove
from styles import STYLES
from finetunes import FINETUNES

openai_key = ""
openai.api_key = openai_key

flux_key = ""



def create_logger(params):
    # Путь к папке
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join("outputs", today_date)

    # Путь к HTML-файлу 
    log_file_path = os.path.join(folder, "log.html")
    reference_path = f"file:///{os.path.abspath(params.get('reference', '')).replace(os.sep, '/')}"

    # HTML контент
    html_entry = f"""
    <div style="display: flex; align-items: center; margin-bottom: 10px; background-color: #111; color: white; padding: 10px; border-radius: 5px;">
        <div style="width: 33%; display: flex; justify-content: center; flex-direction: column; align-items: center;">
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; overflow: hidden;">
                <a href="{params.get('image_name', '')}" target="_blank">
                    <img src="{params.get('image_name', '')}" alt="Generated Image" style="max-width: 100%; max-height: 420px; width: auto; height: auto; border-radius: 5px;">
                </a>
            </div>
            <p style="text-align: center; color: white; margin-top: 10px;">{params.get('image_name', '')}</p>
        </div>
        <div style="width: 67%; padding-left: 10px;">
            <table id="params-table" border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; width: 100%; color: white;">
                <tr><th style="background-color: #333; color: white; text-align: left;">Parameter</th><th style="background-color: #333; color: white; text-align: left;">Value</th></tr>
                <tr><td style="width: 150px;">Prompt</td><td>{params.get('prompt', '')}</td></tr>
                <tr><td style="width: 150px;">Full Prompt</td><td>{params.get('full_prompt', '')}</td></tr>
                <tr><td style="width: 150px;">Style</td><td>{params.get('style', '')}</td></tr>
                <tr><td style="width: 150px;">Aspect Ratio</td><td>{params.get('aspect_ratio', '')}</td></tr>
                <tr><td style="width: 150px;">Size</td><td>{params.get('size', '')}</td></tr>
                <tr><td style="width: 150px;">Seed</td><td>{params.get('seed', '')}</td></tr>
                <tr><td style="width: 150px;">Reference Path</td><td><a href="{reference_path}" target="_blank" style="color: lightblue; text-decoration: none;">{params.get('reference', '')}</a></td></tr>
                <tr><td style="width: 150px;">Reference Strength</td><td>{params.get('reference_strength', '')}</td></tr>
                <tr><td style="width: 150px;">Finetune</td><td>{params.get('finetune', '')}</td></tr>
                <tr><td style="width: 150px;">Finetune Strength</td><td>{params.get('finetune_strength', '')}</td></tr>
            </table>
            <button onclick="copyTableToClipboard()" style="margin-top: 10px; padding: 8px 12px; background-color: #808080; color: white; border: none; border-radius: 5px; cursor: pointer;">Copy to Clipboard</button>
        </div>
    </div>
    <script>
    function copyTableToClipboard() {{
        const table = document.getElementById("params-table");
        let textToCopy = "";
        for (let row of table.rows) {{
            const cells = Array.from(row.cells).map(cell => cell.innerText);
            textToCopy += cells.join(": ") + "\\n";
        }}
        navigator.clipboard.writeText(textToCopy).then(() => {{
            alert("Parameters copied to clipboard!");
        }});
    }}
    </script>
    """

    # Создание файла, если он не существует
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w", encoding="utf-8") as file:
            file.write(f"<html><head><title>Image Generation Log</title></head><body style='background-color: #222; color: white;'>")
            file.write(f"<h1 style='text-align: left;'>Log for {folder}</h1>")
            file.write("</body></html>")

    # Чтение текущего содержимого лога
    with open(log_file_path, "r", encoding="utf-8") as file:
        existing_content = file.read()

    # Вставляем новую запись
    if "</h1>" in existing_content:
        new_content = existing_content.replace("</h1>", f"</h1>{html_entry}")
    else:
        new_content = existing_content + html_entry

    # Запись обновленного содержимого обратно в файл
    with open(log_file_path, "w", encoding="utf-8") as file:
        file.write(new_content)



def save_image(image, output_format='png', folder=None):
    if not folder:
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        folder = os.path.join("outputs", today_date)

    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    random_seed = random.randint(1000, 9999)
    image_name = f"{timestamp}_{random_seed}.{output_format}"
    image_path = os.path.join(folder, image_name)
    
    image.save(image_path, format=output_format.upper())
    print(f"Изображение успешно сохранено: {image_path}")
    
    return image_name



def generate_image(params):
    # Формируем тело запроса
    json_data = {
        'prompt': params['full_prompt'],
        'aspect_ratio': params['aspect_ratio'],
        'output_format': params['output_format'],
        'seed': params['seed'],
        'prompt_upsampling': False,
        'safety_tolerance': 6,
    }

    if params.get('reference'):
        json_data['image_prompt'] = params['reference_base64']
        json_data['image_prompt_strength'] = params['reference_strength']

    if params.get('finetune'):
        json_data['finetune_id'] = str(FINETUNES[params['finetune']])
        json_data['finetune_strength'] = params['finetune_strength']


    # Отправка запроса
    try:
        request = requests.post(
            f'https://api.us1.bfl.ai/v1/{params["model"]}',
            headers={
                'accept': 'application/json',
                'x-key': flux_key,
                'Content-Type': 'application/json',
            },
            json=json_data
        ).json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при отправке запроса: {e}")

    if "id" not in request:
        raise Exception(f"Не удалось получить request_id. Запрос: {request}")
    
    request_id = request["id"]
    image_url = None


    # Ожидание результата
    while True:
        time.sleep(2)
        try:
            result = requests.get(
                'https://api.us1.bfl.ai/v1/get_result',
                headers={
                    'accept': 'application/json',
                    'x-key': flux_key,
                },
                params={'id': request_id}
            ).json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при получении результата: {e}")

        print(f"Статус: {result['status']} - {result['progress']}")
        if result["status"] == "Ready":
            image_url = result["result"]["sample"]
            break


    # Получение изображения
    if image_url:
        try:
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            image = Image.open(BytesIO(image_response.content))
            return image
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка загрузки изображения. Статус: {image_response.status_code}, ошибка: {e}")
    else:
        raise Exception("Ссылка на изображение не найдена")



def encode_image_to_base64(image_path):
    with Image.open(image_path) as image:
        buffered = BytesIO()
        image.save(buffered, format="PNG")  
        encoded_string = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return encoded_string



def create_images(prompt="", num_images=1, aspect_ratio="1:1", output_format='png', seed=-1, reference_path=None, strength=1, finetune=None, finetune_strength=1.1, style=None):
    # Выбор модели
    model = 'flux-pro-1.1-ultra-finetuned' if finetune else 'flux-pro-1.1-ultra'

    # Генерация полного промта с учетом стиля
    full_prompt = STYLES[f"{style}"]["prompt"].replace("{prompt}", prompt) if style else prompt
    print(f"Prompt: {prompt}")
    print(f"Full prompt: {full_prompt}")

    # Параметры для запроса
    params = {
        "model": model,        
        "prompt": prompt,
        "full_prompt": full_prompt,
        "style": style or "",
        "aspect_ratio": aspect_ratio,
        "output_format": output_format,
    }

    # Доп параметры
    if reference_path:
        params["reference"] = reference_path
        params["reference_base64"] = encode_image_to_base64(reference_path)
        params["reference_strength"] = strength

    if finetune:
        params["finetune"] = finetune
        params["finetune_strength"] = finetune_strength
    
    # Генерация изображений
    images = []
    for i in range(num_images):
        print(f"\nГенерация изображения {i+1}:")
        
        # Генерация seed
        params["seed"] = seed + i if seed != -1 else random.randint(0, 2**31)

        # Генерация изображения
        image = generate_image(params)

        # Сохранение изображения
        image_name = save_image(image, output_format)

        # Логирование
        params["image_name"] = image_name
        params["size"] = f"{image.size[0]}x{image.size[1]}"
        create_logger(params)

        images.append(image)

    return images



def upscale_images(image_paths, outscale=2):
    upscaled_images = []

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')

    if outscale == 2:
        model_path = r'upscale_models\RealESRGAN_x2plus.pth'   # скачать по ссылке: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth
        scale = 2
    elif outscale == 4 or outscale == 3:
        model_path = r'upscale_models\RealESRGAN_x4plus.pth'   # скачать по ссылке: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
        scale = 4 

    state_dict = torch.load(model_path, map_location=device)['params_ema']
    model = RRDBNet(num_in_ch=3, num_out_ch=3, scale=scale).to(device)
    model.load_state_dict(state_dict, strict=True)

    upsampler = RealESRGANer(
        scale=scale,
        model_path=model_path,
        model=model,
        half=True
    )
    
    for path in image_paths:
        img = np.array(Image.open(path).convert("RGB"))
        output, _ = upsampler.enhance(img, outscale=outscale)
        output = Image.fromarray(output)

        _ = save_image(output, "png", r"outputs\upscale")
        
        upscaled_images.append(output)
    
    return upscaled_images



def extract_images(image_paths):
    processed_images = []

    for path in image_paths:
        _, ext = os.path.splitext(path)
        img = Image.open(path)
        if ext.lower() in ['.png', '.webp', '.tiff']:  
            output = remove(img, alpha_matting=True, alpha_matting_erode_size=30)
        else:
            output = remove(img, alpha_matting=True, alpha_matting_erode_size=5)

        _ = save_image(output, "png", r"outputs\extract")
        
        processed_images.append(output)

    return processed_images



def generate_prompt(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a generator of detailed prompts for image generation. "
                        "Enhance the given description by adding missing but contextually relevant details such as "
                        "character poses, facial expressions, clothing styles, textures, weather elements, and lighting conditions. "
                        "The final prompt must be structured as: main object, details, background, all separated by commas for clarity."
                    )
                },
                {
                    "role": "user",
                    "content": f"Improve and transform this description into a detailed, comma-separated prompt for SDXL. Include missing nuances and enhance important aspects. Description: {query}"
                }
            ]
        )
        structured_response = response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        raise ValueError(f"Error during the OpenAI API request: {e}")
        
    return structured_response



def show_images(images, title="Generated Images", max_columns=4):
    num_images = len(images)
    num_columns = min(max_columns, num_images)
    num_rows = (num_images + num_columns - 1) // num_columns 

    fig, axes = plt.subplots(num_rows, num_columns, figsize=(5 * num_columns, 5 * num_rows))
    axes = np.array(axes).reshape(num_rows, num_columns)

    for i, img in enumerate(images):
        row, col = divmod(i, num_columns)
        axes[row, col].imshow(img)
        axes[row, col].axis("off")
        axes[row, col].set_title(f"{i+1}", fontsize=18)

    for row in range(num_rows):
        for col in range(num_columns):
            if row * num_columns + col >= num_images:
                axes[row, col].axis("off")

    plt.suptitle(title, fontsize=20)  
    plt.tight_layout()
    plt.show()
