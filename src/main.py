import server
import wxbot


def main():
    wxbot.init()
    server.init_http_server(wxbot.send_msg_to_admin, wxbot.GEWE_CONFIG)


if __name__ == '__main__':
    main()
