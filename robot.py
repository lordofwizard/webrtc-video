import requests
from aiortc import *
import asyncio

SIGNALING_SERVER_URL = 'http://0.0.0.0:6969'
ID = "ttb"

resp = ""

peer_connection = RTCPeerConnection()
async def main():
    global peer_connection
    global resp
    print("Robot Starting")
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





class VideoCameraTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()
        if not ret:
            return None

        # Create an av VideoFrame from the captured frame
        av_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        av_frame.pts = pts
        av_frame.time_base = time_base
        return av_frame

async def run(pc, sdp):
    await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type="offer"))
    await pc.setLocalDescription(await pc.createAnswer())

    # Create and add video track
    video_track = VideoCameraTrack()
    pc.addTrack(video_track)

    # Keep the connection open
    await asyncio.sleep(3600)

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    
    asyncio.run(main())

    # Initialize the RTCPeerConnection

    # Assume laptop_rd is set with the SDP of the laptop
    laptop_rd = resp.json()["sdp"]

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(pc, laptop_rd))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())

