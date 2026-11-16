from pyscript import document
from pyscript.ffi import create_proxy
import json
import js

async def post_request(url, parameter):
    r = await js.axios.post(url, parameter)
    return [r.data, r.status, r.statusText]

async def get_request(url):
    r = await js.axios.get(url)
    return [r.data, r.status, r.statusText]

async def put_request(url, parameter):
    r = await js.axios.put(url, parameter)
    return [r.data, r.status, r.statusText]

async def delete_request(url):
    r = await js.axios.delete(url)
    return [r.data, r.status, r.statusText]


# ==========================================================
# TODO 1: 사용자가 선택한 라디오 버튼(#HTTP-1, #HTTP-2, #HTTP-3)에 따라
#         알맞은 서버 주소를 반환하도록 빈칸(___)을 채우세요!
#   - #HTTP-1 체크 시: 'http://127.0.0.1:8000/membership_api/'
#   - #HTTP-2 체크 시: 'https://127.0.0.1:8000/membership_api/'
#   - 그 외(#HTTP-3):  'https://127.0.0.1:4433/membership_api/'
# ==========================================================
def get_http_url():
    if document.querySelector("#HTTP-1").checked:
        return 'http://127.0.0.1:8000/membership_api/'
    elif document.querySelector("#HTTP-2").checked:
        return 'https://127.0.0.1:8000/membership_api/'
    else:
        return 'https://127.0.0.1:4433/membership_api/'


async def do_create_by_post(evt):
    k = document.getElementById("key_create").value
    v = document.getElementById("value_create").value
    url = get_http_url() + str(k)
    content = json.dumps({str(k): str(v)})

    document.getElementById("key_create").value = ''
    document.getElementById("value_create").value = ''

    res = await post_request(url, content)
    display_msg(f"HTTP POST {url} with {content}", f"{res[1]} {res[2]} - {res[0]}")

async def do_read_by_get(evt):
    k = document.getElementById("key_read").value
    url = get_http_url() + str(k)
    document.getElementById("key_read").value = ''

    res = await get_request(url)
    display_msg(f"HTTP GET {url}", f"{res[1]} {res[2]} - {res[0]}")

async def do_update_by_put(evt):
    k = document.getElementById("key_update").value
    v = document.getElementById("value_update").value
    url = get_http_url() + str(k)
    content = json.dumps({str(k): str(v)})

    document.getElementById("key_update").value = ''
    document.getElementById("value_update").value = ''

    res = await put_request(url, content)
    display_msg(f"HTTP PUT {url} with {content}", f"{res[1]} {res[2]} - {res[0]}")

async def do_delete_by_delete(evt):
    k = document.getElementById("key_delete").value
    url = get_http_url() + str(k)
    document.getElementById("key_delete").value = ''

    res = await delete_request(url)
    display_msg(f"HTTP DELETE {url}", f"{res[1]} {res[2]} - {res[0]}")

def display_msg(req_text, res_text):
    document.getElementById("out_request").innerText = req_text
    document.getElementById("out_response").innerText = res_text

if __name__ == '__main__':
    document.getElementById("submit_create").addEventListener("click", create_proxy(do_create_by_post))
    document.getElementById("submit_read").addEventListener("click", create_proxy(do_read_by_get))
    document.getElementById("submit_update").addEventListener("click", create_proxy(do_update_by_put))
    document.getElementById("submit_delete").addEventListener("click", create_proxy(do_delete_by_delete))

    document.getElementById("program_status_1").innerText = 'Please fill key/value and execute menu :'
    document.getElementById("program_status_2").innerText = 'READY'