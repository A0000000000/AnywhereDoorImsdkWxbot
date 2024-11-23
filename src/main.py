import rpc
import wxbot


def main():
    rpc.init_rpc_server(wxbot.send_msg_to_admin)
    wxbot.init(rpc.send_request)


if __name__ == '__main__':
    main()
