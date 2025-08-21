import asyncio, uuid, cv2, numpy as np
from av import VideoFrame
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
from aiortc.mediastreams import MediaStreamTrack
from .tracking import registry
from .vector_store import upsert_emotion

PCS: dict[str, RTCPeerConnection] = {}  # session_id -> pc

class CameraVideoTrack(MediaStreamTrack):
    kind = "video"
    def __init__(self):
        super().__init__()
        # Windows prefers CAP_DSHOW
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.frame_idx = 0

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        ok, frame = self.cap.read()
        if not ok:
            await asyncio.sleep(0.01)
            # black frame fallback
            black = np.zeros((480, 640, 3), dtype=np.uint8)
            vf = VideoFrame.from_ndarray(black, format="bgr24")
            vf.pts, vf.time_base = pts, time_base
            return vf

        img = frame

        # TODO: plug your real detector here:
        # - get embedding (np.ndarray)
        # - get emotion vector (list[float]) and labels dict
        embedding = np.random.rand(128).astype(np.float32)
        emotion = np.random.rand(7).astype(np.float32); emotion /= (emotion.sum()+1e-9)
        labels = {"happy": float(emotion[0])}

        person_id, _ = registry.match_or_create(embedding)
        if self.frame_idx % 15 == 0:  # throttle writes
            upsert_emotion(person_id, emotion.tolist(), labels)

        cv2.putText(img, f"ID {person_id}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        vf = VideoFrame.from_ndarray(img, format="bgr24")
        vf.pts, vf.time_base = pts, time_base
        self.frame_idx += 1
        return vf

    def stop(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        super().stop()

async def handle_offer(offer_sdp: str, offer_type: str):
    session_id = str(uuid.uuid4())
    cfg = RTCConfiguration(iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])])
    pc = RTCPeerConnection(configuration=cfg)
    PCS[session_id] = pc

    @pc.on("connectionstatechange")
    async def on_state_change():
        if pc.connectionState in ("failed", "closed", "disconnected"):
            await pc.close()
            PCS.pop(session_id, None)

    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp, type=offer_type))
    pc.addTrack(CameraVideoTrack())

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return session_id, pc.localDescription

async def close_session(session_id: str):
    pc = PCS.pop(session_id, None)
    if pc:
        await pc.close()
        return True
    return False
