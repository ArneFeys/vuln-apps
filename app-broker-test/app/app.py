from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page1')
def page1():
    return render_template('page1.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/api/data', methods=['GET', 'POST'])
def api_data():
    if request.method == 'POST':
        data = request.get_json() or request.form.to_dict()
        return jsonify({'received': data, 'message': 'POST successful'})
    return jsonify({'message': 'GET successful', 'status': 'ok'})

@app.route('/redirect-relative')
def redirect_relative():
    return redirect('/page1', code=302)

@app.route('/redirect-absolute')
def redirect_absolute():
    return redirect('http://testbroker.pentest:5001/page2', code=302)

@app.route('/form-submit', methods=['POST'])
def form_submit():
    data = request.form.to_dict()
    return jsonify({'received': data, 'message': 'Form submitted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
