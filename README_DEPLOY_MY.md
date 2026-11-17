# Online တင်ရန် (Render + GitHub)

ဒီ project ကို ဒီနေရာကနေ မင်းရဲ့ Render/GitHub account ထဲ တိုက်ရိုက်မတင်နိုင်ပါ။ Account ချိတ်ဆက်ခွင့် မရှိတဲ့အတွက် မင်းကိုယ်တိုင် အောက်ပါအဆင့်တွေ လုပ်ရပါမယ်။

1. GitHub account ဖွင့်ပြီး repository အသစ်လုပ်ပါ။
2. ZIP ကိုဖြည်ပြီး project ထဲက ဖိုင်အားလုံးကို repository ထဲ upload လုပ်ပါ။ `app.py`, `requirements.txt`, `Dockerfile`, `render.yaml`, `static/` အားလုံး ပါရပါမယ်။
3. Render account ဖွင့်ပြီး GitHub ကိုချိတ်ပါ။
4. Render Dashboard → New → Blueprint ကိုရွေးပြီး repository ကိုချိတ်ပါ။ `render.yaml` ကိုဖတ်ပြီး service တည်ဆောက်ပါ။
5. Environment variable `OPENAI_API_KEY` မှာ ကိုယ့် OpenAI API key ထည့်ပါ။ API key ကို chat ထဲ မပို့ပါနှင့်။
6. Deploy ပြီး Render URL-ийг ဖွင့်ပြီး စမ်းပါ.

**Төлбөр/хадгалалт:** Render free service ရရှိနိုင်မှု၊ sleep/usage limits өөрчлөгдөж болно။ OpenAI API အသုံးပြုခ သီးခြားရှိနိုင်သည်။ Movie ဖိုင်ကြီးများကို upload လုပ်ခြင်းသည် hosting memory/disk/time limit ကြောင့် မအောင်မြင်နိုင်ပါ။ Free instance တွင် job ပြီးဆုံးမီ sleep/restart ဖြစ်နိုင်ပြီး local disk သည် persistent မဟုတ်ပါ။ စမ်းသပ်ရန် video အတိုနှင့် ကိုယ်ပိုင်/အသုံးပြုခွင့်ရှိသော ဖိုင်ကိုသာ သုံးပါ။

ဒီ MVP မှာ login, upload size limit, cloud persistent storage, queue/worker, automatic cleanup မပါသေးပါ။ အများပြည်သူသုံးအဖြစ် မဖြန့်ချိမီ ထပ်မံလုံခြုံရေးပြင်ဆင်ရန်လိုသည်။
