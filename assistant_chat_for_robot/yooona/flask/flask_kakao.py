from flask import Flask, jsonify, request
import requests, sys, json
application = Flask(__name__)




@application.route("/prompt", methods=["POST"])
def get_prompt():

    request_data = json.loads(request.get_data(), encoding='utf-8')
    response = { 
        "version": "2.0", 
        "template": { 
            "outputs": [
                {
                    "simpleText": {
                        "text": f"질문을 받았습니다. AI에게 물어보고 올께요!: {request_data['action']['params']['prompt']}"}
                          }       
                        ]
                    }
                }

    return jsonify(response)



if __name__ == "__main__":
    application.run(host='0.0.0.0', port=80, debug=True)