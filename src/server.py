from pathlib import Path
import socket


HOST = "127.0.0.1"
PORT = 8080
SITE_DIR = Path(__file__).resolve().parent.parent / "site"


def build_response(status: str, body: bytes, content_type: str = "text/html; charset=utf-8") -> bytes:
    headers = [
        f"HTTP/1.1 {status}",
        f"Content-Length: {len(body)}",
        f"Content-Type: {content_type}",
        "Connection: close",
        "",
        "",
    ]
    return "\r\n".join(headers).encode("utf-8") + body


def get_file(path: str) -> tuple[str, bytes, str]:
    if path == "/":
        path = "/index.html"

    safe_path = path.lstrip("/")
    file_path = (SITE_DIR / safe_path).resolve()

    if not str(file_path).startswith(str(SITE_DIR.resolve())) or not file_path.exists():
        return "404 Not Found", b"<h1>404 Not Found</h1>", "text/html; charset=utf-8"

    suffix = file_path.suffix.lower()
    content_type = {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
    }.get(suffix, "application/octet-stream")

    return "200 OK", file_path.read_bytes(), content_type


def handle_client(client_socket: socket.socket) -> None:
    request = client_socket.recv(4096).decode("utf-8", errors="ignore")
    first_line = request.splitlines()[0] if request else ""
    parts = first_line.split()

    if len(parts) < 2 or parts[0] != "GET":
        body = b"<h1>400 Bad Request</h1>"
        client_socket.sendall(build_response("400 Bad Request", body))
        return

    status, body, content_type = get_file(parts[1])
    client_socket.sendall(build_response(status, body, content_type))


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server is running: http://{HOST}:{PORT}")

        while True:
            client_socket, address = server_socket.accept()
            with client_socket:
                print(f"Request from {address}")
                handle_client(client_socket)


if __name__ == "__main__":
    main()
