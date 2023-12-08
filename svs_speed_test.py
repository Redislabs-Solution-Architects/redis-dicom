from redis import asyncio as aioredis
import asyncio
from openslide import OpenSlide
import os
import glob
from argparse import ArgumentParser
from time import perf_counter
import filecmp

MAX_CONNECTIONS = 10000
CHUNK_SIZE = 5
INPUT_DIR = './largeFile_in'
OUTPUT_DIR = './largeFile_out'
REDIS_URL  = 'redis://default:redis@localhost:12000'

async def load_chunks(client, key, file, chunk_size):
    i = 0
    chunk_keys = []
    with open(file, 'rb') as infile:
        while chunk := infile.read(chunk_size):
            chunk_key = f'chunk:{key}:{i}'
            await client.set(chunk_key, chunk)
            chunk_keys.append(chunk_key)
            i += 1
    return chunk_keys

async def load_data(client, chunk_size):
    await client.flushdb()
    count = 0
    keys = []
    for file in glob.glob(f'{INPUT_DIR}/*.svs'):
        print(f'{os.path.basename(file)} Size: {round(os.path.getsize(file)/2**20, 2)} MB')
        slide = OpenSlide(file)
        key = f'file:{os.path.basename(file)}'
        keys.append(key)
        image_name = os.path.basename(file)
        dimensions = slide.dimensions
        level_count = slide.level_count
        chunk_keys = await load_chunks(client, key, file, chunk_size)

        await client.json().set(key, '$', {
            'imageName': image_name, 
            'dimensions': dimensions,
            'levelCount': level_count,
            'chunks': chunk_keys 
        })
        count += 1
    print(f'Files loaded: {count}')
    return keys

async def get_bytes_async(client, chunks, max_connections):
    tasks = []
    connections = 0
    results = []
    for chunk in chunks:
        tasks.append(client.get(chunk))
        connections += 1
        if connections == max_connections:
            results.extend(await asyncio.gather(*tasks))
            connections = 0
            tasks = []
    results.extend(await asyncio.gather(*tasks))
    return b''.join(results)
    
async def async_test(client, chunk_size, max_connections):
    keys = await load_data(client, chunk_size)
    total = 0
    for key in keys:
        t1 = perf_counter()
        results = await client.json().get(key, '$.chunks')
        total_bytes = await get_bytes_async(client, results[0], max_connections)
        t2 = perf_counter()
        exec_time = round((t2-t1)*1000,2)
        total += exec_time
        print(f'\nKey: {key}')
        print(f'Exec time: {exec_time} ms')
        print(f'Bytes Retrieved: {len(total_bytes)}')
        file = key.split(':')[-1]
        with open(os.path.join(OUTPUT_DIR, file), 'wb') as outfile:
            outfile.write(total_bytes)
        if filecmp.cmp(os.path.join(INPUT_DIR, file), os.path.join(OUTPUT_DIR, file), shallow=False):
            print('File integrity check:  Pass')
        else:
            print('File integrity check:  Fail')
    print(f'\nTotal time: {round(total,2)} ms')

if __name__ == '__main__':
    parser = ArgumentParser(description='Image fetch speed test')
    parser.add_argument('--url', required=False, type=str, default=REDIS_URL,
        help='Redis URL connect string')
    parser.add_argument('--chunk_size', required=False, type=int, default=CHUNK_SIZE,
        help='File chunk size in KB')
    parser.add_argument('--connections', required=False, type=int, default=MAX_CONNECTIONS,
        help='Number of Redis client connections')
    args = parser.parse_args()
    chunk_size = args.chunk_size * 1024

    # asynchronous retrieval test
    print(f'\n*** File Retrieval Test - {args.chunk_size} KB Chunks, {args.connections} Client Connections ***')
    async_client = aioredis.from_url(args.url)
    asyncio.run(async_test(async_client, chunk_size, args.connections))