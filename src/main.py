import server
import wxbot


def main():
    server.init_http_server(wxbot.send_msg_to_admin)
    wxbot.init(server.send_request)


if __name__ == '__main__':
    main()
