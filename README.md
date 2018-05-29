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

To run the built-in HTTP server, run the following from within the top-level
`kubehub` directory:

```bash
export FLASK_APP=kubehub/kubehub.py
flask run
```

At this point, you should be able to hit http://localhost:5000/api/kubernetes
from your web browser.

## Deploying to a Production Environment

TODO
