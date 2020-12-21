import time
from io import BytesIO

from selenium import webdriver
from PIL import Image, ImageChops, ImageDraw
# https://pillow.readthedocs.io/

from root.core import Browsers, FOLDER_SCREENSHOTS_SOURCES, FOLDER_SCREENSHOTS_COMPARED


def _full_screenshot_old(browser: webdriver, offset: int = 0) -> Image:
    """ Получение полного скриншота содержимого окна браузера
        offset - начальное смещение"""

    img_list = []  # для хранения фрагментов изображения

    # Определение размера окна браузера
    height = browser.execute_script("""return Math.max(
                                           document.documentElement.clientHeight,
                                           window.innerHeight
                                       );""")

    # Определение высоты содержимого окна браузера
    max_window_height = browser.execute_script("""return Math.max(
                                                      document.body.scrollHeight,
                                                      document.body.offsetHeight,
                                                      document.documentElement.clientHeight,
                                                      document.documentElement.scrollHeight,
                                                      document.documentElement.offsetHeight
                                                  );""")

    # Скроллим страницу и добавляем скриншот видимого окна браузера в img_list
    while offset < max_window_height:
        time.sleep(1)
        browser.execute_script(f"window.scrollTo(0, {offset});")

        img = Image.open(BytesIO((browser.get_screenshot_as_png())))
        img_list.append(img)

        offset += height

    # Обрезание последнего изображения
    box = (0, height - height * (max_window_height / height - max_window_height // height), img_list[-1].size[0],
           img_list[-1].size[1])
    img_list[-1] = img_list[-1].crop(box)

    # Определение размеров нового изображения, создание холста
    img_frame_height = sum([img_frag.size[1] for img_frag in img_list])
    img_frame = Image.new('RGB', (img_list[0].size[0], img_frame_height))

    # Объединение изображений в одно
    offset = 0
    for img_fragment in img_list:
        img_frame.paste(img_fragment, (0, offset))
        offset += img_fragment.size[1]

    return img_frame


def element_screenshot(browser: webdriver, location: str = "//body") -> Image:
    """ Получение скриншота вебэлемента на старнице.
        Если location не зада, снимается скриншот всего окна браузера (элемент body) """

    image = Image.open(BytesIO(browser.find_element_by_xpath(location).screenshot_as_png))

    image_new = Image.new("RGB", image.size)
    image_new.paste(image)

    return image_new


def compare_images(image_1: Image, image_2: Image,
                   marked_image: bool = False, marked_color: tuple = (255, 0, 0)) -> list:
    """ Сравниваем полученные изображения и возвращаем результирующее изображение """

    # Одинаковые участки закрашиваются черным
    result = [ImageChops.difference(image_1, image_2)]

    # Два различных пикселя заменить на marked_color (по умолчанию: красный)
    if marked_image:
        image_copy = ImageChops.duplicate(image_1)

        # Создаем холст
        draw = ImageDraw.Draw(image_copy)
        width, height = image_copy.size

        # Выгружаем значения пикселей
        pixels_1 = image_copy.load()
        pixels_2 = image_2.load()

        for x in range(width):
            for y in range(height):
                result_pixel = pixels_1[x, y] if pixels_1[x, y] == pixels_2[x, y] else marked_color

                draw.point((x, y), result_pixel)

        result.append(image_copy)

    return result


def save_images(sources: list = None, compared: list = None, page: str = "", browser: str = Browsers.DEFAULT) -> None:
    """ Сохранение изображений """

    name = "%folder%/{time}-%number%-{page}-{browser}.png".format(time=int(time.time()),
                                                                  page=page.replace("/", "_"),
                                                                  browser=browser)

    if sources:
        for index, image in enumerate(sources):
            image.save(name.replace("%folder%", FOLDER_SCREENSHOTS_SOURCES).replace("%number%", str(index)))

    if compared:
        for index, image in enumerate(compared):
            image.save(name.replace("%folder%", FOLDER_SCREENSHOTS_COMPARED).replace("%number%", str(index)))
