import asyncio
import json
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.auth_service import decode_access_token
from app.services.session_manager import get_session
from app.services.realtime_state import get_state


router = APIRouter(tags=["Live Admin Monitor"])


# ---------------------------------------------------------
# EXISTING AI LIVE MONITOR
# ---------------------------------------------------------

@router.websocket("/ws/admin/{interview_id}")
async def admin_live_monitor(websocket: WebSocket, interview_id: str):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = decode_access_token(token)
    except Exception:
        await websocket.close(code=1008)
        return

    if payload.get("role") != "admin":
        await websocket.close(code=1008)
        return

    session = get_session(interview_id)

    if session is None:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    try:
        while True:
            session = get_session(interview_id)
            state = get_state(interview_id)

            await websocket.send_text(
                json.dumps(
                    {
                        "interview_id": interview_id,
                        "status": session.get("status") if session else "unknown",
                        "candidate_name": (
                            session.get("name") if session else None
                        ),
                        "candidate_email": (
                            session.get("email") if session else None
                        ),
                        "role": session.get("role") if session else None,
                        "updated_at": state.get("updated_at"),
                        "latest_analysis": state.get(
                            "latest_analysis", {}
                        ),
                        "latest_window": state.get(
                            "latest_window", {}
                        ),
                    },
                    default=str,
                )
            )

            if not session or session.get("status") == "completed":
                break

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        return

    except Exception:
        try:
            await websocket.close(code=1011)
        except Exception:
            pass


# ---------------------------------------------------------
# WEBRTC SIGNALING
# ---------------------------------------------------------
#
# IMPORTANT:
#
# FastAPI does NOT carry the actual video/audio here.
#
# Browser A  <====================>  Browser B
#              WebRTC media
#
# FastAPI only passes:
#   offer
#   answer
#   ICE candidates
#
# The actual camera/microphone media travels peer-to-peer.
# ---------------------------------------------------------


# One candidate + one admin per interview.
#
# Example:
#
# webrtc_connections["IG-123"]["candidate"] = websocket
# webrtc_connections["IG-123"]["admin"] = websocket
#
webrtc_connections: Dict[str, Dict[str, WebSocket]] = {}


async def send_json(websocket: WebSocket, data: dict):
    try:
        await websocket.send_text(json.dumps(data, default=str))
    except Exception:
        pass


async def send_to_peer(
    interview_id: str,
    role: str,
    data: dict,
):
    peers = webrtc_connections.get(interview_id)

    if not peers:
        return

    other_role = "admin" if role == "candidate" else "candidate"

    peer = peers.get(other_role)

    if peer is None:
        return

    await send_json(peer, data)


def remove_webrtc_connection(
    interview_id: str,
    role: str,
    websocket: WebSocket,
):
    peers = webrtc_connections.get(interview_id)

    if not peers:
        return

    current = peers.get(role)

    if current is websocket:
        peers.pop(role, None)

    if not peers:
        webrtc_connections.pop(interview_id, None)


def validate_webrtc_user(
    token: str,
    role: str,
    interview_id: str,
):
    """
    Validate the JWT and interview session.

    Returns:
        payload, session

    Raises:
        ValueError
    """

    if not token:
        raise ValueError("Missing token")

    try:
        payload = decode_access_token(token)
    except Exception:
        raise ValueError("Invalid access token")

    if payload.get("role") != role:
        raise ValueError("Invalid role")

    session = get_session(interview_id)

    if session is None:
        raise ValueError("Interview session not found")

    status = session.get("status")

    if status not in {"active", "started"}:
        raise ValueError("Interview is not active")

    # Candidate ownership check.
    #
    # Candidate JWT username was created from candidate email.
    if role == "candidate":
        token_email = str(
            payload.get("username", "")
        ).strip().lower()

        session_email = str(
            session.get("email", "")
        ).strip().lower()

        if not token_email or token_email != session_email:
            raise ValueError(
                "Candidate is not authorized for this interview"
            )

    return payload, session


