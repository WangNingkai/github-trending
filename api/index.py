import os
import sys

from sanic import Sanic, response

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

try:
    from spider import DEVELOPER, REPOSITORY, get_trending
except:
    raise

app = Sanic("GitHub Trending")


@app.route("/")
async def index(request):
    return response.html("<h3>Hello GitHub Trending!</h3>")


@app.route("/repo")
async def repositoryHandler(request):
    result = trending(REPOSITORY, request)
    return response.json(result)


@app.route("/developer")
async def developerHandler(request):
    result = trending(DEVELOPER, request)
    return response.json(result)


def trending(url, request):
    lang = request.args.get("lang", None)
    since = request.args.get("since", None)
    if lang is not None:
        lang = lang.replace("-shuo", "%23")
        url += lang
    params = None
    if since is not None:
        params = {"since": since}
    result = get_trending(url=url, params=params)
    return result


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False, access_log=False)
