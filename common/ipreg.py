"""
" ip2region python searcher client module
"
" Author: koma<komazhang@foxmail.com>
" Date : 2015-11-06
"""
import io
import sys
import socket
import struct

from config import settings


class IpRegInfo(object):
    __INDEX_BLOCK_LENGTH = 12
    __TOTAL_HEADER_LENGTH = 8192

    __f = None
    __headerSip = []
    __headerPtr = []
    __headerLen = 0
    __indexSPtr = 0
    __indexLPtr = 0
    __indexCount = 0
    __dbBinStr = ''

    def __init__(self, db_file):
        self.init_database(db_file)

    def memory_search(self, ip):
        """
        " memory search method
        " param: ip
        """
        if not ip.isdigit():
            ip = self.ip2long(ip)

        if self.__dbBinStr == '':
            self.__dbBinStr = self.__f.read()  # read all the contents in file
            self.__indexSPtr = self.get_long(self.__dbBinStr, 0)
            self.__indexLPtr = self.get_long(self.__dbBinStr, 4)
            self.__indexCount = int((self.__indexLPtr - self.__indexSPtr) /
                                    self.__INDEX_BLOCK_LENGTH) + 1

        l, h, data_ptr = (0, self.__indexCount, 0)
        while l <= h:
            m = int((l + h) >> 1)
            p = self.__indexSPtr + m * self.__INDEX_BLOCK_LENGTH
            sip = self.get_long(self.__dbBinStr, p)

            if ip < sip:
                h = m - 1
            else:
                eip = self.get_long(self.__dbBinStr, p + 4)
                if ip > eip:
                    l = m + 1
                else:
                    data_ptr = self.get_long(self.__dbBinStr, p + 8)
                    break

        if data_ptr == 0:
            raise Exception("Data pointer not found")

        return self.return_data(data_ptr)

    def init_database(self, db_file):
        """
        " initialize the database for search
        " param: dbFile
        """
        try:
            self.__f = io.open(db_file, "rb")
        except IOError as e:
            print("[Error]: %s" % e)
            sys.exit()

    def return_data(self, data_ptr):
        """
        " get ip data from db file by data start ptr
        " param: data ptr
        """
        data_len = (data_ptr >> 24) & 0xFF
        data_ptr = data_ptr & 0x00FFFFFF

        self.__f.seek(data_ptr)
        data = self.__f.read(data_len)

        info = {"city_id": self.get_long(data, 0),
                "region": data[4:].decode('utf-8')}
        return info

    @staticmethod
    def ip2long(ip):
        _ip = socket.inet_aton(ip)
        return struct.unpack("!L", _ip)[0]

    @staticmethod
    def is_ip(ip):
        p = ip.split(".")
        if len(p) != 4:
            return False
        for pp in p:
            if not pp.isdigit():
                return False
            if len(pp) > 3:
                return False
            if int(pp) > 255:
                return False
        return True

    @staticmethod
    def get_long(b, offset):
        if len(b[offset:offset + 4]) == 4:
            return struct.unpack('I', b[offset:offset + 4])[0]
        return 0

    def close(self):
        if self.__f is not None:
            self.__f.close()
        self.__dbBinStr = None
        self.__headerPtr = None
        self.__headerSip = None


class IpRegData(IpRegInfo):
    def __init__(self):
        path = settings.data_storage_dir.joinpath('ip2region.db')
        IpRegInfo.__init__(self, path)

    def query(self, ip):
        result = self.memory_search(ip)
        addr_list = result.get('region').split('|')
        addr = ''.join(filter(lambda x: x != '0', addr_list[:-1]))
        isp = addr_list[-1]
        if isp == '0':
            isp = '未知'
        info = {'addr': addr, 'isp': isp}
        return info
