import json
import csv

# make sure close the two file before run
# if seeing PermissionError: [Errno 13] Permission denied, recheck if the files are closed or not
JSONfileName = "linkedin_jobs.json"
CSVfileName ="converted_json_to_csv.csv"

json_file = open(JSONfileName, 'r')
data = json.load(json_file)

# now we will open a file for writing
data_file = open(CSVfileName, 'w', newline='', encoding='utf-8') # the newline by default is \n

# create the csv writer object
csv_writer = csv.writer(data_file)

# Counter variable used for writing
# headers to the CSV file
count = 0
for job_id in data:
    job_detail = data[job_id]
    if count == 0:
        # Writing headers of CSV file
        header = job_detail.keys()
        csv_writer.writerow(header)
        count += 1
    # Writing data of CSV file
    csv_writer.writerow(job_detail.values())
json_file.close()
data_file.close()
print(f"{JSONfileName} converted into {CSVfileName}")
