import numpy as np
import os
import cv_bridge
import cv2
from sensor_msgs.msg import Image, CompressedImage

scriptpath = os.path.dirname(os.path.realpath(__file__))
flowersin = cv2.resize(cv2.imread(os.path.join(scriptpath, "flowers.jpg"), flags=cv2.IMREAD_UNCHANGED), None, fx=0.5, fy=0.5)
# imnp = np.random.randint(0, high=256, size=(100,100,3), dtype=np.uint8)
bridge : cv_bridge.CvBridge = cv_bridge.CvBridge()
img_msg_bgr = bridge.cv2_to_imgmsg(flowersin, encoding="bgr8")
img_msg_rgb = bridge.cv2_to_imgmsg(cv2.cvtColor(flowersin, cv2.COLOR_BGR2RGB), encoding="rgb8")


winname = "Flowers"
cv2.namedWindow(winname, flags=cv2.WINDOW_AUTOSIZE)
cv2.imshow(winname, flowersin)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


flowersroundtrip = bridge.imgmsg_to_cv2(img_msg_rgb, desired_encoding="bgr8")
winname = "Flowers from ROS2"
cv2.namedWindow(winname, flags=cv2.WINDOW_AUTOSIZE)
cv2.imshow(winname, flowersroundtrip)
# cv2.waitKey(0)


flowersroundtrip_wrongencoding = bridge.imgmsg_to_cv2(img_msg_bgr, desired_encoding="rgb8")
winname = "Flowers with wrong encoding ROS2"
cv2.namedWindow(winname, flags=cv2.WINDOW_AUTOSIZE)
cv2.imshow(winname, flowersroundtrip_wrongencoding)
cv2.waitKey(0)

cv2.destroyAllWindows()

