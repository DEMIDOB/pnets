import dataclasses
import os


@dataclasses.dataclass
class IPv4:
    ip_str: str
    ip: int
    name: str

    def __init__(self, ip_str: str):
        self.ip_str = ip_str
        self.ip = 0
        self.ip_split = list(map(int, self.ip_str.split(".")))
        self.name = ""
        self.is_alive = False

        assert len(self.ip_split) == 4

        for pt in self.ip_split:
            self.ip *= 256
            self.ip += int(pt)

    def apply_mask(self, mask_ip):
        if not isinstance(mask_ip, IPv4):
            mask_ip = IPv4(mask_ip)

        self.ip = self.ip & mask_ip.ip
        self.update_str()

    def update_str(self):
        self.ip_str = ""
        ip_n = self.ip

        while ip_n > 0:
            pt = ip_n % 256
            ip_n -= pt
            ip_n /= 256

            self.ip_str = f"{int(pt)}.{self.ip_str}"

        self.ip_str = self.ip_str.strip(" ")  # just in case...
        self.ip_str = self.ip_str.strip(".")
        self.ip_str = self.ip_str.strip(" ")  # just in case...

    @property
    def ip_str_bin(self):
        return bin(self.ip)[2:]

    @property
    def is_mask(self):
        is_on_zeros = False
        for c in self.ip_str_bin:
            if c == "0" and not is_on_zeros:
                is_on_zeros = True
                continue

            if c == "0" and is_on_zeros or c == "1" and not is_on_zeros:
                continue
            else:
                return False

        return True

    @property
    def num_devices(self):
        if not self.is_mask:
            return -1

        return 2 ** len(self.ip_str_bin[self.ip_str_bin.find("0"):])

    def inc(self):
        self.ip += 1
        self.update_str()

    def lookup(self, verbose=False):
        # print(f"Checking {self}")
        f = os.popen(f"nslookup {self.ip_str}")
        out = f.read()
        f.close()

        res_str = str(out)
        ok = "server can't find" not in res_str and "name =" in res_str

        if ok:
            ip_repr = self.ip_str
            for _ in range(15 - len(self.ip_str)):
                ip_repr += " "

            self.is_alive = True
            self.name = res_str[res_str.rfind("name =") + 6:].strip().replace("\n", " ")

            if verbose:
                print(ip_repr, self.name)

        return ok