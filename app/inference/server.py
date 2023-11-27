import uvicorn
import yaml
import traceback
from fastapi import FastAPI, HTTPException
from time import time
from definitions import (
    Input,
    Output,
    ChatBot
)



############## DEFINITIONS ###############
_chatbot = None

def get_model():
    global _chatbot

    start = time()
    if _chatbot is None:
        print("Loading ChatBot...")
        _chatbot = ChatBot()
        print("Done!")
    else:
        print("ChatBot already loaded")
    print(f"Model loaded in {time() - start} seconds.")
    return _chatbot



############## Endpoints ##############
app = FastAPI()

@app.post("/warmup")
def warmup():
    try:
        _ = get_model()
        return "done"
    except:
        traceback.print_exc()
        return HTTPException(status_code=500, detail="Internal server error")


@app.post('/')
def predict(payload: Input):
    try:
        start = time()
        print(f"Received request: {payload.model_dump()}")
        print("Getting model...")

        chatbot = get_model()
        print("Done!")

        print("Processing request...")
        result = chatbot.reply(
            payload.prompt,
            payload.chat_history
        )

        
        print(f"Processed request in {time() - start} seconds")
        return result
    except MemoryError as e:
       traceback.print_exc()
       global _model
       del _model, model
       _model = None
       raise HTTPException(status_code=507, detail="Out of Memory")
    except Exception as e2:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)