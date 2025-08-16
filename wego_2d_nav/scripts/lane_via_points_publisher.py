# #!/usr/bin/env python
# """
# Lane Via-Points Publisher for Wego 2D Navigation
# 차선 중심선을 TEB Local Planner의 via-points로 발행하는 노드
# """

# import rospy
# import math
# from nav_msgs.msg import Path
# from geometry_msgs.msg import PoseStamped, Twist
# from sensor_msgs.msg import Image, LaserScan
# from std_msgs.msg import Header, Bool

# class WegoLaneViaPointsPublisher:
#     def __init__(self):
#         rospy.loginfo("Initializing Wego Lane Via-Points Publisher...")
        
#         # Parameters
#         self.update_rate = rospy.get_param('~update_rate', 10.0)
#         self.enable_via_points = rospy.get_param('~enable_via_points', True)
#         self.max_via_points = rospy.get_param('~max_via_points', 10)
#         self.via_point_spacing = rospy.get_param('~via_point_spacing', 1.0)  # meters
        
#         # Publishers
#         self.via_points_pub = rospy.Publisher(
#             '/move_base/TebLocalPlannerROS/via_points',
#             Path, 
#             queue_size=1
#         )
        
#         # Subscribers (차선 검출 데이터를 받기 위한 토픽들)
#         # 실제 차선 검출 노드의 출력에 맞게 수정하세요
#         # self.image_sub = rospy.Subscriber('/camera/image_raw', Image, self.image_callback)
#         # self.lane_sub = rospy.Subscriber('/lane_detection/centerline', Path, self.lane_callback)
        
#         # Enable/disable service (optional)
#         self.enable_sub = rospy.Subscriber('~enable', Bool, self.enable_callback)
        
#         # State variables
#         self.current_lane_centerline = []
#         self.last_via_points_time = rospy.Time.now()
        
#         rospy.loginfo("Wego Lane Via-Points Publisher initialized")

#     def enable_callback(self, msg):
#         """Enable/disable via-points publishing"""
#         self.enable_via_points = msg.data
#         rospy.loginfo(f"Lane via-points {'enabled' if self.enable_via_points else 'disabled'}")


#     def lane_callback(self, msg):
#         """외부 차선 검출 노드로부터 차선 중심선 수신"""
#         if not self.enable_via_points:
#             return
            
#         # 수신된 차선 중심선을 via-points로 변환
#         lane_points = [(pose.pose.position.x, pose.pose.position.y) 
#                       for pose in msg.poses]
#         self.current_lane_centerline = lane_points
        
#     def detect_lane_from_dummy_data(self):
#         """더미 차선 데이터 생성 (테스트용)"""
#         # 실제 운용시에는 이 함수를 제거하고 실제 차선 검출 사용
#         current_time = rospy.Time.now().to_sec()
        
#         # 곡선 차선 시뮬레이션
#         lane_points = []
#         for i in range(self.max_via_points):
#             x = i * self.via_point_spacing
#             y = 0.3 * math.sin(0.1 * x + current_time * 0.5)  # 시간에 따라 변하는 곡선
#             lane_points.append((x, y))
            
#         return lane_points

#     def filter_and_subsample_lane(self, lane_points):
#         """차선 점들을 필터링하고 적절한 간격으로 서브샘플링"""
#         if not lane_points:
#             return []
            
#         filtered_points = []
#         prev_point = None
        
#         for point in lane_points:
#             if prev_point is None:
#                 filtered_points.append(point)
#                 prev_point = point
#                 continue
                
#             # 최소 거리 체크
#             dist = math.sqrt((point[0] - prev_point[0])**2 + 
#                            (point[1] - prev_point[1])**2)
            
#             if dist >= self.via_point_spacing:
#                 filtered_points.append(point)
#                 prev_point = point
                
#         return filtered_points[:self.max_via_points]

#     def calculate_heading_angle(self, current_point, next_point):
#         """두 점 사이의 방향각 계산"""
#         dx = next_point[0] - current_point[0]
#         dy = next_point[1] - current_point[1]
#         return math.atan2(dy, dx)

#     def publish_lane_via_points(self, lane_points):
#         """차선 중심선을 nav_msgs/Path로 발행"""
#         if not lane_points or not self.enable_via_points:
#             # 빈 path 발행 (via-points 비활성화)
#             empty_path = Path()
#             empty_path.header.stamp = rospy.Time.now()
#             empty_path.header.frame_id = "map"
#             self.via_points_pub.publish(empty_path)
#             return

#         # 필터링 및 서브샘플링
#         filtered_points = self.filter_and_subsample_lane(lane_points)
        
#         if not filtered_points:
#             return
            
#         # nav_msgs/Path 메시지 생성
#         path_msg = Path()
#         path_msg.header.stamp = rospy.Time.now()
#         path_msg.header.frame_id = "map"  # 또는 "odom"
        
#         for i, point in enumerate(filtered_points):
#             pose_stamped = PoseStamped()
#             pose_stamped.header = path_msg.header
            
#             # 위치 설정
#             pose_stamped.pose.position.x = point[0]
#             pose_stamped.pose.position.y = point[1]
#             pose_stamped.pose.position.z = 0.0
            
#             # 방향 설정
#             if i < len(filtered_points) - 1:
#                 yaw = self.calculate_heading_angle(point, filtered_points[i+1])
#                 pose_stamped.pose.orientation.z = math.sin(yaw / 2.0)
#                 pose_stamped.pose.orientation.w = math.cos(yaw / 2.0)
#             else:
#                 # 마지막 점은 이전 방향 유지
#                 pose_stamped.pose.orientation.w = 1.0
                
#             path_msg.poses.append(pose_stamped)
            
#         self.via_points_pub.publish(path_msg)
#         rospy.logdebug(f"Published {len(path_msg.poses)} lane via-points")

#     def run(self):
#         """메인 실행 루프"""
#         rate = rospy.Rate(self.update_rate)
#         rospy.loginfo("Wego Lane Via-Points Publisher started")
        
#         while not rospy.is_shutdown():
#             try:
#                 # 1. 차선 중심선 획득
#                 if self.current_lane_centerline:
#                     # 외부 노드에서 수신한 차선 데이터 사용
#                     lane_centerline = self.current_lane_centerline
#                 else:
#                     # 더미 데이터 사용 (테스트/시뮬레이션용)
#                     lane_centerline = self.detect_lane_from_dummy_data()
                
#                 # 2. Via-points로 발행
#                 self.publish_lane_via_points(lane_centerline)
                
#                 # 3. 주기적 로그
#                 current_time = rospy.Time.now()
#                 if (current_time - self.last_via_points_time).to_sec() > 5.0:
#                     rospy.loginfo(f"Lane via-points: {'enabled' if self.enable_via_points else 'disabled'}, "
#                                 f"points: {len(lane_centerline)}")
#                     self.last_via_points_time = current_time
                    
#             except Exception as e:
#                 rospy.logerr(f"Error in lane via-points publisher: {e}")
                
#             rate.sleep()

# if __name__ == "__main__":
#     try:
#         rospy.init_node('wego_lane_via_points_publisher')
#         publisher = WegoLaneViaPointsPublisher()
#         publisher.run()
#     except rospy.ROSInterruptException:
#         rospy.loginfo("Wego Lane Via-Points Publisher shutdown")