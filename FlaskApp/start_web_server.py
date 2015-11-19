from flask import Flask, request, render_template
import kcluster

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', name='jjj')

@app.route('/cluster')
def cluster():
    url = 'https://data.commerce.gov/data.json'
    url = request.args.get('url')
    return kcluster.web_server_call(url,k=10,f=1)



if __name__ == '__main__':
    app.debug = True
    app.run()