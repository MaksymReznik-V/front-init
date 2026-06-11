Build Docker image
docker build -t front-init .

Run Docker container
docker run -p 3000:3000 -p 5000:5000/udp -v ${PWD}/storage:/front-init/storage front-init