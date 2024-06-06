import requests
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
import asyncio



SIGNALING_SERVER_URL = 'http://0.0.0.0:6969'
ID = "ttb"



async def main():
    print("Starting")

    
