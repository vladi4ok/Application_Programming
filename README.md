# Variant - 1

py -3.8 -m venv venv

venv/Scripts/activate

pip install -r requirements.txt

waitress-serve --host 127.0.0.1 --port=5000 --call "main:create_app"
