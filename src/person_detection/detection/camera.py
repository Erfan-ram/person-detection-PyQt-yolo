"""Camera management and detection."""

import subprocess
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QComboBox, QMessageBox


class CameraChecker:
    """Manages camera detection and availability checking."""
    
    def __init__(self, combo_obj: QComboBox):
        self.cameras = {}
        self.combo_obj = combo_obj
        self.timer = None

    def cam_available(self):
        """Check for available cameras and update the combo box."""
        try:
            result = subprocess.run(['v4l2-ctl', '--list-devices'], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                lines = output.split('\n')
                new_cameras = {}
                camera_name = None

                for i, line in enumerate(lines):
                    if "usb-" in line:
                        camera_name = lines[i].strip()
                        address = lines[i+1].strip()
                        new_cameras[camera_name] = address

                # Check for new cameras
                for camera in new_cameras.keys():
                    if camera not in self.cameras:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Icon.Information)
                        msg.setText(f"New camera detected: {camera}")
                        msg.setWindowTitle("Camera Detection")
                        msg.exec()
                        self.combo_obj.addItem(camera)

                # Check for removed cameras
                for camera in self.cameras.keys():
                    if camera not in new_cameras:
                        self.combo_obj.removeItem(self.combo_obj.findText(camera))

                self.cameras = new_cameras.copy()

            else:
                print("Error running v4l2-ctl")
                self.cameras = {}
        except Exception as e:
            print(f"Exception occurred: {e}")
            self.cameras = {}

    def start(self):
        """Start the camera checking timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.cam_available)
        self.timer.start(1000)

    def get_cameras(self):
        """Get the dictionary of available cameras."""
        return self.cameras