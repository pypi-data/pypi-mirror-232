from apsisocr import ApsisOCR
from apsisocr.utils import LOG_INFO

try:
    ocr=ApsisOCR()
    result=ocr("deployment/images/test.png")
except Exception as e:
    LOG_INFO("setup failed",mcolor="red")
    LOG_INFO("--------------------------------------------------------------------------------------------",mcolor="red")
    LOG_INFO(e,mcolor="green")
    LOG_INFO("--------------------------------------------------------------------------------------------",mcolor="red")
    