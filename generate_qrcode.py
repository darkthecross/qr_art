import qrcode
import numpy as np
import cv2

BOX_SIZE_CONST = 10
BORDER_CONST = 2

qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=BOX_SIZE_CONST,
    border=BORDER_CONST,
)
qr.add_data('I love 17')
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")

open_cv_image = np.array(img, dtype=np.uint8)
open_cv_image[:,:] = open_cv_image[:,:] * 255

cv2.imshow("tw", open_cv_image)
cv2.waitKey(0)


qr_mat_l = int(open_cv_image.shape[0] / BOX_SIZE_CONST)

qr_mat = np.zeros((qr_mat_l, qr_mat_l), dtype=np.int32)

for i in range(qr_mat_l):
    for j in range(qr_mat_l):
        qr_mat[i,j] = ( open_cv_image[int(i*BOX_SIZE_CONST + BOX_SIZE_CONST/2)
        , int(j*BOX_SIZE_CONST + BOX_SIZE_CONST/2)] == 0)

print(qr_mat)
