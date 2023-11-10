from flask import Flask, Response, request, Blueprint
from flask_cors import CORS
from werkzeug.utils import secure_filename
from functools import wraps
import openai
import requests
import speech_recognition as sr
import pyaudio
import json
from konlpy.tag import Okt
import wave
import io
from pydub import AudioSegment
from pydub.utils import mediainfo
import soundfile

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

openai.api_key = "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"

def as_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        res = f(*args, **kwargs)
        res = json.dumps(res, ensure_ascii=False).encode('utf8')
        return Response(res, content_type='application/json; charset=utf-8')
    return decorated_function

@app.route('/')
@as_json
def home():
    return "hello world!"

@app.route('/json')
@as_json
def data():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('Speack Anything :')
        audio = r.listen(source)
        
        try:
            sound_to_text = r.recognize_google(audio)
            print('You said : {}'.format(sound_to_text))
        except:
            print('Sirry could not recignize your voice')
    #sound_to_text = "Hello my name is John. Nice to meet you"

    trans_text = "다음 문장을 한국어로 해석해줘. 추가적인 설명은 필요 없어\n" + sound_to_text
    completion_trans = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "한국어 문법을 지켜야돼, 번역한 문장은 존대표현을 유지해줘"},
        {"role": "assistant", "content": "형식은 (번역한 문장)이야. 추가적인 설명은 필요 없어"},
        {"role": "user", "content": trans_text}
    ]
    )

    gram_text = completion_trans.choices[0].message.content
    up_text = "다음 문장의 문법을 올바르게 수정해줘. 추가적인 설명은 필요 없어\n" + gram_text

    completion_gram = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "한국어 문법을 지켜야돼, 추가 설명은 필요 없어, 괄호 안에 문법이 올바른 문장"},
        {"role":"assistant","content":  "형식은 (문법을 수정한 문장)이야 만약, 올바른 문장이면 형식은 (문법이 올바른 문장)을 보내줘. 추가적인 설명은 필요 없어"},
        {"role": "user", "content": gram_text}
    ]
    )

    up_text = completion_gram.choices[0].message.content
    save_text = up_text
    up_text = "다음 문장을 격식체로 표현해줘. 추가적인 설명은 필요 없어\n" + up_text

    completion_up = openai.chat.completions.create(
    model="gpt-4",
    temperature=0.2,
    messages=[
        {"role": "system", "content": "한국어 문법을 지켜야돼. 입력한 문장이 평서문이면 평서문으로 알려주고 의문문이면 의문문, 명령문이면 명령문으로 알려줘"},
        {"role": "assistant", "content": " 형식은 (받은 문장의 격식체) 의 형태로 알려줘. 추가적인 설명은 필요 없어"},
        {"role": "user", "content": up_text}
    ]
    )

    down_text = completion_gram.choices[0].message.content
    down_text = "다음 문장을 비격식체로 표현해줘. 추가적인 설명은 필요 없어\n" + down_text

    completion_down = openai.chat.completions.create(
    model="gpt-4",
    temperature=0.2,
    messages=[
        {"role": "system", "content": "한국어 문법을 지켜야돼. 입력한 문장이 평서문이면 평서문으로 알려주고 의문문이면 의문문, 명령문이면 명령문으로 알려줘"},
        {"role": "assistant", "content": " 형식은 (받은 문장의 비격식체) 표의 형태로 알려줘. 추가적인 설명은 필요 없어"},
        {"role": "user", "content": down_text}
    ]
    )

    upper = completion_up.choices[0].message.content
    lower = completion_down.choices[0].message.content

    save_text_pron = "다음 문장의 한국어 발음의 영어 표기법을 알려줘. 추가적인 설명은 필요 없어\n" + save_text
    completion_trans_pron = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "한국어 문법을 지켜야돼. 입력한 문장이 평서문이면 평서문으로 알려주고 의문문이면 의문문, 명령문이면 명령문으로 알려줘"},
        {"role": "assistant", "content": " 형식은 (받은 문장의 영어 발음) 표의 형태로 알려줘. 추가적인 설명은 필요 없어"},
        {"role": "user", "content": save_text_pron}
    ]
    )
    save_text_pron = completion_trans_pron.choices[0].message.content

    upper_pron = "다음 문장의 한국어 발음의 영어 표기법을 알려줘. 추가적인 설명은 필요 없어\n" + upper
    completion_up_pron = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "한국어 문법을 지켜야돼. 입력한 문장이 평서문이면 평서문으로 알려주고 의문문이면 의문문, 명령문이면 명령문으로 알려줘"},
        {"role": "assistant", "content": " 형식은 (받은 문장의 영어 발음) 표의 형태로 알려줘. 추가적인 설명은 필요 없어"},
        {"role": "user", "content": upper_pron}
    ]
    )
    upper_pron = completion_up_pron.choices[0].message.content

    lower_pron = "다음 문장의 한국어 발음의 영어 표기법을 알려줘. 추가적인 설명은 필요 없어\n" + lower
    completion_down_pron = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "한국어 문법을 지켜야돼. 입력한 문장이 평서문이면 평서문으로 알려주고 의문문이면 의문문, 명령문이면 명령문으로 알려줘"},
        {"role": "assistant", "content": " 형식은 (받은 문장의 영어 발음) 표의 형태로 알려줘. 추가적인 설명은 필요 없어"},
        {"role": "user", "content": lower_pron}
    ]
    )
    lower_pron = completion_down_pron.choices[0].message.content

    #dic1={'소셜 미디어':'누리 소통 매체', '브이로그': '영상일기','치팅 데이':'먹요일','챌린지':'참여잇기','언박싱':'개봉(기)'}

    okt = Okt()
    result = okt.nouns(save_text)
    """
    result = []
    for i in result_noun:
        if i in dic1 :
            result.append(dic1[i])
        else:
            result.append(i)
    """

    return{
        "origin" : sound_to_text, "trans" : save_text, "up" : upper, "down" : lower, "pron" : save_text_pron, "up_pron" : upper_pron, "down_pron" : lower_pron, "noun" : result
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 9900, debug=True)
