import requests
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import asyncio
import cv2
from av import VideoFrame

SIGNALING_SERVER_URL = 'http://0.0.0.0:6969'
ID = "ttb"
resp = ""

class VideoCameraTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()
        if not ret:
            return None

        av_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        av_frame.pts = pts
        av_frame.time_base = time_base
        return av_frame

async def main():
    global resp
    print("Robot Starting")
    peer_connection = RTCPeerConnection()

    # Create and add video track
    video_track = VideoCameraTrack()
    peer_connection.addTrack(video_track)

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
                    await asyncio.sleep(1)
            else:
                print("Wrong type")
            break

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    
    asyncio.run(main())

