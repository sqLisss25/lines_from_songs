from PIL import Image, ImageDraw, ImageFont, ImageFilter


def str_count():
    n = 0
    return n


def create_blur(
    input_path="input_1.png",
    output_path="blur_2.png",
    size=(800, 410),
    blur_radius=80,
    downscale_factor=6
):
    # print(input_path, output_path, size, blur_radius, downscale_factor)
    img = Image.open(input_path).convert("RGB")


    # 1. Жёстко уменьшаем (убивает детали)
    new_size = (
        size[0] // downscale_factor,
        size[1] // downscale_factor
    )
    small = img.resize(new_size, Image.Resampling.LANCZOS)
    # print('уменьшили')

    # 2. Возвращаем размер обратно
    # Убедимся, что `size` - это кортеж, а не список
    original_size_tuple = tuple(size)
    blurred = small.resize(original_size_tuple, Image.Resampling.BICUBIC)
    # print('вернули размер обратно')

    # 3. Дополнительный Gaussian Blur (склеивает переходы)
    blurred = blurred.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    # print('гаусс блюр')

    blurred.save(output_path, quality=95)
    # print('сохранили')


def create_img(quote, title, artist, cover_path, user_id):
    # сначала считаем строчки
    # потом блюрим обложку с cover_blured_{user_id}.png
    # и наконец рисуем картинку
    # обрезаем заблюренную обложку по нужной высоте
    # добавляем легкое затемнение
    # ещё одно легкое затемнение снизу
    # добавляем цитату, название трека и автора
    # пока что всё

    width, height = 1000, 545

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    font_quote = ImageFont.truetype('../Inter/Inter-SemiBold.otf', 54)  # Для цитаты (большой шрифт)
    font_title = ImageFont.truetype('../Inter/Inter-Medium.otf', 36)  # Для трека и автора
    font_author = ImageFont.truetype('../Inter/Inter-Regular.otf', 32)
    # font_time = ImageFont.truetype('Inter-V.ttf', 40)

    x = 140
    y = 140

    # Параметры для цитаты
    max_width = 600  # максимальная ширина текста в пикселях (подгони под свой блок)
    line_spacing = 65  # расстояние между строками (можно 80–100)

    lines = []

    for i in range(len(quote)):

        words = quote[i].split(' ')  # разбиваем на слова
        print('1.0', quote)
        print('1.1', words)
        current_line = ""

        for word in words:
            # Пробуем добавить слово к текущей строке
            test_line = current_line + (" " if current_line else "") + word
            # Считаем ширину тестовой строки
            bbox = draw.textbbox((0, 0), test_line, font=font_quote)
            # txtlen = draw.textlength(test_line, font=font_quote)
            print('2.', test_line, bbox)
            line_width = bbox[2] - bbox[0]

            if line_width <= max_width:
                current_line = test_line
            else:
                # Если не влезает — сохраняем текущую строку и начинаем новую
                if current_line:
                    lines.append(current_line)
                current_line = word

        # добавляем последнюю строку
        if current_line:
            lines.append(current_line)

        if i != len(quote) - 1:
            height += 20
        print(lines)

    height += (len(lines) - 1) * 65

    bg = Image.new("RGB", (width, height), (30, 30, 30))  # это темно-серый фон

    # content_bg = # тут овальчик предполагается заблюренный

    # Создаём полупрозрачный оверлей (тёмный прямоугольник с закруглениями)
    # почему-то это просто прозрачный кусок чего-то
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    radius = 50

    # 1. Создаём и сохраняем заблюренную обложку
    cover_blured = f"img/cover_blured_{user_id}.png"
    create_blur(cover_path, cover_blured, [width - 200, height - 200])

    # делаем тень???

    shadow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)

    rect_x, rect_y = 100, 100
    rect_w, rect_h = width - 200, height - 200

    shadow_draw.rounded_rectangle((rect_x-15, rect_y-15, rect_x + rect_w+15, rect_y + rect_h+15), radius=radius, fill=(0, 0, 0, 100))

    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=15))
    bg = Image.alpha_composite(bg.convert("RGBA"), shadow_layer)
    # bg.alpha_composite(shadow_layer)


    # 2. Открываем заблюренную обложку и вставляем её на основной фон

    blured_img = Image.open(cover_blured)

    # Создаём маску с закруглёнными углами
    mask = Image.new("L", blured_img.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, blured_img.width, blured_img.height), radius=radius, fill=255)

    # Вставляем заблюренную картинку, используя маску для закругления
    bg.paste(blured_img, (100, 100), mask)
    blured_img.close() # Закрываем файл после использования

    # 3. Рисуем затемняющий прямоугольник поверх заблюренной картинки
    rect_x, rect_y = 100, 100
    rect_w, rect_h = width - 200, height - 200
    draw.rounded_rectangle(
        (rect_x, rect_y, rect_x + rect_w, rect_y + rect_h),
        radius=radius,
        fill=(0, 0, 0, 50)  # легкое затемнение
    )

    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

    # 4. Рисуем затемняющий прямоугольник для автора и названия
    # должна быть фиксированная высота 200 px и фиксированная ширина 800 px
    rect_x = 100
    rect_y = height - 300
    rect_w, rect_h = width - 200, 200
    draw.rounded_rectangle(
        (rect_x, rect_y, rect_x + rect_w, rect_y + rect_h),
        radius=radius,
        fill=(0, 0, 0, 128),  # полупрозрачный чёрный
        corners=(False, False, True, True)
    )

    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

    # 5 mini cover
    cover_mini = Image.open(cover_path)
    cover_mini = cover_mini.resize((120, 120), Image.Resampling.LANCZOS)

    mask = Image.new("L", cover_mini.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, cover_mini.width, cover_mini.height), radius=30, fill=255)

    # Вставляем заблюренную картинку, используя маску для закругления
    bg.paste(cover_mini, (740, height-140-120), mask)
    cover_mini.close()  # Закрываем файл после использования

    draw = ImageDraw.Draw(bg)

    # отрисовка цитаты
    for line in lines:
        draw.text((x, y), line, font=font_quote, fill="white")
        # print(line[-1:])
        if line[-1:] == '\n' and line != lines[-1]:
            y += 20
        y += line_spacing

    # # Разбиваем цитату на строки по ширине (Pillow умеет это сам, но textwrap проще)
    # wrapped_lines = textwrap.wrap(quote, width=35)  # 35–40 символов — хорошее значение
    #
    # # Вычисляем высоту, которую займёт цитата
    # quote_height = len(wrapped_lines) * line_spacing
    #
    # # Центрируем цитату вертикально внутри блока
    # # (можно подвинуть выше/ниже, изменив 300)
    # quote_y = (height - quote_height) // 2 - 50  # -50 — чтобы оставить место для трека снизу
    #
    # # Рисуем каждую строку
    # for line in wrapped_lines:
    #     # Вычисляем ширину строки и центрируем по горизонтали
    #     bbox = draw.textbbox((0, 0), line, font=font_quote)
    #     text_width = bbox[2] - bbox[0]
    #     x = (width - text_width) // 2
    #
    #     # Можно добавить обводку (stroke) для лучшей читаемости на тёмном фоне
    #     draw.text((x, quote_y), line, font=font_quote, fill="black")
    #
    #     quote_y += line_spacing
    # ######

    # Трек и исполнитель
    title_text = f"{title}"
    artist_text = f"{artist}"

    x = 140
    y_bottom = height - 216 - 50

    # Трек и исполнитель
    draw.text((x, y_bottom), title_text, font=font_title, fill="white")
    draw.text((x, y_bottom + 44), artist_text, font=font_author, fill="white")
    draw.text((x, y_bottom + 44 + 44 + 3), "@sq_Liss", font=font_author, fill="gray")

    output_file = "img/quote_" + str(user_id) + ".png"

    bg = bg.convert("RGB")
    bg.save(output_file, quality=95)

    return output_file