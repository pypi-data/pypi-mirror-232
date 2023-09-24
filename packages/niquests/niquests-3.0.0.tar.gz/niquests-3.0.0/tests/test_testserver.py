from __future__ import annotations

import socket
import threading
import time

import pytest

import niquests
from tests.testserver.server import Server


class TestTestServer:
    def test_basic(self):
        """messages are sent and received properly"""
        question = b"success?"
        answer = b"yeah, success"

        def handler(sock):
            text = sock.recv(1000)
            assert text == question
            sock.sendall(answer)

        with Server(handler) as (host, port):
            sock = socket.socket()
            sock.connect((host, port))
            sock.sendall(question)
            text = sock.recv(1000)
            assert text == answer
            sock.close()

    def test_server_closes(self):
        """the server closes when leaving the context manager"""
        with Server.basic_response_server() as (host, port):
            sock = socket.socket()
            sock.connect((host, port))

            sock.close()

        with pytest.raises(socket.error):
            new_sock = socket.socket()
            new_sock.connect((host, port))

    def test_text_response(self):
        """the text_response_server sends the given text"""
        server = Server.text_response_server(
            "HTTP/1.1 200 OK\r\n" "Content-Length: 6\r\n" "\r\nroflol"
        )

        with server as (host, port):
            r = niquests.get(f"http://{host}:{port}")

            assert r.status_code == 200
            assert r.text == "roflol"
            assert r.headers["Content-Length"] == "6"

    def test_invalid_location_response(self):
        server = Server.text_response_server(
            "HTTP/1.1 302 PERMANENT-REDIRECTION\r\n"
            "Location: http://localhost:1/search/?q=ïðåçèäåíòû+ÑØÀ\r\n\r\n"
        )

        with server as (host, port):
            with pytest.raises(niquests.exceptions.ConnectionError) as exc:
                niquests.get(f"http://{host}:{port}")
            msg = exc.value.args[0].args[0]
            assert (
                "/search/?q=%C3%AF%C3%B0%C3%A5%C3%A7%C3%A8%C3%A4%C3%A5%C3%AD%C3%B2%C3%BB+%C3%91%C3%98%C3%80"
                in msg
            )

    def test_basic_response(self):
        """the basic response server returns an empty http response"""
        with Server.basic_response_server() as (host, port):
            r = niquests.get(f"http://{host}:{port}")
            assert r.status_code == 200
            assert r.text == ""
            assert r.headers["Content-Length"] == "0"

    def test_basic_waiting_server(self):
        """the server waits for the block_server event to be set before closing"""
        block_server = threading.Event()

        with Server.basic_response_server(wait_to_close_event=block_server) as (
            host,
            port,
        ):
            sock = socket.socket()
            sock.connect((host, port))
            sock.sendall(b"send something")
            time.sleep(2.5)
            sock.sendall(b"still alive")
            block_server.set()  # release server block

    def test_multiple_requests(self):
        """multiple requests can be served"""
        requests_to_handle = 5

        server = Server.basic_response_server(requests_to_handle=requests_to_handle)

        with server as (host, port):
            server_url = f"http://{host}:{port}"
            for _ in range(requests_to_handle):
                r = niquests.get(server_url)
                assert r.status_code == 200

            # the (n+1)th request fails
            with pytest.raises(niquests.exceptions.ConnectionError):
                r = niquests.get(server_url)

    @pytest.mark.skip(reason="this fails non-deterministically under pytest-xdist")
    def test_request_recovery(self):
        """can check the requests content"""
        # TODO: figure out why this sometimes fails when using pytest-xdist.
        server = Server.basic_response_server(requests_to_handle=2)
        first_request = b"put your hands up in the air"
        second_request = b"put your hand down in the floor"

        with server as address:
            sock1 = socket.socket()
            sock2 = socket.socket()

            sock1.connect(address)
            sock1.sendall(first_request)
            sock1.close()

            sock2.connect(address)
            sock2.sendall(second_request)
            sock2.close()

        assert server.handler_results[0] == first_request
        assert server.handler_results[1] == second_request

    def test_requests_after_timeout_are_not_received(self):
        """the basic response handler times out when receiving requests"""
        server = Server.basic_response_server(request_timeout=1)

        with server as address:
            sock = socket.socket()
            sock.connect(address)
            time.sleep(1.5)
            sock.sendall(b"hehehe, not received")
            sock.close()

        assert server.handler_results[0] == b""

    def test_request_recovery_with_bigger_timeout(self):
        """a biggest timeout can be specified"""
        server = Server.basic_response_server(request_timeout=3)
        data = b"bananadine"

        with server as address:
            sock = socket.socket()
            sock.connect(address)
            time.sleep(1.5)
            sock.sendall(data)
            sock.close()

        assert server.handler_results[0] == data

    def test_server_finishes_on_error(self):
        """the server thread exits even if an exception exits the context manager"""
        server = Server.basic_response_server()
        with pytest.raises(Exception):
            with server:
                raise Exception()

        assert len(server.handler_results) == 0

        # if the server thread fails to finish, the test suite will hang
        # and get killed by the jenkins timeout.

    def test_server_finishes_when_no_connections(self):
        """the server thread exits even if there are no connections"""
        server = Server.basic_response_server()
        with server:
            pass

        assert len(server.handler_results) == 0

        # if the server thread fails to finish, the test suite will hang
        # and get killed by the jenkins timeout.
