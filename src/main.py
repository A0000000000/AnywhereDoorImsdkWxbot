import os
import constant
import server
import wxbot


def main():
    if not (os.path.exists(constant.SESSION_DIR) and os.path.isdir(constant.SESSION_DIR)):
        if os.path.exists(constant.SESSION_DIR):
            os.remove(constant.SESSION_DIR)
        os.mkdir(constant.SESSION_DIR)
    wxbot.init()
    server.init_http_server(wxbot.send_msg_to_admin, wxbot.GEWE_CONFIG)


if __name__ == '__main__':
    main()
