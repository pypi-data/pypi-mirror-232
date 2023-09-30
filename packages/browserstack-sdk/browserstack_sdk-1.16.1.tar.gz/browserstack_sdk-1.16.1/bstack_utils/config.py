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
conf = {
    bstack1l1l11l_opy_ (u"ࠫࡦࡶࡰࡠࡣࡸࡸࡴࡳࡡࡵࡧࠪ೉"): False,
    bstack1l1l11l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ೊ"): True,
}
class Config(object):
    instance = None
    def __init__(self):
        self._1ll11l1l1l_opy_ = conf
    @classmethod
    def get_instance(cls):
        if cls.instance:
            return cls.instance
        return Config()
    def get_property(self, property_name):
        return self._1ll11l1l1l_opy_.get(property_name, None)
    def bstack1l11l1l1_opy_(self, property_name, bstack1ll11l1l11_opy_):
        self._1ll11l1l1l_opy_[property_name] = bstack1ll11l1l11_opy_