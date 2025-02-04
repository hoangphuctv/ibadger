md dist
pyinstaller --icon=app.ico --noconsole --onedir ibadger.py
copy app.ico dist\ibadger
copy app.png dist\ibadger