#!/usr/bin/env python3
"""
A ROS node for publishing visuotactile images.
"""
__author__ = 'Paul-Otto Müller'
__date__ = '13.03.2023'

import numpy as np

import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

import canfnet.visuotactile_sensor.visuotactile_interface as vistac_interface
from canfnet.utils.utils import PrintColors

VISTAC_DEVICE: str = rospy.get_param('/visuotactile_sensor_node/tactile_device', 'GelSightMini')
TACTILE_DEVICE_PATH: str = rospy.get_param('/visuotactile_sensor_node/tactile_device_path', '/dev/video0')
DIGIT_SERIAL_NR: str = rospy.get_param('/visuotactile_sensor_node/digit_serial', 'D20025')
TACTILE_CAM_UNDISTORT: bool = rospy.get_param('/visuotactile_sensor_node/tactile_cam_undistort', True)


if __name__ == '__main__':
    bridge: CvBridge = CvBridge()
    pub_rate: int = 60
    visuotactile_device: vistac_interface.VistacInterface = vistac_interface.VistacInterface('V')
    if VISTAC_DEVICE == 'DIGIT':
        pub_rate = 60
        visuotactile_device = vistac_interface.DIGIT(serial_nr=DIGIT_SERIAL_NR, undistort_image=None)
    elif VISTAC_DEVICE == 'GelSightMini':
        pub_rate = 25
        visuotactile_device = vistac_interface.GelSightMini(device_path=TACTILE_DEVICE_PATH,
                                                            undistort_image=TACTILE_CAM_UNDISTORT)

    visuotactile_device.connect()

    pub: rospy.Publisher = rospy.Publisher('/canfnet/visuotactile_image', Image, queue_size=pub_rate)
    rospy.init_node('visuotactile_sensor_node', anonymous=True)
    rospy.loginfo(f"{PrintColors.OKBLUE} [VisuotactileSensorNode] Node has been initialized. {PrintColors.ENDC}")

    rate = rospy.Rate(pub_rate)
    while not rospy.is_shutdown():
        image_: np.ndarray = visuotactile_device.get_image()
        pub.publish(bridge.cv2_to_imgmsg(image_, encoding='rgb8'))
        rate.sleep()
