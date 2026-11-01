"""通过Windows同步串口句柄采集原始字节，不发送板级命令。"""

import ctypes as C
from ctypes import wintypes as W


class DCB(C.Structure):
    """Windows DCB的固定二进制布局。"""
    _fields_ = [("length", W.DWORD), ("baud", W.DWORD), ("flags", W.DWORD),
                ("reserved", W.WORD), ("xon_lim", W.WORD), ("xoff_lim", W.WORD),
                ("byte_size", W.BYTE), ("parity", W.BYTE), ("stop_bits", W.BYTE),
                ("xon", C.c_char), ("xoff", C.c_char), ("error", C.c_char),
                ("eof", C.c_char), ("event", C.c_char), ("reserved1", W.WORD)]


class Timeouts(C.Structure):
    """Windows串口超时布局，读取最长等待200毫秒。"""
    _fields_ = [(n, W.DWORD) for n in ("interval", "multiplier", "constant", "write_multiplier", "write_constant")]


class Uart:
    """只读采集COM4；配置115200、8N1，无硬件或软件流控。"""
    def __init__(self):
        self.k = C.WinDLL("kernel32", use_last_error=True)
        self.handle = None
        self.k.CreateFileW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, C.c_void_p, W.DWORD, W.DWORD, W.HANDLE]
        self.k.CreateFileW.restype = W.HANDLE
        for name, args in (("GetCommState", [W.HANDLE, C.POINTER(DCB)]),
                           ("SetCommState", [W.HANDLE, C.POINTER(DCB)]),
                           ("SetCommTimeouts", [W.HANDLE, C.POINTER(Timeouts)]),
                           ("PurgeComm", [W.HANDLE, W.DWORD]),
                           ("ReadFile", [W.HANDLE, C.c_void_p, W.DWORD, C.POINTER(W.DWORD), C.c_void_p]),
                           ("CloseHandle", [W.HANDLE])):
            fn = getattr(self.k, name)
            fn.argtypes = args
            fn.restype = W.BOOL
        handle = self.k.CreateFileW(r"\\.\COM4", 0xC0000000, 0, None, 3, 0, None)
        if handle == C.c_void_p(-1).value:
            raise C.WinError(C.get_last_error())
        self.handle = handle
        try:
            assert C.sizeof(DCB) == 28
            config = DCB()
            config.length = C.sizeof(DCB)
            self._check(self.k.GetCommState(handle, C.byref(config)))
            config.baud, config.flags = 115200, 1
            config.byte_size, config.parity, config.stop_bits = 8, 0, 0
            self._check(self.k.SetCommState(handle, C.byref(config)))
            limits = Timeouts(0xFFFFFFFF, 0, 200, 0, 1000)
            self._check(self.k.SetCommTimeouts(handle, C.byref(limits)))
            self._check(self.k.PurgeComm(handle, 8))
        except Exception:
            self.close()
            raise

    @staticmethod
    def _check(value):
        if not value:
            raise C.WinError(C.get_last_error())

    def read(self):
        """读取现有原始字节；超时返回空字节串。"""
        buffer = C.create_string_buffer(4096)
        count = W.DWORD()
        self._check(self.k.ReadFile(self.handle, buffer, 4096, C.byref(count), None))
        return buffer.raw[:count.value]

    def close(self):
        """仅关闭本实例创建的句柄。"""
        if self.handle is not None:
            handle, self.handle = self.handle, None
            self._check(self.k.CloseHandle(handle))
