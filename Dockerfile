FROM python:3.8

WORKDIR /projects

COPY . .

EXPOSE 5001

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]