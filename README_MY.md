# Myanmar Movie Recap AI (MVP)

ဒီ project က browser ကနေ video upload လုပ်ပြီး အောက်ပါတို့ကို ထုတ်ပေးတဲ့ စမ်းသပ် version ဖြစ်ပါတယ်။

- Transcript (movie ထဲက စကားပြောစာသား)
- မြန်မာ recap script
- AI voiceover MP3
- Subtitle SRT
- မူရင်း movie ထဲက အချိန်အလိုက် clip တွေကို ဆက်ထားတဲ့ draft MP4

## လိုအပ်တာ
- Python 3.10+
- FFmpeg (ffmpeg နဲ့ ffprobe command တွေ PATH ထဲမှာရှိရမယ်)
- OpenAI API key (API အသုံးပြုခ ကုန်ကျနိုင်တယ်)

## စတင်အသုံးပြုနည်း

1. ZIP ကိုဖြည်ပါ။
2. Terminal / Command Prompt မှာ project folder ထဲဝင်ပါ။
3. Dependencies ထည့်ပါ။

   `pip install -r requirements.txt`

4. `.env.example` ကို `.env` လို့ copy လုပ်ပြီး API key ထည့်ပါ။
5. API key ကို environment variable အဖြစ် သတ်မှတ်ပါ။ ဥပမာ Windows PowerShell:

   `$env:OPENAI_API_KEY="သင့်_API_KEY"`

   macOS/Linux:

   `export OPENAI_API_KEY="သင့်_API_KEY"`

6. Server စပါ။

   `uvicorn app:app --host 0.0.0.0 --port 8000`

7. Browser မှာ `http://127.0.0.1:8000` ဖွင့်ပါ။

## အရေးကြီး
- ဒီ MVP ကို local computer/server ပေါ်မှာ run ရပါမယ်။ ZIP ကို ဖုန်းထဲထည့်ရုံနဲ့ တန်းအလုပ်မလုပ်ပါ။
- ဖုန်းတစ်လုံးတည်းနဲ့သုံးချင်ရင် နောက်တစ်ဆင့်မှာ cloud hosting ချိတ်ပေးရပါမယ်။
- Movie အရှည်၊ file size၊ API limit နဲ့ API ကုန်ကျစရိတ်ပေါ်မူတည်ပြီး processing ကြာနိုင်ပါတယ်။
- Burmese TTS အသံထွက်အရည်အသွေးက voice/model ပေါ်မူတည်ပြီး စမ်းသပ်ဖို့လိုပါတယ်။
- Draft video က အချိန်အလိုက် clip တွေကိုရွေးထားတာသာဖြစ်ပြီး AI က ဇာတ်ဝင်ခန်းအကောင်းဆုံးတွေကို နားလည်ရွေးပေးတာ မဟုတ်သေးပါ။
- ကိုယ်ပိုင် သို့မဟုတ် အသုံးပြုခွင့်ရှိတဲ့ video များကိုသာ အသုံးပြုပါ။
- Production အတွက် upload size limit, login, job queue, cloud storage, retry, cleanup နဲ့ security ထပ်ထည့်ဖို့လိုပါတယ်။
