## Инструкция по использованию приложения для генерации изображений

### Описание работы приложения [Visual](https://visual.kaisaco.com)

Приложение позволяет создавать изображения с помощью текстовых описаний (промтов) и различных параметров стилизации. 

### **Основные параметры**

1. **prompt**: текстовое описание того, что нужно изобразить.
   - Готовый текстовый промт (описание должно быть на английском языке).
   - Референсы и примеры промтов можно посмотреть на [Civitai](https://civitai.com/images).

2. **style**: стиль изображения.
   - По умолчанию стиль не задан.
   - Доступные стили:
     - Character
     - Background
     - Hyperrealism
     - Cinematic
     - Photograph
     - Masterpiece
     - Sharp
     - Comic
     - Anime
     - Graffiti

3. **num_images**: количество генерируемых изображений.
   - Значение по умолчанию: `1`.
   - Среднее время генерации одного изображения: 15-20 секунд.

4. **aspect_ratio**: соотношение сторон изображения.
   - Значение по умолчанию: `1:1` (разрешение 2048x2048).
   - Доступные значения: от `21:9` до `9:21`.
   - Рекомендуемые значения:
     - Для персонажа в полный рост: `9:16` (разрешение 1536x2752) 
     - Для фона: `16:9` (разрешение 1536x2752)

5. **seed**: зерно для воспроизводимости сгенерированных изображений.
   - Значение по умолчанию: `-1` (случайная генерация).
   - Позволяет получать одинаковые изображения при повторной генерации.

6. **reference_path**: путь к изображению, которое будет использовано в качестве референса.
   - По умолчанию параметр не используется (`None`).
   - Параметр позволяет задать изображение, которое будет служить основой для генерации нового изображения.

7. **strength**: сила воздействия референсного изображения.
   - Значение по умолчанию: `1`.
   - Доступные значения: от `0` до `1`.
   - Определяет, насколько сильно референсное изображение будет влиять на результат. Чем выше значение, тем сильнее влияние.

8. **finetune**: возможность генерации образа.
   - По умолчанию параметр не используется (`None`).
   - Параметр позволяет применить обученную на образе модель для генерации нового изображения.
   - Доступные образы:
     - Elvis frog
     - Succubus
     - Rhino

9. **finetune_strength**: сила воздействия образа.
   - Значение по умолчанию: `1.2`.
   - Доступные значения: от `0` до `2`.
   - Определяет, насколько сильно образ будет влиять на результат. Чем выше значение, тем сильнее влияние.

## Пример генераций

<p float="left">
  <img src="https://raw.githubusercontent.com/LeadingIsmi/Creatives/main/outputs/2025-03-03/2025-03-03_13-34-27_6178.png" width="300"/>
  <img src="https://raw.githubusercontent.com/LeadingIsmi/Creatives/main/outputs/2025-03-03/2025-03-03_14-40-41_7869.png" width="300"/>
  <img src="https://raw.githubusercontent.com/LeadingIsmi/Creatives/main/outputs/2025-03-03/2025-03-03_20-59-58_5958.png" width="300"/>
  <img src="https://raw.githubusercontent.com/LeadingIsmi/Creatives/main/outputs/2025-03-03/2025-03-03_21-16-31_2708.png" width="300"/>
</p>

**Промты к изображениям:**

1. *comic rhino, wearing Easter costume, wearing glasses, holding a cocktail, standing in front of Easter decorations with eggs, white background*
2. *singing frog, wearing Easter costume, holding a microphone, performing on a stage, white background*
3. *standing comic succubus, wearing pink Easter dress, bunny hat, posing with Easter egg, white background*
4. *explorer in Indiana Jones style, with Easter eggs and a map, pointing at a betting slip, white background*
