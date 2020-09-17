import StationList as station
import pandas as pd

# inputPath = r'C:\Users\CNOC-DC\Downloads\Sections to be Taken Over.xlsx'
# outputPath = r'C:\Users\CNOC-DC\Downloads\Stations to be Taken Over.xlsx'

def fetch(inputPath,outputPath):
    data = []
    df = pd.read_excel(inputPath, index_col=None)
    code1 = df['Code 1'].to_list()
    code2 = df['Code 2'].to_list()
    for source, dest in zip(code1, code2):
        list = station.getData(source, dest)
        data.append(list)
        print("Successfully fetched data of {}-{}:".format(source, dest))

    dataFrame = pd.concat(data)
    writer = pd.ExcelWriter(outputPath, engine='xlsxwriter')
    dataFrame.to_excel(writer, sheet_name='Station List')
    writer.save()
