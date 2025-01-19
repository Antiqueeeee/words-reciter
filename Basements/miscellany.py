import os, sys
current_path = os.path.abspath(os.path.join(__file__, os.pardir))
project_path = os.path.abspath(os.path.join(current_path, os.pardir))
sys.path.append(project_path)

from Basements.ItemWord import WordSource
class Miscellany:
    
    def filename_parsing(self, filename):
        publisher, grade, examType, edition, volume = str(), str(), str(), str(), str()
        filename = filename.split("-")

        if len (filename) == 1:
            examType = filename[0]
            name = filename[0]
        if len (filename) == 4:
            publisher, edition, grade, volume = filename
            name = publisher + "-" + edition + "-" + grade + "-" + volume
        return WordSource(publisher, grade, examType, edition, volume, name)



if __name__ == '__main__':
    miscellany = Miscellany()
    print(miscellany.filename_parsing("出版社-版本-年级-册数").__dict__)
    print(miscellany.filename_parsing("CET4").__dict__)