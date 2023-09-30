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
import sys
class bstack1ll11l1lll_opy_:
    def __init__(self, handler):
        self._1ll11ll11l_opy_ = sys.stdout.write
        self._1ll11ll111_opy_ = sys.stderr.write
        self.handler = handler
        self._started = False
    def start(self):
        if self._started:
            return
        self._started = True
        sys.stdout.write = self.bstack1ll11l1ll1_opy_
        sys.stdout.error = self.bstack1ll11ll1l1_opy_
    def bstack1ll11l1ll1_opy_(self, _str):
        self._1ll11ll11l_opy_(_str)
        if self.handler:
            self.handler({bstack1l1l11l_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫೃ"): bstack1l1l11l_opy_ (u"࠭ࡉࡏࡈࡒࠫೄ"), bstack1l1l11l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ೅"): _str})
    def bstack1ll11ll1l1_opy_(self, _str):
        self._1ll11ll111_opy_(_str)
        if self.handler:
            self.handler({bstack1l1l11l_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧೆ"): bstack1l1l11l_opy_ (u"ࠩࡈࡖࡗࡕࡒࠨೇ"), bstack1l1l11l_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫೈ"): _str})
    def reset(self):
        if not self._started:
            return
        self._started = False
        sys.stdout.write = self._1ll11ll11l_opy_
        sys.stderr.write = self._1ll11ll111_opy_