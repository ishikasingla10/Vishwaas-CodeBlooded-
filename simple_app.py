from flask import Flask, request, jsonify

app = Flask(__name__)

# Simple scam detection rules
SCAM_KEYWORDS = {
    'urgent': 10, 'winner': 10, 'lottery': 10, 'prince': 10,
    'click link': 15, 'wire money': 15, 'verify account': 10,
    'congratulations': 8, 'million': 8, 'inheritance': 8
}

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Simple Scam Detector</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
        textarea { width: 100%; height: 100px; margin: 10px 0; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        .result { margin: 20px 0; padding: 15px; border-radius: 5px; }
        .safe { background: #d4edda; color: #155724; }
        .scam { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>Scam Detector</h1>
    <textarea id="text" placeholder="Paste message here..."></textarea>
    <button onclick="check()">Check Message</button>
    <div id="result"></div>

    <script>
        async function check() {
            const text = document.getElementById('text').value;
            const res = await fetch('/check', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text})
            });
            const data = await res.json();
            document.getElementById('result').innerHTML = 
                `<div class="result ${data.is_scam ? 'scam' : 'safe'}">
                    <strong>${data.risk}</strong><br>
                    ${data.reason}
                </div>`;
        }
    </script>
</body>
</html>
    '''

@app.route('/check', methods=['POST'])
def check():
    text = request.json.get('text', '').lower()
    score = 0
    reasons = []
    
    for keyword, points in SCAM_KEYWORDS.items():
        if keyword in text:
            score += points
            reasons.append(keyword)
    
    is_scam = score >= 20
    return jsonify({
        'is_scam': is_scam,
        'risk': 'SCAM' if is_scam else 'SAFE',
        'reason': 'Found: ' + ', '.join(reasons) if reasons else 'No scam indicators'
    })

if __name__ == '__main__':
    app.run(debug=True)