@router.websocket("/ws/webrtc/{interview_id}")
async def webrtc_signaling(
    websocket: WebSocket,
    interview_id: str,
):
    """
    WebRTC signaling endpoint.

    Query parameters:

        token=<JWT>
        role=candidate|admin

    Example:

        /ws/webrtc/IG-123?token=...&role=candidate

    This endpoint does NOT send AI analysis to candidates.
    It only relays WebRTC signaling messages.
    """

    token = websocket.query_params.get("token")
    role = websocket.query_params.get("role")

    if role not in {"candidate", "admin"}:
        await websocket.close(code=1008)
        return

    try:
        _, session = validate_webrtc_user(
            token=token,
            role=role,
            interview_id=interview_id,
        )
    except ValueError:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    # -----------------------------------------------------
    # Register this peer
    # -----------------------------------------------------

    peers = webrtc_connections.setdefault(
        interview_id,
        {},
    )

    # Only one connection per role for an interview.
    old_connection = peers.get(role)

    if old_connection is not None:
        try:
            await old_connection.close(code=4001)
        except Exception:
            pass

    peers[role] = websocket

    # Tell this browser that signaling is connected.
    await send_json(
        websocket,
        {
            "type": "signaling-ready",
            "interview_id": interview_id,
            "role": role,
        },
    )

    # -----------------------------------------------------
    # If both sides are connected, tell candidate to
    # create the WebRTC offer.
    # -----------------------------------------------------

    peers = webrtc_connections.get(interview_id, {})

    candidate_socket = peers.get("candidate")
    admin_socket = peers.get("admin")

    if candidate_socket is not None and admin_socket is not None:

        await send_json(
            candidate_socket,
            {
                "type": "peer-ready",
                "message": "Admin is connected. Create WebRTC offer.",
            },
        )

        await send_json(
            admin_socket,
            {
                "type": "peer-ready",
                "message": "Candidate is connected.",
            },
        )

    # -----------------------------------------------------
    # Receive signaling messages
    # -----------------------------------------------------

    try:
        while True:

            raw_message = await websocket.receive_text()

            try:
                message = json.loads(raw_message)
            except json.JSONDecodeError:
                await send_json(
                    websocket,
                    {
                        "type": "error",
                        "message": "Invalid signaling message",
                    },
                )
                continue

            message_type = message.get("type")

            # ---------------------------------------------
            # OFFER
            # ---------------------------------------------

            if message_type == "offer":

                await send_to_peer(
                    interview_id=interview_id,
                    role=role,
                    data={
                        "type": "offer",
                        "sdp": message.get("sdp"),
                    },
                )

            # ---------------------------------------------
            # ANSWER
            # ---------------------------------------------

            elif message_type == "answer":

                await send_to_peer(
                    interview_id=interview_id,
                    role=role,
                    data={
                        "type": "answer",
                        "sdp": message.get("sdp"),
                    },
                )

            # ---------------------------------------------
            # ICE CANDIDATE
            # ---------------------------------------------

            elif message_type == "ice-candidate":

                await send_to_peer(
                    interview_id=interview_id,
                    role=role,
                    data={
                        "type": "ice-candidate",
                        "candidate": message.get("candidate"),
                    },
                )

            # ---------------------------------------------
            # PING
            # ---------------------------------------------

            elif message_type == "ping":

                await send_json(
                    websocket,
                    {
                        "type": "pong",
                    },
                )

            # ---------------------------------------------
            # LEAVE
            # ---------------------------------------------

            elif message_type == "leave":

                await send_to_peer(
                    interview_id=interview_id,
                    role=role,
                    data={
                        "type": "peer-left",
                    },
                )

                break

            else:

                await send_json(
                    websocket,
                    {
                        "type": "error",
                        "message": (
                            f"Unknown signaling message: "
                            f"{message_type}"
                        ),
                    },
                )

    except WebSocketDisconnect:
        pass

    except Exception:
        pass

    finally:

        # Notify the other browser.
        try:
            await send_to_peer(
                interview_id=interview_id,
                role=role,
                data={
                    "type": "peer-left",
                },
            )
        except Exception:
            pass

        remove_webrtc_connection(
            interview_id=interview_id,
            role=role,
            websocket=websocket,
        )