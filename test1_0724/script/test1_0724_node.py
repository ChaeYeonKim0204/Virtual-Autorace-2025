import rospy
from std_msgs.msg import Float64
from sensor_msgs.msg import CompressedImage
import cv2
from cv_bridge import CvBridge
import numpy as np
import time
import math

class Control_pub():
    def __init__(self):
        rospy.init_node("control_pub_node")
        # 카메라 이미지 구독
        self.steer_pub = rospy.Publisher("/commands/servo/position", Float64, queue_size = 10)
        self.speed_pub = rospy.Publisher("/commands/motor/speed", Float64, queue_size = 10)
        self.img = None
        self.sub = rospy.Subscriber("/image_jpeg/compressed", CompressedImage, self.image_callback)
        self.bridge = CvBridge()

        self.last_error = 0.0
        self.last_time = 0.0

        self.steer_msg = Float64()
        self.speed_msg = Float64()
        self.rate = rospy.Rate(1)
        
        # 📷 실제 영상에서 사다리꼴 모양으로 차선 포함 영역 넓게 지정
        self.src_pts = np.float32([
            [50, 460],     # 왼쪽 아래
            [160, 320],    # 왼쪽 위
            [480, 320],    # 오른쪽 위
            [590, 460]     # 오른쪽 아래
        ])

        # 📐 변환 후에도 영상 전체를 너무 꽉 채우지 않도록 여유 있게 설정
        self.dst_pts = np.float32([
            [100, 460],    # 왼쪽 아래
            [100, 0],      # 왼쪽 위
            [540, 0],      # 오른쪽 위
            [540, 460]     # 오른쪽 아래
        ])

    def image_callback(self, data):
        self.img = self.bridge.compressed_imgmsg_to_cv2(data, "bgr8")

    def callback(self):
        if self.img is None:
            return
        # undistorted = cv2.undistort(self.img, self.mtx, self.dist, None, self.mtx)
        bird_img = warp_perspective(self.img, self.src_pts, self.dst_pts)

        cv2.imshow("bird",bird_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        filtered_img = filter_color(bird_img)
        roi_img = filtered_img
        rightbase, leftbase = plothistogram(roi_img)
        out_img, center_fitx = sliding_window(roi_img, rightbase, leftbase)
        steering_angle = get_steering_angle(filtered_img, center_fitx)
        steering, throttle, self.last_error, self.last_time = compute_pd_control(steering_angle, self.last_error, self.last_time)
        self.speed_msg.data = throttle
        self.steer_msg.data = steering
        self.speed_pub.publish(self.speed_msg)
        self.steer_pub.publish(self.steer_msg)
        self.rate.sleep()

def main():
    control = Control_pub()
    while not rospy.is_shutdown():
        control.callback()
        cv2.destroyAllWindows()

def warp_perspective(img, src_points, dst_points):
    h, w = img.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32(src_points), np.float32(dst_points))
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)
    return warped

