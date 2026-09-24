import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2
import numpy as np


class YoloDepthNode(Node):
    def __init__(self):
        super().__init__('yolo_depth_node')

        self.bridge = CvBridge()
        self.model = YOLO('yolo11n.pt')

        self.latest_depth = None

        self.create_subscription(
            Image,
            '/depth_camera/rgb',
            self.rgb_callback,
            10
        )

        self.create_subscription(
            Image,
            '/depth_camera/depth/image_raw',
            self.depth_callback,
            10
        )

        self.get_logger().info('YOLO + depth node running')

    def depth_callback(self, msg):
        self.latest_depth = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='32FC1'
        )

    def rgb_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        results = self.model(frame, verbose=False)
        annotated = results[0].plot()

        if self.latest_depth is not None:
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id]
                confidence = float(box.conf[0])

                if class_name == 'bench':
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                    u = int((x1 + x2) / 2)
                    v = int((y1 + y2) / 2)

                    if (
                        0 <= v < self.latest_depth.shape[0]
                        and 0 <= u < self.latest_depth.shape[1]
                    ):
                        depth = float(self.latest_depth[v, u])

                        if np.isfinite(depth) and depth > 0:
                            self.get_logger().info(
                                f'bench conf={confidence:.2f}, '
                                f'pixel=({u},{v}), '
                                f'depth={depth:.2f} m'
                            )

                            cv2.circle(
                                annotated,
                                (u, v),
                                6,
                                (0, 255, 0),
                                -1
                            )

                            cv2.putText(
                                annotated,
                                f'{depth:.2f} m',
                                (u + 10, v),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7,
                                (0, 255, 0),
                                2
                            )

        cv2.imshow('YOLO + Depth', annotated)
        cv2.waitKey(1)


def main():
    rclpy.init()
    node = YoloDepthNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
