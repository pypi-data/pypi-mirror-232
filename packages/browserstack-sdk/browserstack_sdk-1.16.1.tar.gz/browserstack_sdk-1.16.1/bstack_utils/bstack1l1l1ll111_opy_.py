# coding: UTF-8
import sys
bstack1l11lll_opy_ = sys.version_info [0] == 2
bstack1l1l1ll_opy_ = 2048
bstack1lll111_opy_ = 7
def bstack1l1l11l_opy_ (bstack1llll1l_opy_):
    global bstack1l11l_opy_
    bstack111l1ll_opy_ = ord (bstack1llll1l_opy_ [-1])
    bstack1111l11_opy_ = bstack1llll1l_opy_ [:-1]
    bstack11lll11_opy_ = bstack111l1ll_opy_ % len (bstack1111l11_opy_)
    bstack1llll1_opy_ = bstack1111l11_opy_ [:bstack11lll11_opy_] + bstack1111l11_opy_ [bstack11lll11_opy_:]
    if bstack1l11lll_opy_:
        bstack1l1l1l_opy_ = unicode () .join ([unichr (ord (char) - bstack1l1l1ll_opy_ - (bstack1ll1lll_opy_ + bstack111l1ll_opy_) % bstack1lll111_opy_) for bstack1ll1lll_opy_, char in enumerate (bstack1llll1_opy_)])
    else:
        bstack1l1l1l_opy_ = str () .join ([chr (ord (char) - bstack1l1l1ll_opy_ - (bstack1ll1lll_opy_ + bstack111l1ll_opy_) % bstack1lll111_opy_) for bstack1ll1lll_opy_, char in enumerate (bstack1llll1_opy_)])
    return eval (bstack1l1l1l_opy_)
class bstack1l1l1ll11l_opy_:
    def __init__(self, handler):
        self._1l1l1l1l1l_opy_ = None
        self.handler = handler
        self._1l1l1l1ll1_opy_ = self.bstack1l1l1l1l11_opy_()
        self.patch()
    def patch(self):
        self._1l1l1l1l1l_opy_ = self._1l1l1l1ll1_opy_.execute
        self._1l1l1l1ll1_opy_.execute = self.bstack1l1l1l1lll_opy_()
    def bstack1l1l1l1lll_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            response = self._1l1l1l1l1l_opy_(this, driver_command, *args, **kwargs)
            self.handler(driver_command, response)
            return response
        return execute
    def reset(self):
        self._1l1l1l1ll1_opy_.execute = self._1l1l1l1l1l_opy_
    @staticmethod
    def bstack1l1l1l1l11_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver