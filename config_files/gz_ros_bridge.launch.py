from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    image_topic = LaunchConfiguration('image_topic')
    camera_info_topic = LaunchConfiguration('camera_info_topic')
    imu_topic = LaunchConfiguration('imu_topic')
    optical_frame = LaunchConfiguration('optical_frame')

    return LaunchDescription([
        DeclareLaunchArgument(
            'image_topic',
            default_value='/world/default/model/x500_0/link/camera_link/sensor/camera/image'
        ),
        DeclareLaunchArgument(
            'camera_info_topic',
            default_value='/world/default/model/x500_0/link/camera_link/sensor/camera/camera_info'
        ),
        DeclareLaunchArgument(
            'imu_topic',
            default_value='/world/default/model/x500_0/link/imu_link/sensor/imu/imu'
        ),
        DeclareLaunchArgument(
            'optical_frame',
            default_value='camera_optical_frame'
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='clock_bridge',
            output='screen',
            arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='camera_image_bridge',
            output='screen',
            arguments=[[
                image_topic,
                '@sensor_msgs/msg/Image[gz.msgs.Image'
            ]],
            parameters=[{'override_frame_id': optical_frame}],
            remappings=[(image_topic, '/vio/camera/image_raw')],
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='camera_info_bridge',
            output='screen',
            arguments=[[
                camera_info_topic,
                '@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo'
            ]],
            parameters=[{'override_frame_id': optical_frame}],
            remappings=[(camera_info_topic, '/vio/camera/camera_info')],
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='imu_bridge',
            output='screen',
            arguments=[[
                imu_topic,
                '@sensor_msgs/msg/Imu[gz.msgs.IMU'
            ]],
            remappings=[(imu_topic, '/vio/imu')],
        ),
    ])