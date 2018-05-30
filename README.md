# kubehub
Find kubernetes related GitHub repositories

## Deploying for Development

To deploy in a development environment:

```bash
git clone https://github.com/mattburgess/kubehub
python3 -m venv kubehub
cd kubehub
source bin/activate
pip3 install -r requirements.txt
```

You'll also need to have the redis server installed locally and have it listen
on its default port of 6379.

To run the built-in HTTP server, run the following from within the top-level
`kubehub` directory:

```bash
export FLASK_APP=kubehub/kubehub.py
flask run
```

At this point, you should be able to hit http://localhost:5000/api/kubernetes
from your web browser.

## Deploying to a Production Environment

It's recommended to deploy kubehub using Docker in production environments.  To
do this, simply:

```bash
git clone https://github.com/mattburgess/kubehub
cd kubehub
docker-compose up
```

By default, the API will be available on port `5000` on all network interfaces.

To test that kubehub is working correctly, simply point your web browser at
http://your_docker_host:5000/api/kubernetes
