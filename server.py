import Pyro4

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

@Pyro4.expose
class FileServer:
    def __init__(self):
        self.files = {} 
        self.interests = {} 

    def upload_file(self, ref_name, file_name, file_data):
        if len(file_data) > MAX_FILE_SIZE:
            return "File size exceeds 1MB limit."

        self.files[ref_name] = {'file_name': file_name, 'data': file_data}
        self.check_interests(ref_name)
        return f"File {file_name} uploaded successfully with reference name {ref_name}."

    def list_files(self):
        return {ref_name: info['file_name'] for ref_name, info in self.files.items()}

    def download_file(self, ref_name):
        file_info = self.files.get(ref_name, None)
        if file_info is None:
            return "File not found."
        print(
            # Linha de depuração para confirmar o tipo de dados
            f"Returning data for: {ref_name}, Data Type: {type(file_info['data'])}")
        return file_info['data']

    def register_interest(self, ref_name, client_proxy, duration):
        if ref_name not in self.interests:
            self.interests[ref_name] = []
        self.interests[ref_name].append((client_proxy, duration))
        return f"Interest in {ref_name} registered."

    def cancel_interest(self, ref_name, client_proxy):
        if ref_name in self.interests:
            self.interests[ref_name] = [
                (proxy, duration) for proxy, duration in self.interests[ref_name]
                if proxy != client_proxy
            ]
            return f"Interest in {ref_name} cancelled."
        return "Interest not found."

    def list_interests(self):
        return {ref_name: clients for ref_name, clients in self.interests.items()}

    def delete_file(self, ref_name):
        if ref_name in self.files:
            del self.files[ref_name]
            return f"File with reference name {ref_name} deleted."
        return "File not found."

    def check_interests(self, ref_name):
        if ref_name in self.interests:
            for client_proxy, duration in self.interests[ref_name]:
                client_proxy.notify(ref_name) 
            del self.interests[ref_name] 

def start_server():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS(host="localhost", port=9090)
    uri = daemon.register(FileServer)
    ns.register("example.fileserver", uri)

    print("Server is ready.")
    daemon.requestLoop()

if __name__ == "__main__":
    start_server()
