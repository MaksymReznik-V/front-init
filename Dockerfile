FROM python:3.14

LABEL authors="Max"

WORKDIR /front-init

COPY . .

EXPOSE 3000

EXPOSE 5000/udp

CMD ["python", "main.py"]




