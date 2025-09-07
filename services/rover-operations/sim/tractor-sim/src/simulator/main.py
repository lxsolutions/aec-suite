







import logging
from concurrent import futures

import grpc
from google.protobuf.empty_pb2 import Empty

# Import generated proto classes
try:
    from simulator.hello_tractor_pb2_grpc import add_HelloTractorServicer_to_server, HelloTractorServicer
    from simulator.hello_tractor_pb2 import (
        DriveCommand,
        SafetyStatus,
        DeviceStatusUpdate,
        CommandResponse,
        SafetyCommand,
        DriveStatus,
    )
except ImportError:
    # Fallback for development when protobufs aren't generated yet
    class HelloTractorServicer:
        pass

class TractorSimulator(HelloTractorServicer):
    def __init__(self):
        self.logger = logging.getLogger("tractor-sim")
        self.current_speed = 0.0
        self.steer_angle = 0.0
        self.position = {
            'latitude': 37.7749,   # Starting position in San Francisco
            'longitude': -122.4194,
            'altitude': 15.0,
            'heading': 0.0,       # degrees from north (0-360)
        }
        self.is_moving = False
        self.e_stop_active = False

    def Drive(self, request: DriveCommand, context) -> CommandResponse:
        """Handle drive commands and return current status."""
        if self.e_stop_active:
            self.logger.warning("Drive command ignored - E-stop active")
            return CommandResponse(
                success=False,
                error_message="E-stop active - commands blocked",
            )

        # Execute the drive command
        self.current_speed = request.speed
        self.steer_angle = request.steer_angle

        if self.current_speed != 0:
            self.is_moving = True
        else:
            self.is_moving = False

        self._update_position()

        status_update = DeviceStatusUpdate(
            session_id="simulated-session",
            drive_status=DriveStatus(
                current_speed=self.current_speed,
                steer_angle=self.steer_angle,
                is_moving=self.is_moving,
                emergency_stop_active=self.e_stop_active,

                latitude=self.position['latitude'],
                longitude=self.position['longitude'],
                altitude=float(self.position['altitude']),
                heading_degrees=float(self.position['heading']),

            ),
        )

        self.logger.info(f"Executed drive command: speed={self.current_speed}, steer={self.steer_angle}")
        return CommandResponse(
            success=True,
            response_data=status_update.drive_status
        )

    def Safety(self, request: SafetyCommand, context) -> CommandResponse:
        """Handle safety commands like E-stop."""
        if request.e_stop_activate:
            self.e_stop_active = True
            self.current_speed = 0.0  # Immediate stop

            self.logger.warning("E-STOP ACTIVATED! Tractor halted.")
            return CommandResponse(
                success=True,
                response_data=SafetyStatus(e_stop_active=self.e_stop_active)
            )

        if request.e_stop_release:
            self.e_stop_active = False
            self.logger.info("E-stop released")

        return CommandResponse(success=True)

    def GetStatus(self, request: Empty, context) -> DeviceStatusUpdate:
        """Return current device status."""
        status_update = DeviceStatusUpdate(
            session_id="simulated-session",
            drive_status=DriveStatus(
                current_speed=self.current_speed,
                steer_angle=self.steer_angle,
                is_moving=self.is_moving and not self.e_stop_active,
                emergency_stop_active=self.e_stop_active,

                latitude=self.position['latitude'],
                longitude=self.position['longitude'],
                altitude=float(self.position['altitude']),
                heading_degrees=float(self.position['heading']),

            ),
        )
        return status_update

    def _update_position(self):
        """Simulate position update based on current speed and heading."""
        if self.e_stop_active or not self.is_moving:
            return  # Don't move if stopped or in E-stop mode

        import math
        # Simple movement simulation (naive - for real sim would need proper geospatial calculations)
        self.position['latitude'] += self.current_speed * 0.01 * math.cos(self.position['heading'] * (math.pi / 180))
        self.position['longitude'] += self.current_speed * 0.01 * math.sin(self.position['heading'] * (math.pi / 180))

        # Update heading based on steer angle
        if self.steer_angle != 0:
            self.position['heading'] = self._normalize_heading(
                self.position['heading'] + self.steer_angle * 0.5
            )

    def _normalize_heading(self, heading):
        """Normalize heading to range [0, 360)."""
        while heading < 0:
            heading += 360
        while heading >= 360:
            heading -= 360
        return heading

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("tractor-sim")

    # Set up gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_HelloTractorServicer_to_server(TractorSimulator(), server)

    listen_addr = '[::]:50053'
    logger.info(f"Starting tractor simulator on {listen_addr}")
    server.add_insecure_port(listen_addr)
    server.start()

    try:
        while True:
            # Simulate periodic telemetry updates
            import time
            time.sleep(60)  # Keep server running indefinitely
    except KeyboardInterrupt:
        logger.info("Shutting down simulator...")
    finally:
        server.stop(None)

if __name__ == "__main__":
    main()







