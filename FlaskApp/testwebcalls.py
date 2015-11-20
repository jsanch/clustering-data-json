import kcluster

# url = 'https://data.commerce.gov/data.json'
# kcluster.web_server_call(url,k=10,f=1)


tablelist = []
for i in  range(0,10):
    fpath = 'htmltables/' + str(i) + '.html'
    with open (fpath,'r') as f:
        tablelist.append(f.read())
print tablelist[0]