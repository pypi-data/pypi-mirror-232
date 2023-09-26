import aanalytics2 as api2
import aanalyticsact as act
import pandas as pd

def segIDextract_raw(keyword):
    act.dataInitiator()
    cid = "samsun0"
    ags = api2.Analytics(cid)
    ags.header
    data = ags.getSegments(keyword)

    return data

def segIDExtract(keyword):
    print("Segment Loading Start")

    df = segIDextract_raw(keyword).drop('description', axis=1)
    act.exportToCSV(df, 'output.csv')

    data = pd.read_csv('output.csv', encoding='utf-8')
    data.to_csv('output.csv', encoding='utf-8-sig')

    print("Task done")


# if __name__ == "__main__":
#     keyword = "VD"
#     segIDExtract(keyword)