import server
import wxbot


def main():
    wxbot.init()
    server.init_http_server(wxbot.send_msg_to_admin, wxbot.GEWE_CONFIG, wxbot.check_online_status, wxbot.init_inner)


if __name__ == '__main__':
    main()
