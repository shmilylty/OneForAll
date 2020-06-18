import csv
import zipfile

from common.utils import ip_to_int
from config.setting import data_storage_dir


class Entry(object):
    def __init__(self, start, end, value):
        self.start = int(start)
        self.end = int(end)
        self.value = value


class IPAsnData(object):
    def __init__(self):
        zip_path = data_storage_dir.joinpath("IP2LOCATION-LITE-ASN.CSV.ZIP")
        csv_path = data_storage_dir.joinpath("IP2LOCATION-LITE-ASN.CSV")
        if csv_path.exists():
            asn_fp = open(csv_path)
        else:
            zf = zipfile.ZipFile(zip_path)
            zf.extract('IP2LOCATION-LITE-ASN.CSV', data_storage_dir)
            asn_fp = open(csv_path)
        self.data = []
        reader = csv.reader(asn_fp, delimiter=',', quotechar='"')
        for row in reader:
            e = Entry(row[0], row[1], row)
            self.data.append(e)
        asn_fp.close()

    def __iter__(self):
        return self.data.__iter__()

    def find_i(self, ip, start, end):
        if end - start < 100:
            for i in range(start, end):
                obj = self.data[i]
                if obj.start <= ip <= obj.end:
                    return obj.value
            return None
        else:
            mid = start + (end - start) // 2
            val = self.data[mid].start
            if ip < val:
                return self.find_i(ip, start, mid)
            elif ip > val:
                return self.find_i(ip, mid, end)
            else:
                return self.data[mid].value

    def find_int(self, ip):
        return self.find_i(ip, 0, len(self.data) - 1)

    def find(self, ip):
        return self.find_i(ip_to_int(ip), 0, len(self.data) - 1)


class IPAsnInfo(object):
    def __init__(self):
        self.asn = IPAsnData()

    def find(self, ip):
        asn = self.asn.find(ip)
        if asn:
            result = {"cidr": asn[2], "asn": f'AS{asn[3]} {asn[4]}'}
            return result
        else:
            return None


if __name__ == "__main__":
    asn_info = IPAsnInfo()
    print(asn_info.find("188.81.94.77"))
