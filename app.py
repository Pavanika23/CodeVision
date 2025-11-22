# app.py
from pywebio.input import *
from pywebio.output import *
from pywebio.platform.flask import webio_view as pywebio_webio_view
from pywebio import session
from flask import Flask
import argparse
from menu import Menu
import os

mymenu = Menu()  # obj of class Menu

app = Flask(__name__)

def _load_image_bytes(path):
    """Return bytes if file exists else None (prevents import-time crashes)."""
    try:
        with open(path, 'rb') as f:
            return f.read()
    except Exception:
        return None

def show_main_menu():
    """Main PyWebIO app entrypoint"""
    # load images at runtime (safer on WSGI import)
    header_img = _load_image_bytes(os.path.join('images', 'header.jpg'))
    exit_img = _load_image_bytes(os.path.join('images', 'exit.png'))

    session.set_env(title='CodeVision', output_animation=False)

    mymenu.user = None
    while mymenu.user != 4:  # end program when option 4 i.e. exit portal is selected.
        mymenu.login()
        if mymenu.user == 2:
            mymenu.menu_for_student()
        elif mymenu.user == 3:
            mymenu.menu_for_admin()

    with use_scope('ROOT'):
        if header_img:
            put_image(header_img, width='100%', height='50px', position=0)
        else:
            put_html("<h3>Header image not found</h3>")

        put_html("<br>")
        put_html("<br>")

        if exit_img:
            put_image(exit_img, width='100%', height='420px')
        else:
            put_html("<p>(Exit image not found)</p>")

        put_info("Thank you for visiting our site.", position=1)
        clear("main")


# Register the PyWebIO view with Flask WSGI (this is what PythonAnywhere will call).
# We expose the app object above so the WSGI file can import it: `from app import app as application`
app.add_url_rule(
    '/tool',                          # URL path you want to serve on (your previous value)
    'webio_view',                     # endpoint name
    pywebio_webio_view(show_main_menu),  # wrap the PyWebIO function
    methods=['GET', 'POST', 'OPTIONS']
)

# ---------------- Development convenience (optional) ----------------
# Keep this block commented in production. Only use locally for quick testing.
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-p", "--port", type=int, default=8080)
#     args = parser.parse_args()
#     from pywebio import start_server
#     start_server(show_main_menu, port=args.port, websocket_ping_interval=60)
#
# # visit http://localhost:8080/tool to open the application locally
