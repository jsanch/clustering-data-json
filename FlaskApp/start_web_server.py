from flask import Flask, request, render_template
import kcluster
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', name='jjj')

@app.route('/cluster')
def cluster():
    # url = 'https://data.commerce.gov/data.json'
    url = request.args.get('url')
    k = int(request.args.get('k'))
    return kcluster.web_server_call(url,k,f=1)

# must be called after cluster !
@app.route('/tables')
def tables():
    k = int(request.args.get('k'))
    tablelist = []
    for i in  range(0,k):
        fpath = 'htmltables/' + str(i) + '.html'
        with open (fpath,'r') as f:
            tablelist.append(f.read().replace('\n',''))
    return json.dumps(tablelist)

if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True)
    # app.run()