def filter_color(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 흰색 임계값(값 수정 필요)
    lower_white = np.array([0, 0, 200], dtype=np.uint8)
    upper_white = np.array([180, 60, 255], dtype=np.uint8)
    filtered_img = cv2.inRange(hsv, lower_white, upper_white)
    
    cv2.imshow("Binary Image", filtered_img)
    # cv2.waitKey(1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return filtered_img

# def roi(filtered_img):
#     height, width = filtered_img.shape[:2]
#     x_center = width / 2
        
#     mask = np.zeros_like(filtered_img)
#     trap_bottom_width = 1
#     trap_top_width = 0.65
#     trap_height = 0.85
        
#     bottom_left = (int(width * (0.5 - trap_bottom_width / 2)), height)
#     bottom_right = (int(width * (0.5 + trap_bottom_width / 2)), height)
#     top_left = (int(width * (0.5 - trap_top_width / 2)), int(height * (1 - trap_height)))
#     top_right = (int(width * (0.5 + trap_top_width / 2)), int(height * (1 - trap_height)))
#     roi_point = np.array([[bottom_left, bottom_right, top_right, top_left]], dtype=np.int32)
#     cv2.fillConvexPoly(mask, roi_point, 255)
#     roi_img = cv2.bitwise_and(filtered_img, mask)

#     print(f"roi_point: {roi_point}")

#     cv2.imshow("roi_img", roi_img)
#     cv2.waitKey(1)
#     # cv2.waitKey(0)
#     # cv2.destroyAllWindows()
#     return roi_img, [bottom_left, bottom_right, top_left, top_right]


def plothistogram(roi_img):
    plothistogram = np.sum(roi_img, axis=0)
    if plothistogram.size == 0 or np.all(plothistogram == 0):
        print("[경고] 히스토그램이 비었거나 모든 값이 0입니다.")
        return None, None
    
    midpoint = len(plothistogram)//2
    leftbase = np.argmax(plothistogram[:midpoint])
    rightbase = np.argmax(plothistogram[midpoint:]) + midpoint

    # # --- 추가: 위치 기반 검증 (비정상적인 경우 None 처리) ---
    # img_width = roi_img.shape[1]
    # min_margin = int(img_width * 0.05)  # 왼쪽 차선 최소 허용 (화면의 5% 이상)
    # max_margin = int(img_width * 0.95)  # 오른쪽 차선 최대 허용 (화면의 95% 이하)
    # center_min = int(img_width * 0.35)   # 중앙 근처 최소값
    # center_max = int(img_width * 0.65)   # 중앙 근처 최대값

    # # 왼쪽 차선이 너무 오른쪽(중앙 근처)에 있으면 → 검출 실패로 간주
    # if leftbase > center_min:
    #     print("[판단] 왼쪽 차선 검출 실패 (중앙 쪽으로 너무 치우침)")
    #     leftbase = None
    # # 오른쪽 차선이 너무 왼쪽(중앙 근처)에 있으면 → 검출 실패로 간주
    # if rightbase < center_max:
    #     print("[판단] 오른쪽 차선 검출 실패 (중앙 쪽으로 너무 치우침)")
    #     rightbase = None
    # # 이미지 영역 벗어난 값 무효화
    # if leftbase is not None and (leftbase < min_margin or leftbase > max_margin):
    #     print("[판단] 왼쪽 차선 위치가 허용 범위 벗어남")
    #     leftbase = None
    # if rightbase is not None and (rightbase < min_margin or rightbase > max_margin):
    #     print("[판단] 오른쪽 차선 위치가 허용 범위 벗어남")
    #     rightbase = None
    # # --- 추가 끝 ---

    # # --- 반환 조건 ---
    # if rightbase is None and leftbase is None:
    #     print("둘 다 없음")
    #     return None, None
    # elif leftbase is None:
    #     print("왼쪽 차선 없음")
    #     return rightbase, None
    # elif rightbase is None:
    #     print("오른쪽 차선 없음")
    #     return None, leftbase
    # else:
    #     print("둘 다 검출")
    return rightbase, leftbase


def sliding_window(roi_img, rightbase, leftbase):
    out_img = np.dstack((roi_img, roi_img, roi_img)).astype(np.uint8)
    nwindows = 12
    window_height = int(roi_img.shape[0] // nwindows)
    margin = 60
    minpix = 20

    nonzero = roi_img.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    # # --- 추가: None 처리 (기본값 설정) ---
    # midpoint = roi_img.shape[1] // 2
    # if leftbase is None:
    #     print("[대체] 왼쪽 차선 없음 → 기본값 사용")
    #     leftbase = midpoint - 100

    # if rightbase is None:
    #     print("[대체] 오른쪽 차선 없음 → 기본값 사용")
    #     rightbase = midpoint + 100
    # # --- 추가 끝 ---
    left_current = leftbase
    right_current = rightbase

    left_lanes = []
    right_lanes = []

    for window in range(nwindows):
        win_y_low = roi_img.shape[0] - ((window+1) * window_height)
        win_y_high = roi_img.shape[0] - window * window_height

        win_xleft_low = left_current - margin
        win_xleft_high = left_current + margin
        win_xright_low = right_current - margin
        win_xright_high = right_current + margin

        cv2.rectangle(out_img, (win_xleft_low, win_y_low), (win_xleft_high, win_y_high), (0, 255, 0), 2)
        cv2.rectangle(out_img, (win_xright_low, win_y_low), (win_xright_high, win_y_high), (0, 255, 0), 2)
        cv2.imshow("window", out_img)
        cv2.waitKey(100)

        #-------------윈도우 내에 포함되는 픽셀 검출------

        # good_left_inds: 왼쪽 차선 픽셀 인덱스
        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
                          (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
                           (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]

        left_lanes.append(good_left_inds)
        right_lanes.append(good_right_inds)
        
        # ---------------슬라이딩 윈도우 중심점 업데이트-----------
        # 차선 픽셀 인덱스에서 x좌표만 뽑아서(nonzerox) x좌표들의 평균을 구하고(mean) 다음 윈도우 x좌표 중심(__current)으로 사용
        if len(good_left_inds) > minpix:
            left_current = int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            right_current = int(np.mean(nonzerox[good_right_inds]))

    left_lanes = np.concatenate(left_lanes)
    right_lanes = np.concatenate(right_lanes)

    leftx = nonzerox[left_lanes]
    lefty = nonzeroy[left_lanes]
    rightx = nonzerox[right_lanes]
    righty = nonzeroy[right_lanes]

    # 차선 개수 판별 and heading 점 개산
    if len(leftx) == 0 or len(lefty) == 0:
        right_fit = np.polyfit(righty, rightx, 2)
        ploty = np.linspace(0, roi_img.shape[0]-1, roi_img.shape[0])

        right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]
        out_img[nonzeroy[right_lanes], nonzerox[right_lanes]] = [255, 0, 0]
        for i in range(len(ploty)-1):
            pt1 = (int(right_fitx[i]), int(ploty[i]))
            pt2 = (int(right_fitx[i+1]), int(ploty[i+1]))
            cv2.line(out_img, pt1, pt2, (255, 255, 0), 3)
        
        return out_img
        
    elif len(rightx) == 0 or len(righty) == 0:
        left_fit = np.polyfit(lefty, leftx, 2)
        ploty = np.linspace(0, roi_img.shape[0]-1, roi_img.shape[0])

        left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
        out_img[nonzeroy[left_lanes], nonzerox[left_lanes]] = [255, 0, 0]
        for i in range(len(ploty)-1):
            pt1 = (int(left_fitx[i]), int(ploty[i]))
            pt2 = (int(left_fitx[i+1]), int(ploty[i+1]))
            cv2.line(out_img, pt1, pt2, (255, 255, 0), 3)
        
        return out_img
    
    else: #(len(leftx) != 0 and len(rightx) != 0):
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)

        ploty = np.linspace(0, roi_img.shape[0]-1, roi_img.shape[0])
        left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
        right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]

        out_img[nonzeroy[left_lanes], nonzerox[left_lanes]] = [255, 0, 0]
        out_img[nonzeroy[right_lanes], nonzerox[right_lanes]] = [0, 0, 255]
        for i in range(len(ploty)-1):
            pt1 = (int(left_fitx[i]), int(ploty[i]))
            pt2 = (int(left_fitx[i+1]), int(ploty[i+1]))
            cv2.line(out_img, pt1, pt2, (255, 255, 0), 3)
            pt1 = (int(right_fitx[i]), int(ploty[i]))
            pt2 = (int(right_fitx[i+1]), int(ploty[i+1]))
            cv2.line(out_img, pt1, pt2, (0, 255, 255), 3)

        # --- 여기서 중앙선 추가 ---
        center_fitx = (left_fitx + right_fitx) / 2
        for i in range(len(ploty)-1):
            pt1 = (int(center_fitx[i]), int(ploty[i]))
            pt2 = (int(center_fitx[i+1]), int(ploty[i+1]))
            cv2.line(out_img, pt1, pt2, (0, 255, 0), 3)  # 녹색으로 중앙선 표시
            # cv2.line(out_img, (center_fitx[0],roi_img.shape[0]//2), (center_fitx[0],roi_img.shape[0]//2), (255, 255, 0), 3)
        cv2.imshow("center_line", out_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print(f"중앙점: {center_fitx[0]}")
        return out_img, center_fitx[0]
    
def get_steering_angle(filtered_img, center_fitx):
    height, width = filtered_img.shape[:2]
    mid = width // 2
    x_offset = center_fitx - mid
    y_offset =  height // 2
    steering_angle_radian = math.atan2(x_offset, y_offset)
    steering_angel_deg = steering_angle_radian / math.pi * 180
    steering_angle = 90 - steering_angel_deg
    print(f"{height}, {width}")
    return steering_angle

def compute_pd_control(steering_angle, last_error, last_time, kp=0.4, kd_ratio=0.65, base_speed=0.3):
    now = time.time()
    dt = now - last_time if last_time != 0 else 1e-3
    error = abs(steering_angle - 90)

    deviation = steering_angle - 90
    if -5 < deviation < 5:
        steering = 0.0
        error = 0.0
    else:
        steering = deviation / 180.0
        steering = max(min(steering, 0.4), -0.4)
        steering -= 0.23

    kd = kp * kd_ratio
    derivative = kd * (error - last_error) / dt
    proportional = kp * error
    pd_value = base_speed + derivative + proportional
    throttle = max(min(abs(pd_value), 0.25), 0.25)

    return steering, throttle, error, now


if __name__ =="__main__":
    main()