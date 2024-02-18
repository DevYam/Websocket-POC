from quart import Quart, request, jsonify, websocket, render_template
import os
import aiosqlite
import datetime
import aiofiles

app = Quart(__name__)

UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_FILE = 'file_metadata.db'

# A set to keep track of active WebSocket connections
active_websockets = set()


async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                size INTEGER NOT NULL,
                upload_time TEXT NOT NULL
            )
        ''')
        await db.commit()


@app.before_serving
async def before_serving():
    await init_db()


@app.route('/upload', methods=['POST'])
async def upload_file():
    files = await request.files
    file = files.get('file')
    if file and file.filename:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        async with aiofiles.open(filepath, 'wb') as f:
            content = file.read()  # Directly read without await
            await f.write(content)  # Asynchronously write to the file
        file_size = os.path.getsize(filepath)
        upload_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute('INSERT INTO files (name, size, upload_time) VALUES (?, ?, ?)', (filename, file_size, upload_time))
            await db.commit()
        await send_files_to_all_websockets()  # Notify all WebSocket connections
        return jsonify({'message': 'File uploaded successfully', 'filename': filename})
    return jsonify({'message': 'No file uploaded'}), 400



async def send_files_to_all_websockets():
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute('SELECT name, size, upload_time FROM files ORDER BY upload_time DESC')
        files = await cursor.fetchall()
        for ws in active_websockets:
            await ws.send_json({'files': files})


@app.websocket('/ws')
async def ws():
    active_websockets.add(websocket._get_current_object())
    try:
        # Immediately send the current list of files upon connection
        await send_files_to_all_websockets()

        while True:
            await websocket.receive()
            # The loop is kept alive to listen for any messages. You may not need to send anything here.
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        active_websockets.remove(websocket._get_current_object())


@app.route('/')
async def index():
    return await render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
