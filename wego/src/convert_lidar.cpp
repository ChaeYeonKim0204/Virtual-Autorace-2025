
#include <vector>
#include <algorithm>
#include <memory>

// ROS 헤더 및 LaserScan 메시지 사용
#include "ros/ros.h"
#include "sensor_msgs/LaserScan.h"

using namespace std;

// LaserScan 데이터를 변환해서 퍼블리시하는 노드 클래스
class LidarConvert : public ros::NodeHandle {
public:
    // 생성자
    LidarConvert() {
        // "lidar2D" 토픽을 구독하고 lidarCallback 함수로 콜백 처리
        this->lidar_sub_ = this->subscribe("lidar2D", 10, &LidarConvert::lidarCallback, this);
        // 처리된 데이터를 "scan"이라는 이름의 토픽으로 퍼블리시
        this->lidar_pub_ = this->advertise<sensor_msgs::LaserScan>("scan", 10);
    }

private:
    ros::Publisher lidar_pub_;           // 퍼블리셔 객체 (변환된 LaserScan 발행)
    ros::Subscriber lidar_sub_;          // 서브스크라이버 객체 (원본 LaserScan 수신)
    bool init_flag_ = false;             // 메시지 초기화 여부 체크 플래그
    sensor_msgs::LaserScan scan_msg_;    // 퍼블리시할 메시지 객체

    // LaserScan 메시지를 수신했을 때 호출되는 콜백 함수
    void lidarCallback(const sensor_msgs::LaserScan::ConstPtr& msg) {
        // 처음 수신된 메시지를 기반으로 고정값 초기화
        if (!this->init_flag_) {
            this->scan_msg_.header.frame_id = msg->header.frame_id;
            this->scan_msg_.angle_min = msg->angle_min;
            this->scan_msg_.angle_max = msg->angle_max;
            this->scan_msg_.angle_increment = msg->angle_increment;
            this->scan_msg_.time_increment = msg->time_increment;
            this->scan_msg_.scan_time = msg->scan_time;
            this->scan_msg_.range_min = msg->range_min;
            this->scan_msg_.range_max = msg->range_max;
            this->scan_msg_.ranges.resize(msg->ranges.size());  // ranges 벡터 크기 설정
            this->init_flag_ = true;  // 초기화 완료 플래그 설정
        }

        // 현재 시각으로 타임스탬프 갱신
        this->scan_msg_.header.stamp = ros::Time::now();

        // msg->ranges의 앞쪽 180개 값을 뒤집어서 scan_msg에 복사
        std::transform(msg->ranges.begin(), msg->ranges.begin() + 180,
                       scan_msg_.ranges.begin() + 180,
                       [](auto value) { return value; });

        // msg->ranges의 뒤쪽 값을 그대로 앞쪽에 복사
        std::transform(msg->ranges.begin() + 180, msg->ranges.end(),
                       scan_msg_.ranges.begin(),
                       [](auto value) { return value; });

        // 변환된 데이터를 퍼블리시
        this->lidar_pub_.publish(scan_msg_);
    }
};

int main(int argc, char ** argv)
{
    ros::init(argc, argv, "lidar_convert");
    auto lidar_convert=make_shared<LidarConvert>();
    ros::spin();

    return 0;
}