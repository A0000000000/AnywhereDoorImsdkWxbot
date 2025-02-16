import log
import server
import wxbot


def main():
    log_ctx = log.create_log_ctx()
    wxbot.init(log_ctx)
    server.init_http_server(log_ctx,
                            wxbot.send_msg_to_admin,
                            wxbot.GEWE_CONFIG,
                            wxbot.check_online_status,
                            wxbot.init_inner)


if __name__ == '__main__':
    main()
