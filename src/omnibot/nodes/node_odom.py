#! /usr/bin/python3
from __future__ import division

import rospy
from nav_msgs.msg import Odometry
from std_msgs.msg import Int32
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf.broadcaster import TransformBroadcaster
from tf.transformations import quaternion_from_euler, euler_from_quaternion

from omnibot import pose, odometry
from omnibot.msg import MotorSpeed

class OdometryNode:

    def __init__(self):
        self.odometry = odometry.Odometry()

    def main(self):
        self.odomPub = rospy.Publisher('odom', Odometry, queue_size=10)
        self.tfPub = TransformBroadcaster()

        rospy.init_node('node_odometry')
        self.nodeName = rospy.get_name()
        rospy.loginfo("{0} started".format(self.nodeName))
        rospy.Subscriber("initialpose", PoseWithCovarianceStamped,
                         self.on_initial_pose)
        self.rate = float(rospy.get_param('~rate', 10.0))
        self.baseFrameID = rospy.get_param('~base_frame_id', 'base_link')
        self.odomFrameID = rospy.get_param('~odom_frame_id', 'odom')
        self.odometry.setTime(rospy.get_time())
        rate = rospy.Rate(self.rate)
        while not rospy.is_shutdown():
            self.publish()
            rate.sleep()

    def publish(self):
        self.odometry.updatePose(rospy.get_time())
        now = rospy.get_rostime()
        pose = self.odometry.getPose()

        q = quaternion_from_euler(0, 0, pose.theta)
        self.tfPub.sendTransform(
            (pose.x, pose.y, 0),
            (q[0], q[1], q[2], q[3]),
            now,
            self.baseFrameID,
            self.odomFrameID
        )

        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = self.odomFrameID
        odom.child_frame_id = self.baseFrameID
        odom.pose.pose.position.x = pose.x
        odom.pose.pose.position.y = pose.y
        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]
        odom.twist.twist.linear.x = pose.xVel
        odom.twist.twist.angular.z = pose.thetaVel
        self.odomPub.publish(odom)

    def on_initial_pose(self, msg):
        q = [msg.pose.pose.orientation.x,
             msg.pose.pose.orientation.x,
             msg.pose.pose.orientation.x,
             msg.pose.pose.orientation.w]
        roll, pitch, yaw = euler_from_quaternion(q)

        pose = pose.Pose()
        pose.x = msg.pose.pose.position.x
        pose.y = msg.pose.pose.position.y
        pose.theta = yaw

        rospy.loginfo('Setting initial pose to %s', pose)
        self.odometry.setPose(pose)

if __name__ == '__main__':
    try:
        rospy.loginfo('running node odometry')
        node = OdometryNode()
        node.main()
    except rospy.ROSInterruptException:
        pass