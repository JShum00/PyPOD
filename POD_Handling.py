import struct, io, time
from Constants import Constants

class PodEntry:
    def __init__(self, name, offset, size, timestamp=0):
        self.name = name
        self.offset = offset
        self.size = size
        self.timestamp = timestamp

class PodFile:
    def __init__(self, path):
        self.path = path
        self.title = ""
        self.entries = []
        self.version = None
        with open(path, "rb") as f:
            self._load(f)

    def _read_fixed(self, f, length):
        data = f.read(length)
        return data.split(b"\x00", 1)[0].decode("ascii", "ignore")

    def _read_nullterm(self, f):
        buf = bytearray()
        while True:
            b = f.read(1)
            if not b or b == b"\x00":
                break
            buf.extend(b)
        return buf.decode("ascii", "ignore")

    def _load(self, f: io.BufferedReader):
        magic = struct.unpack("<I", f.read(4))[0]
        if magic == 0x65787464:  # 'dtxe' or 'tsal' for EPD1
            self.version = "EPD1"
            self._load_epd1(f)
        elif magic == 0x32444F50:  # POD2
            self.version = "POD2"
            self._load_pod2(f)
        elif magic == 0x33444F50:  # POD3
            self.version = "POD3"
            self._load_pod3(f)
        else:
            # Fallback — maybe POD1, which has no magic string
            try:
                f.seek(0)
                file_count = struct.unpack("<I", f.read(4))[0]

                # sanity check: file count must be reasonable, and file must be long enough
                file_size = f.seek(0, 2)
                f.seek(0)
                min_size = Constants.POD1_HEADER_SIZE + file_count * Constants.POD1_ENTRY_SIZE
                if file_count <= 0 or file_count > 10000 or file_size < min_size:
                    raise ValueError("Invalid POD1 structure")

                self.version = "POD1"
                self._load_pod1(f)
            except Exception:
                raise ValueError("Unsupported or unknown POD format")

    # ---- POD1 ----
    def _load_pod1(self, f):
        f.seek(0)
        file_count, = struct.unpack("<I", f.read(4))
        self.title = self._read_fixed(f, 80)

        dir_offset = Constants.POD1_HEADER_SIZE
        f.seek(dir_offset)

        for _ in range(file_count):
            name = self._read_fixed(f, 32)
            size, offset = struct.unpack("<II", f.read(8))
            self.entries.append(PodEntry(name, offset, size))


    # ---- POD2 ----
    def _load_pod2(self, f):
        _crc, = struct.unpack("<I", f.read(4))
        self.title = self._read_fixed(f, 80)
        file_count, audit_count = struct.unpack("<II", f.read(8))

        dir_offset = Constants.POD2_HEADER_SIZE
        names_offset = dir_offset + file_count * Constants.POD2_ENTRY_SIZE

        f.seek(dir_offset)
        for _ in range(file_count):
            name_off, size, offset, ts, checksum = struct.unpack("<IIIII", f.read(Constants.POD2_ENTRY_SIZE))
            cur = f.tell()
            f.seek(names_offset + name_off)
            name = self._read_nullterm(f)
            f.seek(cur)
            self.entries.append(PodEntry(name, offset, size, ts))

    # ---- POD3 ----
    def _load_pod3(self, f):
        _crc, = struct.unpack("<I", f.read(4))
        self.title = self._read_fixed(f, 80)
        file_count, audit_count, rev, priority = struct.unpack("<IIII", f.read(16))
        author = self._read_fixed(f, 80)
        copyright_ = self._read_fixed(f, 80)
        dir_off, dir_crc, str_size, dep_count, dep_crc, audit_crc = struct.unpack("<IIIIII", f.read(24))
        names_off = dir_off + file_count * Constants.POD3_ENTRY_SIZE

        f.seek(dir_off)
        for _ in range(file_count):
            name_off, size, offset, ts, checksum = struct.unpack("<IIIII", f.read(Constants.POD3_ENTRY_SIZE))
            cur = f.tell()
            f.seek(names_off + name_off)
            name = self._read_nullterm(f)
            f.seek(cur)
            self.entries.append(PodEntry(name, offset, size, ts))

    # ---- EPD1 ----
    def _load_epd1(self, f):
        f.seek(4)
        self.title = self._read_fixed(f, 256)
        entry_count = struct.unpack("<I", f.read(4))[0]
        f.read(8)  # skip version + checksum
        for _ in range(entry_count):
            name = self._read_fixed(f, 64)
            size, offset, ts, checksum = struct.unpack("<IIII", f.read(16))
            self.entries.append(PodEntry(name, offset, size, ts))

    def extract(self, outdir="."):
        import os
        os.makedirs(outdir, exist_ok=True)
        with open(self.path, "rb") as src:
            for e in self.entries:
                src.seek(e.offset)
                data = src.read(e.size)

                normalized_path = e.name.replace("\\", "/")
                dest_path = os.path.join(outdir, normalized_path)

                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, "wb") as out:
                    out.write(data)

