import os
import sys
import threading
import time
import random
import Pyro5.api
import Pyro5.errors
import cmd
import base64

@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class Peer:
    def __init__(self, peer_id, base_dir="files"):
        self.peer_id = peer_id
        self.base_dir = base_dir
        self.dir = os.path.join(base_dir, str(peer_id))

        os.makedirs(self.dir, exist_ok=True)
        self.files = set(os.listdir(self.dir))

        self.is_tracker = False
        self.epoch = 0
        self.tracker_epoch = 0
        self.voted_for = None
        self.voted_for_epoch = 0
        self.votes = 0
        # timers
        self.heartbeat_timer = None
        self.timeout = random.uniform(0.150, 400)
        # Pyro
        self.ns = Pyro5.api.locate_ns()
        self.daemon = Pyro5.api.Daemon()
        self.uri = self.daemon.register(self)
        self.name = f"Peer_{self.peer_id}"
        self.ns.register(self.name, self.uri)

        print(f"[{self.peer_id}] Registrado no NameServer como {self.name} -> {self.uri}")

        # encontrar tracker ou iniciar eleição
        self.tracker = self.find_tracker()
        if self.tracker:
            print(f"[{self.peer_id}] Tracker encontrado na época {self.tracker_epoch}")
            self.register_files_with_tracker()
        else:
            print(f"[{self.peer_id}] Nenhum tracker encontrado; iniciando eleição")
            self.start_election()

        # iniciar threads de background
        threading.Thread(target=self.daemon.requestLoop, daemon=True).start()
        self.reset_tracker_timer()

    def find_tracker(self):
        try:
            trackers = self.ns.list(prefix="Tracker_Epoca_")
            if trackers:
                # escolher maior época
                best = max(trackers.keys(), key=lambda n: int(n.split('_')[-1]))
                uri = trackers[best]
                epoch = int(best.split('_')[-1])
                
                self.tracker_epoch = epoch
                return Pyro5.api.Proxy(uri)
        except Exception:
            pass
        return None

    def register_files_with_tracker(self):
        try:
            self.tracker.register_files(self.peer_id, list(self.files))
        except Exception as e:
            print(f"Erro ao registrar arquivos no tracker: {e}")

    def reset_tracker_timer(self):
        # só agenda timeout se existir tracker remoto e não for tracker
        if self.is_tracker or self.tracker is None:
            return
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()
        self.heartbeat_timer = threading.Timer(self.timeout, self.on_tracker_failure)
        self.heartbeat_timer.daemon = True
        self.heartbeat_timer.start()

    def on_tracker_failure(self):
        # se já sou tracker, ignoro detecção de falha
        if self.is_tracker:
            return
        print(f"[{self.peer_id}] Timeout de heartbeat; detector de falha disparado")
        self.start_election()

    def start_election(self):
        # iniciar nova eleição com época sempre superior
        new_epoch = max(self.epoch, self.tracker_epoch) + 1
        self.epoch = new_epoch
        self.votes = 1
        self.voted_for = self.peer_id
        self.voted_for_epoch = self.epoch
        print(f"[{self.peer_id}] Iniciando eleição para época {self.epoch}")
        threading.Thread(target=self._collect_votes, daemon=True).start()

    def _collect_votes(self):
        # usar novo proxy do NameServer nesta thread e filtrar peers vivos
        ns = Pyro5.api.locate_ns()
        peers = ns.list(prefix="Peer_")
        ids = [int(name.split('_')[1]) for name in peers.keys()]
        # testar liveness via ping
        active_ids = []
        for pid in ids:
            try:
                uri = ns.lookup(f"Peer_{pid}")
                proxy = Pyro5.api.Proxy(uri)
                proxy.ping()
                active_ids.append(pid)
            except:
                pass
        total = len(active_ids)
        needed = total // 2 + 1
        for pid in active_ids:
            if pid == self.peer_id:
                continue
            try:
                uri = ns.lookup(f"Peer_{pid}")
                proxy = Pyro5.api.Proxy(uri)
                vote = proxy.request_vote(self.epoch, self.peer_id)
                if vote:
                    self.votes += 1
                    print(f"[{self.peer_id}] Recebi voto de {pid}")
            except Exception:
                pass
        if self.votes >= needed:
            self.become_tracker()
        else:
            print(f"[{self.peer_id}] Eleição falhou (votes={self.votes}/{needed})")

    @Pyro5.api.expose
    def request_vote(self, epoch, candidate_id):
        # aceita votar apenas se for nova época
        if epoch > getattr(self, 'voted_for_epoch', 0):
            self.voted_for = candidate_id
            self.voted_for_epoch = epoch
            print(f"[{self.peer_id}] Votou em {candidate_id} na época {epoch}")
            return True
        return False

    def become_tracker(self):
        # cancelar timer de detecção de falha ao virar tracker
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()
            self.heartbeat_timer = None
        self.is_tracker = True
        self.tracker_epoch = self.epoch
        self.file_index = {}  # nome_arquivo -> set(peer_id)
        self.peers = {}       # peer_id -> uri
        name = f"Tracker_Epoca_{self.epoch}"
        # registrar tracker no NameServer usando novo proxy nesta thread
        ns = Pyro5.api.locate_ns()
        try:
            ns.register(name, self.uri)
            print(f"[{self.peer_id}] Eleito tracker na época {self.epoch} e registrado como {name}")
            # atualizar self.ns para futuras operações
            self.ns = ns
        except Exception as e:
            print(f"Erro ao registrar tracker no NameServer: {e}")
        # coletar arquivos de todos os peers
        for pid in range(1,6):
            try:
                uri = ns.lookup(f"Peer_{pid}")
                proxy = Pyro5.api.Proxy(uri)
                fl = proxy.get_files()
                self.peers[pid] = uri
                self._update_index(pid, fl)
            except Exception:
                pass
        # iniciar envio periódico de heartbeat
        threading.Thread(target=self._send_heartbeat, daemon=True).start()

    def _update_index(self, pid, flist):
        # remover entradas antigas
        for fn, owners in list(self.file_index.items()):
            if pid in owners:
                owners.discard(pid)
                if not owners:
                    del self.file_index[fn]
        # adicionar novos
        for fn in flist:
            self.file_index.setdefault(fn, set()).add(pid)

    def _send_heartbeat(self):
        while self.is_tracker:
            for pid, uri in list(self.peers.items()):
                try:
                    proxy = Pyro5.api.Proxy(uri)
                    proxy.receive_heartbeat(self.tracker_epoch)
                except Exception:
                    pass
            time.sleep(0.1)

    @Pyro5.api.expose
    def register_files(self, peer_id, flist):
        # usar novo proxy do NameServer nesta thread
        try:
            ns = Pyro5.api.locate_ns()
            uri = ns.lookup(f"Peer_{peer_id}")
            self.peers[peer_id] = uri
            self._update_index(peer_id, flist)
            print(f"[{self.peer_id}] Tracker atualizou índice com arquivos de {peer_id}")
        except Exception as e:
            print(f"Erro em register_files: {e}")

    @Pyro5.api.expose
    def query_file(self, filename):
        return list(self.file_index.get(filename, []))

    @Pyro5.api.expose
    def query_all(self):
        return {fn: list(owners) for fn, owners in self.file_index.items()}

    @Pyro5.api.expose
    def receive_heartbeat(self, epoch):
        if epoch == self.tracker_epoch:
            self.reset_tracker_timer()
        return True

    @Pyro5.api.expose
    def download(self, filename):
        path = os.path.join(self.dir, filename)
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                return f.read()
        else:
            raise FileNotFoundError(f"Arquivo {filename} não encontrado em {self.peer_id}")

    @Pyro5.api.expose
    def get_files(self):
        return list(self.files)

    @Pyro5.api.expose
    def ping(self):
        """Retorna True para indicar que o peer está vivo."""
        return True

    def add_local_file(self, filename, content=None):
        path = os.path.join(self.dir, filename)
        with open(path, 'wb') as f:
            if content:
                f.write(content)
        self.files.add(filename)
        if not self.is_tracker:
            try:
                self.tracker.register_files(self.peer_id, list(self.files))
            except:
                pass

    def remove_local_file(self, filename):
        path = os.path.join(self.dir, filename)
        if os.path.isfile(path):
            os.remove(path)
            self.files.discard(filename)
            if not self.is_tracker:
                try:
                    self.tracker.register_files(self.peer_id, list(self.files))
                except:
                    pass

