# Requirements

```bash
pip install quart quart-cors aiosqlite aiofiles
```


### Working

This application allows users to upload files and updates the file metadata over websockets. 
File uploaded by one user will be broadcasted to all the connected users in realtime over websockets


### Scope of Improvements

* Allow users to Collaborate download the uploaded file [Over HTTP] (Straightforward)
* For collaboration on uploaded files in realtime (Like Google Docs). To start with we can limit the number of file types supported (for e.g. Only .txt and .docx).
* Use a WYSIWYG use ```yjs``` and ```Quill``` for frontend and quart can handle the backend for it. 