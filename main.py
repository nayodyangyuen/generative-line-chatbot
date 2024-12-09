import uvicorn
from fastapi import FastAPI, HTTPException, Request
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (Configuration,
                                  ApiClient,
                                  MessagingApi,
                                  ReplyMessageRequest,
                                  TextMessage)
from linebot.v3.webhooks import (MessageEvent,
                                 TextMessageContent)
from linebot.v3.exceptions import InvalidSignatureError
import google.generativeai as genai

app = FastAPI()

ACCESS_TOKEN = "V25xhs4SySiSAbLkOAZ6i0ktzW4CyhjizPhM9fL+MubkS2dnDBYrp0xEGvPyU6ItEiyxYjeq4dk8Hf7Y9o1SVZKEX+9Cy9QAGIIM4OdasPud8iisbIDIutx+wCh7rRGGOrYmeK2QWer0pnvDOKB0mgdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "1ff49a2a3ee21666d3c0dc145181adc2"
GEMINI_API_KEY = "AIzaSyCitTSkOqIGjc0xptHygLSYo7qPtp3iX90"

configuration = Configuration(access_token=ACCESS_TOKEN)
handler = WebhookHandler(channel_secret=CHANNEL_SECRET)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


@app.get('/')
async def greeting():
    return "Hello from Backend 🙋‍♂️"


@app.post('/message')
async def message(request: Request):
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        raise HTTPException(
            status_code=400, detail="X-Line-Signature header is missing")

    body = await request.body()

    try:
        handler.handle(body.decode("UTF-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        gemini_response = model.generate_content(event.message.text)

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[TextMessage(text=gemini_response.text)]
            )
        )


if __name__ == "__main__":
    uvicorn.run("main:app",
                port=8000,
                host="0.0.0.0")
