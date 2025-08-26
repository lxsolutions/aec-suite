














"""
Telemetry client for Rover Operations platform.
"""

import grpc
from typing import Optional, Tuple, List

# Import generated protobuf classes
try:
    from rover_operations.proto.telemetry import telemetry_pb2, telemetry_pb2_grpc
except ImportError as e:
    raise ImportError("Could not import gRPC definitions. Ensure protobuf files are compiled.") from e

class TelemetryClient:
    """
    Client for ingesting and querying telemetry data.
    """

    def __init__(self, endpoint: str = "localhost:8082"):
        """Initialize the client connection.

        Args:
            endpoint: Address of the gRPC server (host:port)
        """
        self.endpoint = endpoint
        self.channel: Optional[grpc.Channel] = None
        self.stub = None

    def connect(self) -> Tuple[bool, str]:
        """Establish connection to the telemetry service.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            self.channel = grpc.insecure_channel(self.endpoint)
            self.stub = telemetry_pb2_grpc.TelemetryServiceStub(self.channel)

            # Test connection by sending a simple ping
            test_event = telemetry_pb2.TelemetryEvent(
                device_id="test-device",
                sensor_type=telemetry_pb2.SensorType.GPS,
                gps_data=telemetry_pb2.GpsData(
                    position=telemetry_pb2.GeoPoint(latitude=0, longitude=0),
                    timestamp=telemetry_pb2.Timestamp.now()
                )
            )

            response = self.stub.IngestEvent(test_event)
            if not response.success:
                return False, f"Connection test failed: {response.message}"

            return True, "Connected to telemetry service"

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

    def ingest_gps_data(self, device_id: str, latitude: float, longitude: float,
                       altitude_meters: Optional[float] = 0.0) -> Tuple[bool, str]:
        """Ingest GPS telemetry data.

        Args:
            device_id: Identifier for the device
            latitude: Latitude in degrees (WGS84)
            longitude: Longitude in degrees (WGS84)
            altitude_meters: Altitude above sea level in meters

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if self.stub is None:
                return False, "Not connected"

            event = telemetry_pb2.TelemetryEvent(
                device_id=device_id,
                sensor_type=telemetry_pb2.SensorType.GPS,
                gps_data=telemetry_pb2.GpsData(
                    position=telemetry_pb2.GeoPoint(latitude=latitude, longitude=longitude),
                    altitude_meters=altitude_meters or 0.0,
                    timestamp=telemetry_pb2.Timestamp.now()
                )
            )

            response = self.stub.IngestEvent(event)

            if response.success:
                return True, "GPS data ingested successfully"
            else:
                return False, f"Failed to ingest GPS data: {response.message}"

        except Exception as e:
            return False, f"Error ingesting GPS data: {str(e)}"

    def ingest_imu_data(self, device_id: str,
                      accel_x: float, accel_y: float, accel_z: float,
                      gyro_x: Optional[float] = 0.0, gyro_y: Optional[float] = 0.0, gyro_z: Optional[float] = 0.0) -> Tuple[bool, str]:
        """Ingest IMU telemetry data.

        Args:
            device_id: Identifier for the device
            accel_x/y/z: Acceleration in m/s² (vehicle frame)
            gyro_x/y/z: Angular rate in rad/s

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if self.stub is None:
                return False, "Not connected"

            event = telemetry_pb2.TelemetryEvent(
                device_id=device_id,
                sensor_type=telemetry_pb2.SensorType.IMU,
                imu_data=telemetry_pb2.ImuData(
                    acceleration_x=accel_x,
                    acceleration_y=accel_y,
                    acceleration_z=accel_z,
                    angular_rate_x=gyro_x or 0.0,
                    angular_rate_y=gyro_y or 0.0,
                    angular_rate_z=gyro_z or 0.0,
                    timestamp=telemetry_pb2.Timestamp.now()
                )
            )

            response = self.stub.IngestEvent(event)

            if response.success:
                return True, "IMU data ingested successfully"
            else:
                return False, f"Failed to ingest IMU data: {response.message}"

        except Exception as e:
            return False, f"Error ingesting IMU data: {str(e)}"

    def query_recent_data(self, device_id: str, sensor_type: telemetry_pb2.SensorType,
                         minutes_back: int = 5) -> Tuple[bool, str, Optional[List[telemetry_pb2.TelemetryEvent]]]:
        """Query recent telemetry data for a specific device and sensor type.

        Args:
            device_id: Identifier for the device
            sensor_type: Type of sensor to query (GPS, IMU, etc.)
            minutes_back: Number of minutes back to query

        Returns:
            Tuple of (success: bool, message: str, events: Optional[List[TelemetryEvent]])
        """
        try:
            if self.stub is None:
                return False, "Not connected", None

            # Calculate time range
            now = telemetry_pb2.Timestamp.now()
            start_time = telemetry_pb2.Timestamp(
                seconds=now.seconds - (minutes_back * 60),
                nanos=now.nanos
            )

            query = telemetry_pb2.QueryRequest(
                device_id=device_id,
                sensor_type=sensor_type,
                start_time=start_time,
                end_time=now,
                max_results=100
            )

            response = self.stub.QueryEvents(query)

            if len(response.events) > 0:
                return True, f"Retrieved {len(response.events)} events", list(response.events)
            else:
                return False, "No data found for the specified query", None

        except Exception as e:
            return False, f"Error querying telemetry: {str(e)}", None
















