import qrcode
import numpy as np
from cv2 import cv2
import os
import sys
import random


class QrArt():

    def __init__(self):
        self.BOX_SIZE_CONST = 10
        self.BORDER_CONST = 2
        self.asset_imgs = []
        self.asset_mats = []
        self.BINARIZATION_THRESHOLD = 240
        self.POSITIVE_THRESHOLD = 40 # note: pos means < thresh

    def initiateAssets(self):
        for root, dirs, files in os.walk("img/"):
            for dir in dirs:
                dir_split = dir.split('x')
                if len(dir_split) != 2:
                    if(dir == "code_position"):
                        for _, _, fs in os.walk("img/" + dir + "/"):
                            for fn in fs:
                                oimg, res_mat = self.initAssetsHelper("img/" + dir + "/" + fn, (7,7))
                                exsisted = False
                                for idx, nparr in enumerate(self.asset_mats):
                                    if np.array_equal(nparr, res_mat):
                                        self.asset_imgs[idx].append(oimg)
                                        exsisted = True
                                        break;
                                if not exsisted:
                                    self.asset_imgs.append([oimg])
                                    self.asset_mats.append(res_mat)
                    continue;
                w = int(dir_split[0])
                h = int(dir_split[1])
                for _, _, fs in os.walk("img/" + dir + "/"):
                    for fn in fs:
                        oimg, res_mat = self.initAssetsHelper("img/" + dir + "/" + fn, (w,h))
                        exsisted = False
                        for idx, nparr in enumerate(self.asset_mats):
                            if np.array_equal(nparr, res_mat):
                                self.asset_imgs[idx].append(oimg)
                                exsisted = True
                                break;
                        if not exsisted:
                            self.asset_imgs.append([oimg])
                            self.asset_mats.append(res_mat)
        for idx1 in range(len(self.asset_mats)):
            for idx2 in range(idx1 + 1, len(self.asset_mats)):
                sp1 = self.asset_mats[idx1].shape[0] * self.asset_mats[idx1].shape[1]
                sp2 = self.asset_mats[idx2].shape[0] * self.asset_mats[idx2].shape[1]
                if sp1 < sp2:
                    self.asset_mats[idx1], self.asset_mats[idx2] = self.asset_mats[idx2], self.asset_mats[idx1]
                    self.asset_imgs[idx1], self.asset_imgs[idx2] = self.asset_imgs[idx2], self.asset_imgs[idx1]

    def initAssetsHelper(self, assetImgDir, assetSize):
        origin_img = cv2.imread(assetImgDir)
        origin_img = cv2.resize(origin_img, (0,0), fx=0.1, fy=0.1)
        gray_img = cv2.cvtColor(origin_img, cv2.COLOR_BGR2GRAY)
        thresh = 240
        _, im_bw = cv2.threshold(gray_img, thresh, 255, cv2.THRESH_BINARY)
        result_mat = np.zeros(assetSize, dtype=np.int32)
        for i in range(assetSize[0]):
            for j in range(assetSize[1]):
                tmpmat = np.zeros((self.BOX_SIZE_CONST, self.BOX_SIZE_CONST), dtype=np.int32)
                tmpmat[:,:] = im_bw[i*self.BOX_SIZE_CONST:(i+1)*self.BOX_SIZE_CONST, j*self.BOX_SIZE_CONST:(j+1)*self.BOX_SIZE_CONST]
                if np.sum( tmpmat ) < self.POSITIVE_THRESHOLD * 255:
                    result_mat[i, j] = 1
        return origin_img, result_mat

    def generateQrArtMat(self, words):
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
        result_mat = np.ones((open_cv_image.shape[0], open_cv_image.shape[1], 3), dtype=np.uint8)
        result_mat[:,:,:] = result_mat[:,:,:] * 255
        for idx, submats in enumerate(self.asset_mats):
            resultList = self.findSubCode(qr_mat, submats)
            for results in resultList:
                xx = results[0]*self.BOX_SIZE_CONST
                yy = results[1]*self.BOX_SIZE_CONST
                xx_end = submats.shape[0]*self.BOX_SIZE_CONST + xx
                yy_end = submats.shape[1]*self.BOX_SIZE_CONST + yy
                tmpsubimg = random.choice(self.asset_imgs[idx])
                result_mat[xx:xx_end, yy:yy_end, :] = tmpsubimg[:,:,:]
        cv2.imshow("res", result_mat)
        cv2.waitKey(0)
        return result_mat

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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("arg error!")
    else:
        qa = QrArt()
        wordss = sys.argv[1]
        qa.initiateAssets()
        qa.generateQrArtMat(wordss)
