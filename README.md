Running a Python runtime in Docker:
```
docker run -i -t --rm --name lehm-madu-uss -v /home/k6ps/windows_user_home/projects/maze-solver-simulator:/app python:3.8-alpine3.10 /bin/bash
```
Running unit tests in container:
```
cd /app
python -m unittest discover -v
```
