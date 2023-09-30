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
import os
from browserstack_sdk.bstack111l111l_opy_ import *
from bstack_utils.helper import bstack11ll11ll1_opy_
from bstack_utils.messages import bstack11111l1ll_opy_
from bstack_utils.constants import bstack1ll1l11lll_opy_
class bstack1l111ll1_opy_:
    def __init__(self, args, logger, bstack1ll1l1l111_opy_, bstack1ll11lll1l_opy_):
        self.args = args
        self.logger = logger
        self.bstack1ll1l1l111_opy_ = bstack1ll1l1l111_opy_
        self.bstack1ll11lll1l_opy_ = bstack1ll11lll1l_opy_
        self._prepareconfig = None
        self.Config = None
        self.runner = None
        self.bstack1ll1ll11ll_opy_ = []
        self.bstack1ll1l1111l_opy_ = None
        self.bstack1l11l111_opy_ = []
        self.bstack1ll11ll1ll_opy_ = self.bstack1l1111l1l_opy_()
    def start(self):
        self.bstack11ll1111l_opy_()
        self.parse_args()
        self.bstack1ll1l11l1l_opy_()
    def bstack1l1l1l111_opy_(self, bstack1ll1l1l1l1_opy_):
        self.parse_args()
        self.bstack1ll1l11l1l_opy_()
        self.bstack1ll1l11111_opy_(bstack1ll1l1l1l1_opy_)
        self.bstack1ll11llll1_opy_()
    @staticmethod
    def version():
        import pytest
        return pytest.__version__
    def bstack1ll1l1l11l_opy_(self, arg):
        if arg in self.args:
            i = self.args.index(arg)
            self.args.pop(i + 1)
            self.args.pop(i)
    def parse_args(self):
        try:
            bstack1ll11lllll_opy_ = [bstack1l1l11l_opy_ (u"࠭࠭࠮ࡣࡵ࡫ࡸ࠭ಚ"), bstack1l1l11l_opy_ (u"ࠧ࠮࠯ࡧࡶ࡮ࡼࡥࡳࠩಛ"), bstack1l1l11l_opy_ (u"ࠨ࠯࠰ࡴࡱࡻࡧࡪࡰࡶࠫಜ"), bstack1l1l11l_opy_ (u"ࠩ࠰ࡴࠬಝ"), bstack1l1l11l_opy_ (u"ࠪ࠱࠲ࡴࡵ࡮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫಞ"), bstack1l1l11l_opy_ (u"ࠫ࠲ࡴࠧಟ")]
            for arg in bstack1ll11lllll_opy_:
                self.bstack1ll1l1l11l_opy_(arg)
        except Exception as exc:
            self.logger.error(str(exc))
    def bstack1ll1l111l1_opy_(self, bstack1ll1ll11ll_opy_):
        try:
            if os.environ.get(bstack1l1l11l_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡗࡋࡒࡖࡐࠥಠ"), None) == bstack1l1l11l_opy_ (u"ࠨࡴࡳࡷࡨࠦಡ"):
                tests = os.environ.get(bstack1l1l11l_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡒࡆࡔࡘࡒࡤ࡚ࡅࡔࡖࡖࠦಢ"), None)
                if bstack1l1l11l_opy_ (u"ࠣࡴࡨࡶࡺࡴࡔࡦࡵࡷࡷࠧಣ") in self.bstack1ll1l1l111_opy_:
                    del self.bstack1ll1l1l111_opy_[bstack1l1l11l_opy_ (u"ࠤࡵࡩࡷࡻ࡮ࡕࡧࡶࡸࡸࠨತ")]
                if tests is None or tests == bstack1l1l11l_opy_ (u"ࠥࡲࡺࡲ࡬ࠣಥ"):
                    return bstack1ll1ll11ll_opy_
                bstack1ll1ll11ll_opy_ = tests.split(bstack1l1l11l_opy_ (u"ࠫ࠱࠭ದ"))
                return bstack1ll1ll11ll_opy_
        except Exception as exc:
            self.logger.error(str(exc))
        return bstack1ll1ll11ll_opy_
    def get_args(self):
        return self.args
    def bstack1ll1l11l1l_opy_(self):
        config = self._prepareconfig(self.args)
        bstack1ll1ll11ll_opy_ = config.args
        bstack1ll1l11ll1_opy_ = config.invocation_params.args
        bstack1ll1l11ll1_opy_ = list(bstack1ll1l11ll1_opy_)
        bstack1ll11lll11_opy_ = [os.path.normpath(item) for item in bstack1ll1ll11ll_opy_]
        bstack1ll1l1ll11_opy_ = [os.path.normpath(item) for item in bstack1ll1l11ll1_opy_]
        bstack1ll1l1111l_opy_ = [item for item in bstack1ll1l1ll11_opy_ if item not in bstack1ll11lll11_opy_]
        import platform as pf
        if pf.system().lower() == bstack1l1l11l_opy_ (u"ࠬࡽࡩ࡯ࡦࡲࡻࡸ࠭ಧ"):
            from pathlib import PureWindowsPath, PurePosixPath
            bstack1ll1ll11ll_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11111l111_opy_)))
                          for bstack11111l111_opy_ in bstack1ll1ll11ll_opy_]
        bstack1ll1ll11ll_opy_ = self.bstack1ll1l111l1_opy_(bstack1ll1ll11ll_opy_)
        self.bstack1ll1ll11ll_opy_ = bstack1ll1ll11ll_opy_
        self.bstack1ll1l1111l_opy_ = bstack1ll1l1111l_opy_
        return bstack1ll1l1111l_opy_
    def bstack11ll1111l_opy_(self):
        try:
            from _pytest.config import _prepareconfig
            from _pytest.config import Config
            from _pytest import runner
            import importlib
            bstack1ll1l11l11_opy_ = importlib.find_loader(bstack1l1l11l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠨನ"))
            self._prepareconfig = _prepareconfig
            self.Config = Config
            self.runner = runner
        except Exception as e:
            self.logger.warn(e, bstack11111l1ll_opy_)
    def bstack1ll1l11111_opy_(self, bstack1ll1l1l1l1_opy_):
        if bstack1l1l11l_opy_ (u"ࠧ࠮࠯ࡦࡥࡨ࡮ࡥ࠮ࡥ࡯ࡩࡦࡸࠧ಩") not in self.bstack1ll1l1111l_opy_:
            self.bstack1ll1l1111l_opy_.append(bstack1l1l11l_opy_ (u"ࠨ࠯࠰ࡧࡦࡩࡨࡦ࠯ࡦࡰࡪࡧࡲࠨಪ"))
        if bstack1ll1l1l1l1_opy_:
            self.bstack1ll1l1111l_opy_.append(bstack1l1l11l_opy_ (u"ࠩ࠰࠱ࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ಫ"))
            self.bstack1ll1l1111l_opy_.append(bstack1l1l11l_opy_ (u"ࠪࡘࡷࡻࡥࠨಬ"))
        if not self.bstack1ll11ll1ll_opy_:
            self.bstack1ll1l1111l_opy_.append(bstack1l1l11l_opy_ (u"ࠫ࠲ࡶࠧಭ"))
            self.bstack1ll1l1111l_opy_.append(bstack1l1l11l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡴࡱࡻࡧࡪࡰࠪಮ"))
        self.bstack1ll1l1111l_opy_.append(bstack1l1l11l_opy_ (u"࠭࠭࠮ࡦࡵ࡭ࡻ࡫ࡲࠨಯ"))
        self.bstack1ll1l1111l_opy_.append(bstack1l1l11l_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࠧರ"))
    def bstack1ll11llll1_opy_(self):
        bstack1l11l111_opy_ = []
        for spec in self.bstack1ll1ll11ll_opy_:
            bstack11ll11ll_opy_ = [spec]
            bstack11ll11ll_opy_ += self.bstack1ll1l1111l_opy_
            bstack1l11l111_opy_.append(bstack11ll11ll_opy_)
        self.bstack1l11l111_opy_ = bstack1l11l111_opy_
        return bstack1l11l111_opy_
    def bstack1l1111l1l_opy_(self):
        try:
            from pytest_bdd import reporting
            self.bstack1ll11ll1ll_opy_ = True
            return True
        except Exception as e:
            self.bstack1ll11ll1ll_opy_ = False
        return self.bstack1ll11ll1ll_opy_
    def bstack1ll1ll11l1_opy_(self):
        bstack11lll111_opy_ = 1
        if bstack1l1l11l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨಱ") in self.bstack1ll1l1l111_opy_:
            bstack11lll111_opy_ = self.bstack1ll1l1l111_opy_[bstack1l1l11l_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩಲ")]
        bstack11lllllll_opy_ = int(bstack11lll111_opy_) * int(len(self.bstack1ll1l1l111_opy_[bstack1l1l11l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ಳ")]))
        execution_items = []
        for bstack11ll11ll_opy_ in self.bstack1l11l111_opy_:
            for index, _ in enumerate(self.bstack1ll1l1l111_opy_[bstack1l1l11l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ಴")]):
                item = {}
                item[bstack1l1l11l_opy_ (u"ࠬࡧࡲࡨࠩವ")] = bstack11ll11ll_opy_
                item[bstack1l1l11l_opy_ (u"࠭ࡩ࡯ࡦࡨࡼࠬಶ")] = index
                execution_items.append(item)
        bstack111111111_opy_ = bstack11ll11ll1_opy_(execution_items, bstack11lllllll_opy_)
        return bstack111111111_opy_
    def bstack1lll11l1_opy_(self, bstack111111111_opy_, bstack1ll1l1ll1l_opy_):
        for execution_item in bstack111111111_opy_:
            bstack1l1l111l1_opy_ = []
            for item in execution_item:
                bstack1l1l111l1_opy_.append(bstack1lll1lll11_opy_(name=str(item[bstack1l1l11l_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ಷ")]),
                                                     target=self.bstack1ll1l111ll_opy_,
                                                     args=(item[bstack1l1l11l_opy_ (u"ࠨࡣࡵ࡫ࠬಸ")], bstack1ll1l1ll1l_opy_)))
            for t in bstack1l1l111l1_opy_:
                t.start()
            for t in bstack1l1l111l1_opy_:
                t.join()
    def bstack1ll1l111ll_opy_(self, arg, bstack1ll1l1ll1l_opy_):
        arg.append(bstack1l1l11l_opy_ (u"ࠤ࠰࠱࡮ࡳࡰࡰࡴࡷ࠱ࡲࡵࡤࡦ࠿࡬ࡱࡵࡵࡲࡵ࡮࡬ࡦࠧಹ"))
        arg.append(bstack1l1l11l_opy_ (u"ࠥ࠱࡜ࠨ಺"))
        arg.append(bstack1l1l11l_opy_ (u"ࠦ࡮࡭࡮ࡰࡴࡨ࠾ࡒࡵࡤࡶ࡮ࡨࠤࡦࡲࡲࡦࡣࡧࡽࠥ࡯࡭ࡱࡱࡵࡸࡪࡪ࠺ࡱࡻࡷࡩࡸࡺ࠮ࡑࡻࡷࡩࡸࡺࡗࡢࡴࡱ࡭ࡳ࡭ࠢ಻"))
        arg.append(bstack1l1l11l_opy_ (u"ࠧ࠳ࡗ಼ࠣ"))
        arg.append(bstack1l1l11l_opy_ (u"ࠨࡩࡨࡰࡲࡶࡪࡀࡔࡩࡧࠣ࡬ࡴࡵ࡫ࡪ࡯ࡳࡰࠧಽ"))
        bstack1ll1l1ll1l_opy_(bstack1ll1l11lll_opy_)
        if self.bstack1ll11lll1l_opy_:
            os.environ[bstack1l1l11l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡕࡔࡇࡕࡒࡆࡓࡅࠨಾ")] = self.bstack1ll1l1l111_opy_[bstack1l1l11l_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪಿ")]
            os.environ[bstack1l1l11l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡆࡇࡊ࡙ࡓࡠࡍࡈ࡝ࠬೀ")] = self.bstack1ll1l1l111_opy_[bstack1l1l11l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ು")]
        os.environ[bstack1l1l11l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧೂ")] = self.bstack1ll11lll1l_opy_.__str__()
        from _pytest.config import main as bstack1ll1l1l1ll_opy_
        bstack1ll1l1l1ll_opy_(arg)