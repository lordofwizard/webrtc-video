from fastapi import FastAPI, Response, HTTPException, Form
import json

app = FastAPI()

data = {}

@app.get('/test')
async def test():
    return {"status": "ok"}

@app.post('/offer')
async def offer(type: str = Form(...), id: str = Form(...), sdp: str = Form(...)):
    if type == "offer":
        data["offer"] = {"id": id, "type": type, "sdp": sdp}
        return Response(status_code=200)
    else:
        raise HTTPException(status_code=400)

@app.post('/answer')
async def answer(type: str = Form(...), id: str = Form(...), sdp: str = Form(...)):
    if type == "answer":
        data["answer"] = {"id": id, "type": type, "sdp": sdp}
        return Response(status_code=200)
    else:
        raise HTTPException(status_code=400)

@app.get('/get_offer')
async def get_offer():
    if "offer" in data:
        offer_data = json.dumps(data["offer"])
        del data["offer"]
        return Response(content=offer_data, status_code=200, media_type='application/json')
    else:
        raise HTTPException(status_code=503)

@app.get('/get_answer')
async def get_answer():
    if "answer" in data:
        answer_data = json.dumps(data["answer"])
        del data["answer"]
        return Response(content=answer_data, status_code=200, media_type='application/json')
    else:
        raise HTTPException(status_code=503)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6969)

