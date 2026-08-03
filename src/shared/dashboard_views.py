"""Dashboard views."""

from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from src.shared.composition import resolve


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard(request):
    """Get dashboard data for the logged-in user."""
    try:
        service = resolve("dashboard_service")
        data = service.execute(user_id=request.user.id)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def admin_dashboard(request):
    """Get admin dashboard with all system data."""
    if not request.user.is_admin():
        return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)
    try:
        service = resolve("dashboard_service")
        data = service.execute()  # No user_id means all data
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
