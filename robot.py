import requests
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
import asyncio

SIGNALING_SERVER_URL = 'http://0.0.0.0:6969'
ID = "ttb"

async def main():
    print("Robot Starting")
    peer_connection = RTCPeerConnection()
    channel = peer_connection.createDataChannel("chat")


    await peer_connection.setLocalDescription(await peer_connection.createOffer())
    message = {"id": ID, "sdp": peer_connection.localDescription.sdp, "type": peer_connection.localDescription.type}
    req = requests.post(SIGNALING_SERVER_URL + '/offer', data=message)
    print(req.status_code)

    while True:
        resp = requests.get(SIGNALING_SERVER_URL + "/get_answer")
        if resp.status_code == 503:
            print("Answer not ready, trying again")
            await asyncio.sleep(1)
        elif resp.status_code == 200:
            data = resp.json()
            if data["type"] == "answer":
                rd = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                await peer_connection.setRemoteDescription(rd)
                print(peer_connection.remoteDescription)
                while True:
                    #print("Ready for Stuff")
                    await asyncio.sleep(1)
            else:
                print("Wrong type")
            break


    resp = requests.get(SIGNALING_SERVER_URL + "/get_offer")

asyncio.run(main())
