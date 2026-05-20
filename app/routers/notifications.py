from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, status
from ..websocket_manager import manager
from ..oauth2 import verify_access_token
from ..schemas import TokenData

router = APIRouter(tags=["Notifications"])


@router.websocket("/ws/notifications")
async def notification_websocket(
    websocket: WebSocket,
    token: str = Query(...)  # token passed as ?token=... in the URL
):
    # Accept the connection first, then validate the token.
    # Rejecting before accept causes the ASGI server to return a 403
    # handshake response (client sees "Unexpected response code: 403").
    await websocket.accept()

    # WebSockets can't use Bearer headers like normal HTTP
    # so we verify the JWT token passed in the URL query param
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    try:
        token_data: TokenData = verify_access_token(token, credentials_exception)
        user_id = token_data.id
    except Exception as e:
        # Log the failure so it's visible in the server terminal
        print(f"WebSocket token verification failed: {e}")
        # Close gracefully with a policy-violation code so the client receives
        # a normal close event instead of an HTTP 403 handshake response.
        await websocket.close(code=1008, reason=str(e))  # 1008 = policy violation
        return

    # connect the user
    await manager.connect(websocket, user_id)

    try:
        # keep the connection alive — listen for any messages from the client
        while True:
            data = await websocket.receive_text()
            # you could handle client messages here (e.g. "mark as read")
            # for now we just keep the loop running to hold the connection open

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)