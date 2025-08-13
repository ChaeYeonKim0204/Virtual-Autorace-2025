# import rospy
# from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
# from actionlib_msgs.msg import GoalStatus
# import actionlib
# import pandas as pd

# class NavigationClient:
#     def __init__(self, waypoint_file):
#         self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
#         self.client.wait_for_server()

#         # CSV 파일 읽기
#         self.waypoints = pd.read_csv(waypoint_file)

#         # 목표지점 리스트
#         self.goal_list = []

#         # CSV 데이터 → MoveBaseGoal 변환
#         for idx, row in self.waypoints.iterrows():
#             goal = MoveBaseGoal()
#             goal.target_pose.header.frame_id = 'map'
#             goal.target_pose.header.stamp = rospy.Time.now()
#             goal.target_pose.pose.position.x = row['x']
#             goal.target_pose.pose.position.y = row['y']
#             goal.target_pose.pose.orientation.z = row['orientation_z']
#             goal.target_pose.pose.orientation.w = row['orientation_w']
#             self.goal_list.append(goal)

#         self.sequence = 0
#         self.start_time = rospy.Time.now()

#     def run(self):
#         print("running waypoint")
#         # 목표 전송 상태 확인
#         if self.client.get_state() != GoalStatus.ACTIVE:
#             self.start_time = rospy.Time.now()

#             # 다음 waypoint 선택
#             if self.sequence < len(self.goal_list):
#                 rospy.loginfo(f"Sending goal {self.sequence+1}/{len(self.goal_list)}")
#                 self.client.send_goal(self.goal_list[self.sequence])
#                 self.sequence += 1
#             else:
#                 rospy.loginfo("All waypoints reached.")
#                 rospy.signal_shutdown("Navigation complete.")

#         else:
#             # 목표 도착 제한 시간 초과 시 중단
#             if (rospy.Time.now().to_sec() - self.start_time.to_sec()) > 30.0:
#                 rospy.logwarn("Timeout reached. Stopping navigation.")
#                 self.stop()

#     def stop(self):
#         self.client.cancel_all_goals()

# def main():
#     rospy.init_node('navigation_client')

#     # 방금 만든 CSV 경로 넣기
#     waypoint_file = '~/ws/waypoint_amcl_org.csv'
#     nc = NavigationClient(waypoint_file)

#     rate = rospy.Rate(1)  # 1Hz
#     while not rospy.is_shutdown():
#         nc.run()
#         rate.sleep()

# if __name__ == "__main__":
#     main()


#wego/scripts/navigation_client.py
#출발지 -> 목표지점 이동하는
import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
import actionlib

class NavigationClient:
    def __init__(self):
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        self.client.wait_for_server()

        self.goal_list = list()

        self.waypoint1 = MoveBaseGoal()
        self.waypoint1.target_pose.header.frame_id = 'map'
        self.waypoint1.target_pose.pose.position.x = 0.025463516085767933
        self.waypoint1.target_pose.pose.position.y = -0.01637579246710124
        self.waypoint1.target_pose.pose.orientation.w = 0.9999839783913462
        self.waypoint1.target_pose.pose.orientation.z = 0.0056606501937182955

        self.goal_list.append(self.waypoint1)

        # self.waypoint1 = MoveBaseGoal()
        # self.waypoint1.target_pose.header.frame_id = 'map'
        # self.waypoint1.target_pose.pose.position.x = 0.024845656602266952
        # self.waypoint1.target_pose.pose.position.y = -0.016559474250307026
        # self.waypoint1.target_pose.pose.orientation.w = 0.005685134412241484
        # self.waypoint1.target_pose.pose.orientation.z = 0.9999838394927764

        # self.goal_list.append(self.waypoint1)

        #         pose: 
        # pose: 
        #     position: 
        #     x: 0.025463516085767933
        #     y: -0.01637579246710124
        #     z: 0.0
        #     orientation: 
        #     x: 0.0
        #     y: 0.0
        #     z: 0.0056606501937182955
        #     w: 0.9999839783913462


        # pose: 
        # pose: 
        #     position: 
        #     x: 16.351945735941193
        #     y: -9.223850296288006
        #     z: 0.0
        #     orientation: 
        #     x: 0.0
        #     y: 0.0
        #     z: -0.000429277785270227
        #     w: 0.9999999078602873


        # self.waypoint2 = MoveBaseGoal()
        # self.waypoint2.target_pose.header.frame_id = 'map'
        # self.waypoint2.target_pose.pose.position.x = 16.51341876243319
        # self.waypoint2.target_pose.pose.position.y = -8.847849314248052
        # self.waypoint2.target_pose.pose.orientation.w = -0.15919003101032428
        # self.waypoint2.target_pose.pose.orientation.z = 0.9872479597481739

        # self.goal_list.append(self.waypoint2)

        self.waypoint2 = MoveBaseGoal()
        self.waypoint2.target_pose.header.frame_id = 'map'
        self.waypoint2.target_pose.pose.position.x = 16.351945735941193
        self.waypoint2.target_pose.pose.position.y = -9.223850296288006
        self.waypoint2.target_pose.pose.orientation.w = 0.9999999078602873
        self.waypoint2.target_pose.pose.orientation.z = -0.000429277785270227

        self.goal_list.append(self.waypoint2)


        self.sequence = 0
        self.start_time = rospy.Time.now()


    def run(self):
        # self.sequence = 0

        if self.client.get_state() != GoalStatus.ACTIVE:
            self.start_time = rospy.Time.now()
            self.sequence = (self.sequence+1)%2
            self.client.send_goal(self.goal_list[self.sequence])

        # else:
        #     if (rospy.Time.now().to_sec() - self.start_time.to_sec()) > 30.0:
        #         self.stop()

        # if self.client.get_state() != GoalStatus.ACTIVE:
        #     self.start_time = rospy.Time.now()
        #     self.sequence = (self.sequence + 1) % len(self.goal_list)  # len() 사용 꼭 해야 함
        #     self.client.send_goal(self.goal_list[self.sequence])


    def stop(self):
        self.client.cancel_all_goals()

def main():
    rospy.init_node('navigation_client')
    nc = NavigationClient()
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        nc.run()
        rate.sleep()


if __name__ == "__main__":
    main()