import os
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.types import Receive, Scope, Send
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.environ.get("STATIC_ROOT", os.path.join(ROOT, "htdocs"))
STATIC_URL = "/"

# HTML과 PyScript 파일을 서빙할 템플릿 폴더 지정
templates = Jinja2Templates(directory=os.path.join(ROOT, "templates"))

# 1. 웹 브라우저가 첫 화면("/")에 접속했을 때 HTML 파일 보내주기
async def homepage(request):
    return templates.TemplateResponse(request, "client_pyscript.html")

# 2. 웹 브라우저가 파이썬 클라이언트 코드("/wasm/client_main.py")를 요청했을 때 보내주기
async def wasm_python_code(request):
    return templates.TemplateResponse(request, "client_main.py")


# ==========================================================
# 인메모리 데이터베이스 (Key: Value 저장소)
# ==========================================================
db = {}

# [CREATE] HTTP POST 요청 처리
async def do_POST(request):
    print(">> do_POST() activated")
    content = await request.json()  # 비동기로 JSON 바디를 한 번에 파싱!

    key = list(content.keys())[0]
    value = list(content.values())[0]

    # TODO 1: key가 이미 db에 있으면 'CREATE rejected',
    #         없으면 db[key] = value 저장 후 'CREATE accepted'를 res_text에 담으세요!
    if key in db:
        print(f":: CREATE {key}:{value} rejected")
        res_text = "create rejected"
    else:
        db[key] = value
        print(f":: CREATE {key}:{value} created")
        res_text = "create accepted"

    return Response(res_text, media_type=request.headers.get("content-type"))


# [READ] HTTP GET 요청 처리
async def do_GET(request):
    print(">> do_GET() activated")
    key = request.path_params["key"]  # URL 경로(/membership_api/{key})에서 바로 추출!

    # TODO 2: key가 db에 있으면 f"READ accepted for < {key} : {db[key]} >",
    #         없으면 'READ rejected'를 res_text에 담으세요!
    if key in db:
        print(f":: READ {key}:{db[key]} completed")
        res_text = f"Read accepted for << {key}: {db[key]}>>"
    else:
        print(f":: READ {key} rejected")
        res_text = "read rejected"

    return Response(res_text, media_type=request.headers.get("content-type"))


# [UPDATE] HTTP PUT 요청 처리
async def do_PUT(request):
    print(">> do_PUT() activated")
    content = await request.json()

    key = list(content.keys())[0]
    value = list(content.values())[0]

    # TODO 3: key가 db에 있으면 db[key] = value 수정 후 'UPDATE completed',
    #         없으면 'UPDATE rejected'를 res_text에 담으세요!
    if key in db:
        db[key] = value
        print(f":: UPDATE {key}:{value} completed")
        res_text = "update completed"
    else:
        print(f":: UPDATE {key}:{value} rejected")
        res_text = "update rejected"

    return Response(res_text, media_type=request.headers.get("content-type"))


# [DELETE] HTTP DELETE 요청 처리
async def do_DELETE(request):
    print(">> do_DELETE() activated")
    key = request.path_params["key"]

    # TODO 4: key가 db에 있으면 del db[key] 삭제 후 'DELETE accepted',
    #         없으면 'DELETE rejected'를 res_text에 담으세요!
    if key in db:
        del db[key]
        print(f":: DELETE {key} completed")
        res_text = "delete accepted"
    else:
        print(f":: DELETE {key} rejected")
        res_text = "delete rejected"

    return Response(res_text, media_type=request.headers.get("content-type"))


# CORS 미들웨어 설정 (이전 2탄에서 수동으로 헤더 넣던 것을 한 방에 해결!)
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

# 라우팅 테이블 (URL 주소와 함수를 연결)
starlette = Starlette(
    routes=[
        Route("/", homepage),
        Route("/wasm/client_main.py", wasm_python_code),
        Route("/membership_api/{key:str}", do_GET),
        Route("/membership_api/{key:str}", do_POST, methods=["POST"]),
        Route("/membership_api/{key:str}", do_PUT, methods=["PUT"]),
        Route("/membership_api/{key:str}", do_DELETE, methods=["DELETE"]),
        Mount(STATIC_URL, StaticFiles(directory=STATIC_ROOT, html=True)),
    ],
    middleware=middleware
)

# Hypercorn ASGI 서버가 실행할 진입점 함수
async def run(scope: Scope, receive: Receive, send: Send) -> None:
    await starlette(scope, receive, send)