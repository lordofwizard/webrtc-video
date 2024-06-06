import requests
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
import asyncio
import cv2


SIGNALING_SERVER_URL = 'http://0.0.0.0:6969'
ID = "ttb"
sdp = ""
peer_connection = RTCPeerConnection()

async def main():
    global sdp,peer_connection
    print("Starting")

    resp = requests.get(SIGNALING_SERVER_URL + "/get_offer")

    print(resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        sdp = data["sdp"]
        if data["type"] == "offer":
            rd = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
            await peer_connection.setRemoteDescription(rd)
            await peer_connection.setLocalDescription(await peer_connection.createAnswer())

            message = {"id": ID, "sdp": peer_connection.localDescription.sdp, "type": peer_connection.localDescription.type}
            r = requests.post(SIGNALING_SERVER_URL + '/answer', data=message)
            print(message) 
            while True:
                await asyncio.sleep(3600)


async def run(pc, sdp):
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

    await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type="offer"))
    await pc.setLocalDescription(await pc.createAnswer())

    # Keep the connection open
    await asyncio.sleep(3600)

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    # Initialize the RTCPeerConnection
    pc = peer_connection

    # Assume robot_rd is set with the SDP of the robot
    robot_rd = "robot_sdp_string_here"

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(pc, robot_rd))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())
        cv2.destroyAllWindows()

