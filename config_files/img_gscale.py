import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class GrayscaleRepublisher(Node):
    def __init__(self):
        super().__init__('grayscale_republisher')

        self.bridge = CvBridge()

        self.sub = self.create_subscription(
            Image,
            '/vio/camera/image_raw',
            self.image_callback,
            10
        )

        self.pub = self.create_publisher(
            Image,
            '/vio/camera/image_mono',
            10
        )

    def image_callback(self, msg: Image):
        # Convert ROS image -> OpenCV image
        cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Convert to grayscale
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        # Convert back to ROS image with mono8 encoding
        gray_msg = self.bridge.cv2_to_imgmsg(gray, encoding='mono8')
        gray_msg.header = msg.header  # preserve timestamp/frame_id

        self.pub.publish(gray_msg)


def main(args=None):
    rclpy.init(args=args)
    node = GrayscaleRepublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()