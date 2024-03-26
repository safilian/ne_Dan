from flask import Flask, jsonify, request
from ..ACT.src.sample_act_tree import analyze_act

app = Flask(__name__)

@app.route('/analyze-act', methods=['POST'])
def analyze_act_endpoint():
    act_data = request.get_json()
    # Assume 'act_data' contains the structure needed by your 'analyze_act' function

    result = analyze_act(act_data)

    return jsonify(result) 

if __name__ == '__main__':
    app.run(debug=False, port=5000) 
