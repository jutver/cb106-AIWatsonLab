from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from ibm_watson import AssistantV2, SpeechToTextV1, TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import ibm_db, os, io
from dotenv import load_dotenv

load_dotenv()
# app = Flask(__name__)
app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Khởi tạo Watson clients
assistant_auth = IAMAuthenticator(os.getenv('ASSISTANT_APIKEY'))
assistant = AssistantV2(version='2024-08-25', authenticator=assistant_auth)
assistant.set_service_url(os.getenv('ASSISTANT_URL'))

stt_auth = IAMAuthenticator(os.getenv('STT_APIKEY'))
stt = SpeechToTextV1(authenticator=stt_auth)
stt.set_service_url(os.getenv('STT_URL'))

tts_auth = IAMAuthenticator(os.getenv('TTS_APIKEY'))
tts = TextToSpeechV1(authenticator=tts_auth)
tts.set_service_url(os.getenv('TTS_URL'))

# Kết nối Db2
conn_str = (
    f"DATABASE={os.getenv('DB2_DATABASE')};"
    f"HOSTNAME={os.getenv('DB2_HOST')};"
    f"PORT={os.getenv('DB2_PORT')};"
    f"UID={os.getenv('DB2_USERNAME')};"
    f"PWD={os.getenv('DB2_PASSWORD')};SECURITY=SSL;"
)
conn = ibm_db.connect(conn_str, '', '')

# Endpoint 1: Speech to Text
@app.route('/api/stt', methods=['POST'])
def speech_to_text():
    audio_file = request.files['audio']
    result = stt.recognize(audio=audio_file, content_type='audio/mp3').get_result()
    transcript = result['results'][0]['alternatives'][0]['transcript']
    return jsonify({'transcript': transcript})

# Endpoint 2: Watson Assistant
@app.route('/api/message', methods=['POST'])
def assistant_message():
    try:
        text = request.json['text']
        session_id = assistant.create_session(os.getenv('ENVIRONMENT_ID')).get_result()['session_id']
        response = assistant.message(
            assistant_id=os.getenv('ENVIRONMENT_ID'),
            session_id=session_id,
            input={'text': text}
        ).get_result()
        assistant.delete_session(os.getenv('ENVIRONMENT_ID'), session_id)
        return jsonify(response['output']['generic'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint 3: Text to Speech
@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    text = request.json['text']
    audio = tts.synthesize(text, accept='audio/wav', voice='en-US_AllisonV3Voice').get_result()
    return send_file(io.BytesIO(audio.content), mimetype='audio/wav')

# Endpoint 4: Db2 Courses
@app.route('/courses', methods=['GET'])
def get_courses():
    try:
        course_id = request.args.get('id', '')
        query = f"SELECT NAME, DESCRIPTION FROM COURSES WHERE NAME LIKE '%{course_id}%'"
        stmt = ibm_db.exec_immediate(conn, query)
        result = []
        row = ibm_db.fetch_assoc(stmt)
        while row:
            result.append({'name': row['NAME'], 'description': row['DESCRIPTION']})
            row = ibm_db.fetch_assoc(stmt)
        return jsonify({'courses': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint 5: Serve Web UI
@app.route('/')
def serve_ui():
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(port=5000)
