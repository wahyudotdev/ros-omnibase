from omnibot.msg import MotorEncoder
import math

from omnibot.pose import Pose

sqrt3 = 1.73205080757


class Odometry:
    def __init__(self, d_wheel, base_wheel, ppr) -> None:
        self.pose = Pose()
        self.last_pose = Pose()
        self.last_time = 0
        self.d_wheel = d_wheel
        self.base_wheel = base_wheel
        self.ppr = ppr
        self.m_a: float = 0.0
        self.m_b: float = 0.0
        self.m_c: float = 0.0
        self.cmp = 0

    def set_time(self, time):
        self.last_time = time

    def update_encoder(self, en_msg: MotorEncoder):
        self.v1 = (en_msg.en_a / self.ppr) * math.pi * self.d_wheel
        self.v2 = (en_msg.en_c / self.ppr) * math.pi * self.d_wheel
        self.v3 = (en_msg.en_b / self.ppr) * math.pi * self.d_wheel

    def update_pose(self, new_time):
        delta_time = new_time - self.last_time
        if delta_time <= 0:
            delta_time = 1
        x = (2 * self.v2 - self.v1 - self.v3)/3
        y = (sqrt3 * self.v3 - sqrt3 * self.v1)/3

        # self.pose.theta = ((self.m_a + self.m_c + self.m_b) / (self.base_wheel * 3))
        self.pose.theta = self.cmp
        self.pose.x = -1 * (math.cos(self.cmp) * x - math.sin(self.cmp) * y)
        self.pose.y = -1 * (math.sin(self.cmp) * x + math.cos(self.cmp) * y)
        # self.pose.theta = ((self.v1 + self.v2 + self.v3) / (self.base_wheel * 3))

        self.pose.xVel = abs((self.pose.x - self.last_pose.x) / delta_time)
        self.pose.yVel = abs((self.pose.y - self.last_pose.y) / delta_time)
        self.pose.thetaVel = abs(
            (self.pose.theta - self.last_pose.thetaVel)/delta_time)
        self.last_pose.y = self.pose.y
        self.last_pose.x = self.pose.x
        self.last_pose.theta = self.pose.theta
        self.last_time = new_time

    def get_pose(self) -> Pose:
        return self.pose

    def set_pose(self, pose):
        self.pose = pose

    def update_compass(self, cmp):
        self.cmp = cmp * math.pi / 180
