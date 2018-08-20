import qrcode
import numpy as np
from cv2 import cv2


class QrArt():

    def __init__(self):
        self.BOX_SIZE_CONST = 10
        self.BORDER_CONST = 2
        self.assets = {}

    def initiateAssets(self): 
        return 0

    def generateQrMat(self, words):
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=self.BOX_SIZE_CONST,
            border=self.BORDER_CONST,
        )
        qr.add_data(words)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        open_cv_image = np.array(img, dtype=np.uint8)
        open_cv_image[:, :] = open_cv_image[:, :] * 255
        #cv2.imshow("tw", open_cv_image)
        #cv2.waitKey(0)
        qr_mat_l = int(open_cv_image.shape[0] / self.BOX_SIZE_CONST)
        qr_mat = np.zeros((qr_mat_l, qr_mat_l), dtype=np.int32)
        for i in range(qr_mat_l):
            for j in range(qr_mat_l):
                qr_mat[i, j] = (open_cv_image[int(i * self.BOX_SIZE_CONST + self.BOX_SIZE_CONST / 2),
                                              int(j * self.BOX_SIZE_CONST + self.BOX_SIZE_CONST / 2)] == 0)
        return qr_mat

    def findSubCode(self, origin_mat, sub_code_mat):
        resultList = []
        origin_mat_cp = origin_mat[:,:]
        omsp = origin_mat.shape
        scmsp = sub_code_mat.shape
        for i in range(omsp[0] - scmsp[0]):
            for j in range(omsp[1] - scmsp[1]):
                if np.array_equal(origin_mat_cp[i:i+scmsp[0], j:j+scmsp[1]], sub_code_mat[:,:]):
                    origin_mat_cp[i:i+scmsp[0], j:j+scmsp[1]] = np.zeros((scmsp[0],scmsp[1]), dtype=np.int32)
                    resultList.append((i,j))
        return resultList

    def testFSC(self, words):
        om = self.generateQrMat(words)
        scm = np.ones((2,2), dtype=np.int32)
        resultList = self.findSubCode(om, scm)
        result_mat = np.ones((om.shape[0]*self.BOX_SIZE_CONST, om.shape[1]*self.BOX_SIZE_CONST, 3), dtype=np.uint8)
        result_mat[:,:,:] = result_mat[:,:,:] * 255
        for i in range(om.shape[0]):
            for j in range(om.shape[1]):
                if om[i,j] == 1:
                    result_mat[i*self.BOX_SIZE_CONST:(i+1)*self.BOX_SIZE_CONST, j*self.BOX_SIZE_CONST:(j+1)*self.BOX_SIZE_CONST,:] = [0,0,0]
        for results in resultList:
            ii = results[0]
            jj = results[1]
            result_mat[ii*self.BOX_SIZE_CONST:(ii+2)*self.BOX_SIZE_CONST, jj*self.BOX_SIZE_CONST:(jj+2)*self.BOX_SIZE_CONST,:] = [0,0,255]
        cv2.imshow("123", result_mat)
        cv2.waitKey(0)

if __name__ == "__main__":
    qa = QrArt()
    wordss = "I love 17"
    qa.testFSC(wordss)
