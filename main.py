import FetchData as fetch


inputPath = r'C:\Users\CNOC-DC\Downloads\Sections to be Taken Over.xlsx'
outputPath = r'C:\Users\CNOC-DC\Downloads\Stations to be Taken Over.xlsx'

if __name__ == '__main__':
    fetch.fetch(inputPath,outputPath)

