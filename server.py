import socket, os, json, math, time
import random

# クライアントからjson形式のデータ(id, 関数名, 引数, データ型など)を受け取り
# serverで関数を実行して、クライアントに結果を返却したい
# jsonで渡される例
# request
# {
#    "method": "subtract",
#    "params": [42, 23],
#    "param_types": [int, int],
#    "id": 1
# }
# response
# {
#    "results": "19",
#    "result_type": "int",
#    "id": 1
# }

def main():
    socketManager = SocketManager()
    socketManager.create_socket()
    socketManager.bind_socket()
    socketManager.listen_for_connections()
    time.sleep(1)
    print("Running server")
    time.sleep(1)
    requestHandler = RequestHandler(socketManager.sock)
    print("request_handler is ok")
    while True:
        requestHandler.accept()
        try:
            print("address {}".format(requestHandler.client_address))
            while True:
                print("test running")
                json_data = requestHandler.response()
                if json_data:
                    implement_function = ImplementFunction()
                    implement_function.catch_data(json_data)
                    data = implement_function.set_result_to_return(implement_function.results, implement_function.results_type, implement_function.id)
                    requestHandler.request(data)
                else:
                    print("no data")
                    time.sleep(1)
                    print("Closing current connection")
                    break
        finally:
            requestHandler.connection.close()





class FunctionCollection:
    def floor(self, num):
        return math.floor(num)

    def nroot(self, n, x, epsilon=1e-10):
        low, high = 0.0, max(1.0, x)
        guess = (low + high) / 2.0

        while abs(guess ** n - x) > epsilon:
            if guess ** n < x:
                low = guess
            else:
                high = guess
            guess = (low + high) / 2.0

        return guess

    def reverse(self, s):
        return s[::-1]

    def valid_anagram(self, s1, s2):
        if len(s1) != len(s2):
            return False
        s1HashMap = {}
        s2HashMap = {}
        for s in s1:
            if s in s1HashMap:
                s1HashMap[s] += 1
            else:
                s1HashMap[s] = 1
        for s in s2:
            if s in s2HashMap:
                s2HashMap[s] += 1
            else:
                s2HashMap[s] = 1

        for key in s1HashMap.keys():
            if key not in s2HashMap:
                return False
            if s1HashMap[key] != s2HashMap[key]:
                return False
        return True

    def sort(self, strArr):
        for i in range(len(strArr) - 1):
            for j in range(i + 1, len(strArr)):
                if ord(strArr[i]) > ord(strArr[j]):
                    strArr[i], strArr[j] = strArr[j], strArr[i]
        return strArr


class SocketManager:
    def __init__(self):
        self.server_address = "./remote_address_file"
        self.sock = None

    def create_socket(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def bind_socket(self):
        try:
            os.unlink(self.server_address)
        except FileNotFoundError:
            pass
        self.sock.bind(self.server_address)

    def listen_for_connections(self):
        print("Starting Server address: {}".format(self.server_address))
        self.sock.listen(1)

class RequestHandler:
    def __init__(self, socket):
        self.sock = socket
        self.client_address = ""
        self.connection = None
        self.request_json = None

    def request(self, data):
        print(data)
        self.connection.sendall(data.encode())

    def response(self):
        # json形式のデータを受け取る
        data = json.load(self.connection.recv(16))
        return data.decode("utf-8")


    def accept(self):
        connection, client_address = self.sock.accept()
        self.set_client_address(client_address)
        self.set_connection(connection)


    def set_client_address(self, address):
        self.client_address = address

    def set_connection(self, connection):
        self.connection = connection

# クラス内で関数を実行して結果をjson形式でRequestHandlerのrequestに渡す
class ImplementFunction:
    def __init__(self):
        self.results = ""
        self.id = ""
        self.results_type = None
        self.method = ""
        self.params = None


    def execute(self):
        functionCollection = FunctionCollection()
        if self.method == "floot":
            tmp_result = functionCollection.floor(int(self.params))
            self.results_type = type(tmp_result)
            self.results = str(tmp_result)
        elif self.method == "nroot":
            tmp_result = functionCollection.nroot(self.params[0], self.params[1])
            self.results_type = type(tmp_result)
            self.results = str(tmp_result)
        elif self.method == "reverse":
            tmp_result = functionCollection.reverse(self.params)
            self.results_type = type(tmp_result)
            self.results = str(tmp_result)
        elif self.method == "valid_anagram":
            self.results = functionCollection.valid_anagram(self.params[0], self.params[1])
            self.results_type = type(self.results)
        elif self.method == "sort":
            self.results = functionCollection.sort(self.params)
            self.results_type = type(self.results)
        else:
            # 実行しないでそのまま返すかもう一度どクライアントからデータを受け取る
            pass


    def catch_data(self, data):
        self.id = data["id"]
        self.method = data["method"]
        self.params = data["paramas"]

    def set_result_to_return(self, result, result_type, id) -> dict:
        return {"result":result, "result_type":result_type, "id":id}





if __name__ == '__main__':
    main()
