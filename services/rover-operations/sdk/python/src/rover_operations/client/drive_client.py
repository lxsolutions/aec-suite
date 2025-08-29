














"""
Hello Tractor gRPC client for Rover Operations platform.
"""

import grpc
from typing import Optional, Tuple

# Import generated protobuf classes
try:
    from rover_operations.proto.drive import drive_pb2, drive_pb2_grpc
except ImportError as e:
    raise ImportError("Could not import gRPC definitions. Ensure protobuf files are compiled.") from e

class HelloTractorClient:
    """
    Client for interacting with Hello Tractor devices via gRPC.
    """

    def __init__(self, endpoint: str = "localhost:50053"):
        """Initialize the client connection.

        Args:
            endpoint: Address of the gRPC server (host:port)
        """
        self.endpoint = endpoint
        self.channel: Optional[grpc.Channel] = None
        self.stub = None

    def connect(self) -> Tuple[bool, str]:
        """Establish connection to the Hello Tractor service.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            self.channel = grpc.insecure_channel(self.endpoint)
            self.stub = drive_pb2_grpc.HelloTractorStub(self.channel)

            # Test connection by getting status
            _ = self.get_status()
            return True, "Connected to Hello Tractor service"

        except Exception as e:
            error_msg = f"Failed to connect to {self.endpoint}: {str(e)}"
            return False, error_msg

    def disconnect(self) -> None:
        """Close the gRPC connection."""
        if self.channel is not None:
            try:
                self.channel.close()
            except Exception as e:
                print(f"Error closing channel: {e}")
            finally:
                self.channel = None
                self.stub = None

    def drive(self, speed: float, steer_angle: float) -> Tuple[bool, str, Optional[drive_pb2.DriveStatus]]:
        """Send a drive command to the tractor.

        Args:
            speed: Speed in meters per second (positive for forward, negative for reverse)
            steer_angle: Steering angle in degrees (-90 to +90)

        Returns:
            Tuple of (success: bool, message: str, status: Optional[DriveStatus])
        """
        try:
            if self.stub is None:
                return False, "Not connected", None

            command = drive_pb2.DriveCommand(
                speed=speed,
                steer_angle=steer_angle
            )

            response = self.stub.Drive(command)

            if response.status == drive_pb2.Status.OK:
                return True, "Drive command successful", response.response_data.drive_status
            else:
                error_type = drive_pb2.Status.Name(response.status)
                return False, f"Command failed: {error_type}", None

        except Exception as e:
            return False, f"Error sending drive command: {str(e)}", None

    def emergency_stop(self) -> Tuple[bool, str]:
        """Activate the emergency stop on the tractor.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if self.stub is None:
                return False, "Not connected"

            command = drive_pb2.SafetyCommand(
                e_stop_activate=True,
                reason="Emergency stop activated via SDK"
            )

            response = self.stub.Safety(command)

            if response.status == drive_pb2.Status.OK:
                return True, "Emergency stop activated"
            else:
                error_type = drive_pb2.Status.Name(response.status)
                return False, f"E-stop failed: {error_type}"

        except Exception as e:
            return False, f"Error activating emergency stop: {str(e)}"

    def release_emergency_stop(self) -> Tuple[bool, str]:
        """Release the emergency stop on the tractor.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if self.stub is None:
                return False, "Not connected"

            command = drive_pb2.SafetyCommand(
                e_stop_release=True,
                reason="Emergency stop released via SDK"
            )

            response = self.stub.Safety(command)

            if response.status == drive_pb2.Status.OK:
                return True, "Emergency stop released"
            else:
                error_type = drive_pb2.Status.Name(response.status)
                return False, f"E-stop release failed: {error_type}"

        except Exception as e:
            return False, f"Error releasing emergency stop: {str(e)}"

    def get_status(self) -> Tuple[bool, str, Optional[drive_pb2.DeviceStatusUpdate]]:
        """Get the current status of the tractor.

        Returns:
            Tuple of (success: bool, message: str, status: Optional[DeviceStatusUpdate])
        """
        try:
            if self.stub is None:
                return False, "Not connected", None

            response = self.stub.GetStatus(drive_pb2.Empty())

            if response.position.latitude != 0.0 or response.position.longitude != 0.0:
                # Valid position data
                return True, "Status retrieved successfully", response
            else:
                return False, "Received empty status", None

        except Exception as e:
            return False, f"Error getting status: {str(e)}", None














