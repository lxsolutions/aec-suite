














"""
Telemetry session replay functionality for Rover Operations SDK.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Iterator

import minio
from minio.error import ResponseError

class TelemetrySession:
    """Represents a recorded telemetry session."""

    def __init__(self):
        self.session_id: str = ""
        self.device_id: str = ""
        self.start_time: datetime = None
        self.end_time: datetime = None
        self.duration_seconds: float = 0.0

        # Metadata about the recording
        self.metadata: Dict[str, str] = {}

        # List of telemetry events (lazy-loaded)
        self._events: Optional[List[Dict]] = None

    @property
    def events(self) -> List[Dict]:
        """Get all telemetry events for this session."""
        if self._events is None:
            raise ValueError("Events not loaded. Call load_events() first.")
        return self._events

class SessionReplayer:
    """
    Handles loading and playing back recorded telemetry sessions from MinIO storage.
    """

    def __init__(self, minio_endpoint: str = "localhost:9000",
                 access_key: Optional[str] = None,
                 secret_key: Optional[str] = None):
        """Initialize the replay loader.

        Args:
            minio_endpoint: Address of MinIO server (host:port)
            access_key: Access key for authentication
            secret_key: Secret key for authentication
        """
        self.minio_client = minio.Minio(
            endpoint=minio_endpoint,
            access_key=access_key or "roveradmin",
            secret_key=secret_key or "roverpassword",
            secure=False  # For development, use True in production
        )

    def list_sessions(self) -> List[str]:
        """List available telemetry session recordings.

        Returns:
            List of session IDs (file names)
        """
        try:
            bucket_name = "telemetry-recordings"
            if not self.minio_client.bucket_exists(bucket_name):
                return []

            objects = self.minio_client.list_objects(bucket_name, recursive=True)

            # Filter for JSON files that look like recordings
            session_ids = []
            for obj in objects:
                if obj.object_name.endswith('.json') and 'session-' in obj.object_name:
                    session_ids.append(obj.object_name.split('/')[-1])

            return sorted(session_ids)

        except ResponseError as e:
            print(f"Error listing sessions: {e}")
            return []

    def load_session(self, session_id: str) -> Optional[TelemetrySession]:
        """Load a telemetry session by ID.

        Args:
            session_id: Identifier for the recording (filename without extension)

        Returns:
            TelemetrySession object if successful, None otherwise
        """
        try:
            bucket_name = "telemetry-recordings"
            file_path = f"sessions/{session_id}.json"

            # Check if file exists
            if not self.minio_client.fstat_object(bucket_name, file_path):
                print(f"Session {file_path} does not exist")
                return None

            # Download the JSON content
            response = self.minio_client.get_object(bucket_name, file_path)
            session_data = json.loads(response.data.decode('utf-8'))
            response.close()
            response.release_conn()

            # Parse metadata and create session object
            session = TelemetrySession()
            session.session_id = session_id

            if 'metadata' in session_data:
                session.metadata = session_data['metadata']
                session.device_id = session.metadata.get('device_id', '')
                session.start_time = datetime.fromisoformat(session.metadata['start_time'])
                session.end_time = datetime.fromisoformat(session.metadata['end_time'])

                # Calculate duration
                if session.end_time and session.start_time:
                    session.duration_seconds = (session.end_time - session.start_time).total_seconds()

            return session

        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def load_events(self, session: TelemetrySession) -> bool:
        """Load telemetry events for a session.

        Args:
            session: TelemetrySession object to populate with events

        Returns:
            True if successful, False otherwise
        """
        try:
            bucket_name = "telemetry-recordings"
            file_path = f"sessions/{session.session_id}.json"

            # Download the JSON content
            response = self.minio_client.get_object(bucket_name, file_path)
            session_data = json.loads(response.data.decode('utf-8'))
            response.close()
            response.release_conn()

            if 'events' in session_data and isinstance(session_data['events'], list):
                session._events = session_data['events']
                return True
            else:
                print("No events found in session data")
                return False

        except Exception as e:
            print(f"Error loading events for session {session.session_id}: {e}")
            return False

    def play_session(self, session: TelemetrySession,
                    interval_seconds: float = 0.1) -> Iterator[Dict]:
        """Play back a telemetry session with timing.

        Args:
            session: Loaded TelemetrySession object
            interval_seconds: Time between events during playback (seconds)

        Returns:
            Generator yielding telemetry events at appropriate intervals

        Yields:
            Dict: Individual telemetry event data
        """
        if not session.events or len(session.events) == 0:
            raise ValueError("No events loaded for this session")

        # Sort events by timestamp if needed
        sorted_events = sorted(session.events, key=lambda x: x.get('timestamp', ''))

        start_time = datetime.fromisoformat(sorted_events[0]['timestamp'])

        for event in sorted_events:
            yield event

            # Calculate time since first event and sleep appropriately
            current_timestamp = datetime.fromisoformat(event['timestamp'])
            elapsed_seconds = (current_timestamp - start_time).total_seconds()

            if interval_seconds > 0:
                import time
                time.sleep(interval_seconds)

    def export_session(self, session: TelemetrySession,
                      output_path: str) -> bool:
        """Export a telemetry session to a local file.

        Args:
            session: Loaded TelemetrySession object
            output_path: Path where the JSON file should be saved

        Returns:
            True if successful, False otherwise
        """
        try:
            bucket_name = "telemetry-recordings"
            file_path = f"sessions/{session.session_id}.json"

            # Download the JSON content
            response = self.minio_client.get_object(bucket_name, file_path)
            session_data = json.loads(response.data.decode('utf-8'))
            response.close()
            response.release_conn()

            with open(output_path, 'w') as f:
                json.dump(session_data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error exporting session {session.session_id} to {output_path}: {e}")
            return False
