class CLI(cmd.Cmd):
    intro = "CLI P2P iniciado. Digite help para comandos."
    prompt = "> "

    def __init__(self, peer):
        super().__init__()
        self.peer = peer

    def do_list_local(self, arg):
        "Listar arquivos locais"
        print("Arquivos locais:", list(self.peer.files))

    def do_add_file(self, arg):
        "Adicionar arquivo local: add_file nome"
        fn = arg.strip()
        if fn:
            self.peer.add_local_file(fn)
            print(f"Arquivo {fn} adicionado localmente")
        else:
            print("Uso: add_file nome_do_arquivo")

    def do_remove_file(self, arg):
        "Remover arquivo local: remove_file nome"
        fn = arg.strip()
        if fn:
            self.peer.remove_local_file(fn)
            print(f"Arquivo {fn} removido localmente")
        else:
            print("Uso: remove_file nome_do_arquivo")

    def do_list_network(self, arg):
        "Listar arquivos disponíveis na rede"
        if self.peer.tracker:
            try:
                info = self.peer.tracker.query_all()
                print("Arquivos na rede:")
                for fn, owners in info.items():
                    print(f"  {fn}: {owners}")
            except Exception as e:
                print(f"Erro ao consultar tracker: {e}")
        elif self.peer.is_tracker:
            try:
                info = self.peer.query_all()
                print("Arquivos na rede:")
                for fn, owners in info.items():
                    print(f"  {fn}: {owners}")
            except Exception as e:
                print(f"Erro ao consultar tracker: {e}")
        else:
            print("Nenhum tracker disponível")

    def do_download(self, arg):
        "Baixar arquivo: download nome"
        fn = arg.strip()
        if not fn:
            print("Uso: download nome_do_arquivo")
            return
        # obter lista de peers que possuem o arquivo
        if self.peer.is_tracker:
            try:
                owners = self.peer.query_file(fn)
            except Exception as e:
                print(f"Erro ao consultar índice local: {e}")
                return
        elif self.peer.tracker:
            try:
                owners = self.peer.tracker.query_file(fn)
            except Exception as e:
                print(f"Erro ao consultar tracker: {e}")
                return
        else:
            print("Nenhum tracker disponível")
            return
        owners = [pid for pid in owners if pid != self.peer.peer_id]
        if not owners:
            print(f"Nenhum peer encontrado com {fn}")
            return
        # se houver múltiplos donos, permitir seleção
        if len(owners) > 1:
            print("Peers disponíveis para download:")
            for idx, owner_id in enumerate(owners, start=1):
                print(f"  {idx}: Peer_{owner_id}")
            choice = input("Escolha o número do peer: ")
            try:
                sel = int(choice)
                if sel < 1 or sel > len(owners):
                    raise ValueError
                pid = owners[sel-1]
            except Exception:
                print("Escolha inválida.")
                return
        else:
            pid = owners[0]
        try:
            # usar novo NameServer proxy nesta thread e criar proxy temporário
            ns = Pyro5.api.locate_ns()
            uri = ns.lookup(f"Peer_{pid}")
            with Pyro5.api.Proxy(uri) as proxy:
                data = proxy.download(fn)
            # normalizar retorno de download em vários formatos
            if not isinstance(data, (bytes, bytearray)):
                if isinstance(data, dict):
                    raw = data.get('data', data)
                else:
                    raw = data
                if isinstance(raw, (bytes, bytearray)):
                    data = raw
                elif isinstance(raw, list):
                    data = bytes(raw)
                elif isinstance(raw, str):
                    # decodifica base64 se for string do serializer, senão usa encode
                    try:
                        data = base64.b64decode(raw)
                    except Exception:
                        data = raw.encode()
                else:
                    data = str(raw).encode()
            self.peer.add_local_file(fn, content=data)
            print(f"Arquivo {fn} baixado de Peer_{pid}")
        except Exception as e:
            print(f"Falha no download de Peer_{pid}: {e}")

    def do_exit(self, arg):
        "Sair"
        print("Encerrando...")
        sys.exit(0)

    def do_EOF(self, arg):
        return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python peer.py <peer_id>")
        sys.exit(1)
    pid = int(sys.argv[1])
    peer = Peer(pid)
    CLI(peer).cmdloop() 