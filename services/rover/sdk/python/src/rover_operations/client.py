










import grpc
from google.protobuf.empty_pb2 import Empty

# Import generated proto classes when available
try:
    from rover_operations.hello_tractor_pb2_grpc import HelloTractorStub
    from rover_operations.hello_tractor_pb2 import (
        DriveCommand,
        SafetyStatus,
        DeviceStatusUpdate,
        CommandResponse,
        SafetyCommand,
        DriveStatus,
    )
except ImportError:
    # Fallback for development when protobufs aren't generated yet
    class HelloTractorStub:
        pass

class RoverClient:
    """Python client for interacting with Rover Operations devices."""

    def __init__(self, device_host='localhost', device_port=50053):
        """
        Initialize a connection to the device.

        Args:
            device_host (str): Hostname or IP address of the device
            device_port (int): gRPC port for the device service
        """
        self.channel = grpc.insecure_channel(f'{device_host}:{device_port}')
        self.stub = HelloTractorStub(self.channel)

    def drive(self, speed: float, steer_angle: float) -> CommandResponse:
        """Send a drive command to the device.

        Args:
            speed (float): Desired speed in m/s
            steer_angle (float): Steering angle in degrees

        Returns:
            CommandResponse: Response from the device with current status
        """
        cmd = DriveCommand(speed=speed, steer_angle=steer_angle)
        return self.stub.Drive(cmd)

    def e_stop(self) -> SafetyStatus:
        """Activate emergency stop on the device.

        Returns:
            SafetyStatus: Current safety status of the device
        """
        cmd = SafetyCommand(e_stop_activate=True)
        response = self.stub.Safety(cmd)
        return response.response_data.safety_status

    def release_e_stop(self) -> SafetyStatus:
        """Release emergency stop on the device.

        Returns:
            SafetyStatus: Current safety status of the device
        """
        cmd = SafetyCommand(e_stop_release=True)
        response = self.stub.Safety(cmd)
        return response.response_data.safety_status

    def get_status(self) -> DeviceStatusUpdate:
        """Get current status from the device.

        Returns:
            DeviceStatusUpdate: Current telemetry and status
        """
        empty = Empty()
        return self.stub.GetStatus(empty)










