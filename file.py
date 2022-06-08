from PIL import Image

class File:
    def __init__(self, name):
        self.name = name

    def saveEncoded(self, encodedData, file):
        pass

    def getBinaryData(self):
        pass

class PbmFile(File):
    def __init__(self, name):
        super().__init__(name)

    def getBinaryData(self):
        with open(self.name, 'rb') as file:
            data = file.read()
        binary = ''
        data = data[3:]
        self.columns = int(data[:data.index(b' ')].decode())
        data = data[data.index(b' ')+1:]
        self.rows = int(data[:data.index(b'\n')].decode())
        data = data[data.index(b'\n')+1:]
        for i in data:
            binary += bin(i)[2:].zfill(8)
        return binary

    def saveEncoded(self, encodedData, path):
        with open(path, 'wb') as file:
            file.write(bytes('P4\n', 'utf'))
            file.write(bytes(f'{self.columns} {self.rows}\n', 'utf'))
            file.write(int(encodedData, 2).to_bytes(len(encodedData)//8, 'big'))


class PilFile(File):
    def __init__(self, name):
        super().__init__(name)
        self.image = Image.open(name)

    def __del__(self):
        self.image.close()

    def getBinaryData(self):
        pixels = self.image.load()
        res = ''
        for x in range(self.image.size[0]):
            for y in range(self.image.size[1]):
                for component in pixels[x, y]:
                    res += bin(component)[2:].zfill(8)
        return res

    def saveEncoded(self, encodedData, path):
        new_image = Image.new(self.image.mode, self.image.size)

        pixels = new_image.load()
        counter = 0
        pixelSize = 32 if self.image.mode == 'RGBA' else 24
        for x in range(self.image.size[0]):
            for y in range(self.image.size[1]):
                pixels[x, y] = self.toPixel(encodedData[counter:counter+pixelSize])
                counter += pixelSize
        new_image.save(path)

    def toPixel(self, bits):
        res = []
        for i in range(len(bits)//8):
            res.append(int(bits[i*8:(i+1)*8], 2))
        return tuple(res)

def createFile(name):
    if name.endswith('.pbm'):
        return PbmFile(name)
    else:
        return PilFile(name)