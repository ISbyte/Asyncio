import asyncio
import aiohttp
from time import time
import requests
from PIL import Image, ImageOps
import logging


def transpose(data):
    filename = 'img/file-{}.jpeg'.format(int(time() * 1000))
    with open(filename, 'wb') as file:
        file.write(data)
    image = ImageOps.mirror(Image.open('{}'.format(filename)))
    return image
    

async def post_content(url, session, image):
    try:
        response = await session.post(url, data=image.tobytes())
        assert response.status == 200
    except AssertionError:
        print("POST_ERROR: {}".format(response.status))


async def fetch_content(url, session):
    try:
        async with session.get(url) as response:
            data = await response.content.read()
            assert response.status == 200
            image = transpose(data)
            await post_content(url, session, image)
    except AssertionError:
        print('GET ERROR: {}'.format(response.status))
    


async def main(urls):
    tasks = list()
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(fetch_content(url, session))
            tasks.append(task)
        await asyncio.gather(*tasks)


def sync(urls):
    for url in urls:
        try:
            response_get = requests.get(url)
            assert response_get.status_code == 200
            data = response_get.content
            image = transpose(data)
            response_post = requests.post(url, data=image.tobytes())
            assert response_post.status_code == 200
        except AssertionError:
            print('AssertionError')


if __name__ == "__main__":
    content = requests.get('http://142.93.138.114/images/').content
    images = content.split(b'\n')
    urls = ['http://142.93.138.114/images/{}'.format(image.decode('utf-8')) for image in images]
    start = time()
    asyncio.run(main(urls))
    print(time() - start)
    start = time()
    sync(urls)
    print(time() - start)

