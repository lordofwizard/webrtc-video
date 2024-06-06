import requests
from aiortc import RTCPeerConnection, RTCSessionDescription
import asyncio
import cv2

SIGNALING_SERVER_URL = 'http://0.0.0.0:6969'
ID = "ttb"
peer_connection = RTCPeerConnection()

async def main():
    global peer_connection
    print("Starting")

    resp = requests.get(SIGNALING_SERVER_URL + "/get_offer")

    print(resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        if data["type"] == "offer":
            rd = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
            await peer_connection.setRemoteDescription(rd)
            await peer_connection.setLocalDescription(await peer_connection.createAnswer())

            message = {"id": ID, "sdp": peer_connection.localDescription.sdp, "type": peer_connection.localDescription.type}
            r = requests.post(SIGNALING_SERVER_URL + '/answer', data=message)
            print(message)

async def run(pc):
    @pc.on("track")
    def on_track(track):
        if track.kind == "video":
            print("Receiving video track")

            @track.on("frame")
            def on_frame(frame):
                img = frame.to_ndarray(format="bgr24")
                cv2.imshow("Received Video", img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    exit(0)

    # Keep the connection open
    await asyncio.sleep(3600)

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    # Create a new event loop and set it as the current event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
        loop.run_until_complete(run(peer_connection))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(peer_connection.close())
        cv2.destroyAllWindows()
        loop.close()

