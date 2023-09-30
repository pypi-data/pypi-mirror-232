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
import datetime
import json
import logging
import os
import threading
from bstack_utils.helper import bstack1l1llll1ll_opy_, bstack1ll1111lll_opy_, get_host_info, bstack1ll1111ll1_opy_, bstack1l1llll111_opy_, bstack1l1lll1ll1_opy_, \
    bstack1l1lll1l11_opy_, bstack1ll1111111_opy_, bstack111111l1_opy_, bstack1ll1111l1l_opy_, bstack1ll111lll1_opy_, bstack1ll1111l11_opy_
from bstack_utils.bstack1l1l1ll1ll_opy_ import bstack1l1ll111l1_opy_
bstack1l1l11lll1_opy_ = [
    bstack1l1l11l_opy_ (u"ࠨࡎࡲ࡫ࡈࡸࡥࡢࡶࡨࡨࠬလ"), bstack1l1l11l_opy_ (u"ࠩࡆࡆ࡙࡙ࡥࡴࡵ࡬ࡳࡳࡉࡲࡦࡣࡷࡩࡩ࠭ဝ"), bstack1l1l11l_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬသ"), bstack1l1l11l_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡘࡱࡩࡱࡲࡨࡨࠬဟ"),
    bstack1l1l11l_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧဠ"), bstack1l1l11l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧအ"), bstack1l1l11l_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨဢ")
]
bstack1l1l11ll11_opy_ = bstack1l1l11l_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࡦࡳࡱࡲࡥࡤࡶࡲࡶ࠲ࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭ࠨဣ")
logger = logging.getLogger(__name__)
class bstack1llll1lll1_opy_:
    bstack1l1l1ll1ll_opy_ = None
    bs_config = None
    @classmethod
    @bstack1ll1111l11_opy_(class_method=True)
    def launch(cls, bs_config, bstack1l11lllll1_opy_):
        cls.bs_config = bs_config
        if not cls.bstack1l11lll111_opy_():
            return
        cls.bstack1l1l1ll1ll_opy_ = bstack1l1ll111l1_opy_(cls.bstack1l1l1111ll_opy_)
        cls.bstack1l1l1ll1ll_opy_.start()
        bstack1l1l11l1l1_opy_ = bstack1ll1111ll1_opy_(bs_config)
        bstack1l1l111lll_opy_ = bstack1l1llll111_opy_(bs_config)
        data = {
            bstack1l1l11l_opy_ (u"ࠩࡩࡳࡷࡳࡡࡵࠩဤ"): bstack1l1l11l_opy_ (u"ࠪ࡮ࡸࡵ࡮ࠨဥ"),
            bstack1l1l11l_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡤࡴࡡ࡮ࡧࠪဦ"): bs_config.get(bstack1l1l11l_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪဧ"), bstack1l1l11l_opy_ (u"࠭ࠧဨ")),
            bstack1l1l11l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬဩ"): bs_config.get(bstack1l1l11l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫဪ"), os.path.basename(os.path.abspath(os.getcwd()))),
            bstack1l1l11l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬါ"): bs_config.get(bstack1l1l11l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬာ")),
            bstack1l1l11l_opy_ (u"ࠫࡩ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩိ"): bs_config.get(bstack1l1l11l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡈࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠨီ"), bstack1l1l11l_opy_ (u"࠭ࠧု")),
            bstack1l1l11l_opy_ (u"ࠧࡴࡶࡤࡶࡹࡥࡴࡪ࡯ࡨࠫူ"): datetime.datetime.now().isoformat(),
            bstack1l1l11l_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭ေ"): bstack1l1lll1ll1_opy_(bs_config),
            bstack1l1l11l_opy_ (u"ࠩ࡫ࡳࡸࡺ࡟ࡪࡰࡩࡳࠬဲ"): get_host_info(),
            bstack1l1l11l_opy_ (u"ࠪࡧ࡮ࡥࡩ࡯ࡨࡲࠫဳ"): bstack1ll1111lll_opy_(),
            bstack1l1l11l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢࡶࡺࡴ࡟ࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫဴ"): os.environ.get(bstack1l1l11l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇ࡛ࡉࡍࡆࡢࡖ࡚ࡔ࡟ࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕࠫဵ")),
            bstack1l1l11l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩࡥࡴࡦࡵࡷࡷࡤࡸࡥࡳࡷࡱࠫံ"): os.environ.get(bstack1l1l11l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡒࡆࡔࡘࡒ့ࠬ"), False),
            bstack1l1l11l_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯ࡡࡦࡳࡳࡺࡲࡰ࡮ࠪး"): bstack1l1llll1ll_opy_(),
            bstack1l1l11l_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࡡࡹࡩࡷࡹࡩࡰࡰ္ࠪ"): {
                bstack1l1l11l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡔࡡ࡮ࡧ်ࠪ"): bstack1l11lllll1_opy_.get(bstack1l1l11l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࠬျ"), bstack1l1l11l_opy_ (u"ࠬࡖࡹࡵࡧࡶࡸࠬြ")),
                bstack1l1l11l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩွ"): bstack1l11lllll1_opy_.get(bstack1l1l11l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠫှ")),
                bstack1l1l11l_opy_ (u"ࠨࡵࡧ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬဿ"): bstack1l11lllll1_opy_.get(bstack1l1l11l_opy_ (u"ࠩࡶࡨࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ၀"))
            }
        }
        config = {
            bstack1l1l11l_opy_ (u"ࠪࡥࡺࡺࡨࠨ၁"): (bstack1l1l11l1l1_opy_, bstack1l1l111lll_opy_),
            bstack1l1l11l_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡷࠬ၂"): cls.default_headers()
        }
        response = bstack111111l1_opy_(bstack1l1l11l_opy_ (u"ࠬࡖࡏࡔࡖࠪ၃"), cls.request_url(bstack1l1l11l_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡢࡶ࡫࡯ࡨࡸ࠭၄")), data, config)
        if response.status_code != 200:
            os.environ[bstack1l1l11l_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡇ࡛ࡉࡍࡆࡢࡇࡔࡓࡐࡍࡇࡗࡉࡉ࠭၅")] = bstack1l1l11l_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧ၆")
            os.environ[bstack1l1l11l_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡊࡘࡖࠪ၇")] = bstack1l1l11l_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ၈")
            os.environ[bstack1l1l11l_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡄࡘࡍࡑࡊ࡟ࡉࡃࡖࡌࡊࡊ࡟ࡊࡆࠪ၉")] = bstack1l1l11l_opy_ (u"ࠧࡴࡵ࡭࡮ࠥ၊")
            os.environ[bstack1l1l11l_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧ။")] = bstack1l1l11l_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧ၌")
            bstack1l11llllll_opy_ = response.json()
            if bstack1l11llllll_opy_ and bstack1l11llllll_opy_[bstack1l1l11l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ၍")]:
                error_message = bstack1l11llllll_opy_[bstack1l1l11l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ၎")]
                if bstack1l11llllll_opy_[bstack1l1l11l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࡖࡼࡴࡪ࠭၏")] == bstack1l1l11l_opy_ (u"ࠫࡊࡘࡒࡐࡔࡢࡍࡓ࡜ࡁࡍࡋࡇࡣࡈࡘࡅࡅࡇࡑࡘࡎࡇࡌࡔࠩၐ"):
                    logger.error(error_message)
                elif bstack1l11llllll_opy_[bstack1l1l11l_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࡘࡾࡶࡥࠨၑ")] == bstack1l1l11l_opy_ (u"࠭ࡅࡓࡔࡒࡖࡤࡇࡃࡄࡇࡖࡗࡤࡊࡅࡏࡋࡈࡈࠬၒ"):
                    logger.info(error_message)
                elif bstack1l11llllll_opy_[bstack1l1l11l_opy_ (u"ࠧࡦࡴࡵࡳࡷ࡚ࡹࡱࡧࠪၓ")] == bstack1l1l11l_opy_ (u"ࠨࡇࡕࡖࡔࡘ࡟ࡔࡆࡎࡣࡉࡋࡐࡓࡇࡆࡅ࡙ࡋࡄࠨၔ"):
                    logger.error(error_message)
                else:
                    logger.error(error_message)
            else:
                logger.error(bstack1ll111l11l_opy_ (u"ࠤࡇࡥࡹࡧࠠࡶࡲ࡯ࡳࡦࡪࠠࡵࡱࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡗࡩࡸࡺࠠࡐࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠠࡧࡣ࡬ࡰࡪࡪࠠࡥࡷࡨࠤࡹࡵࠠࡴࡱࡰࡩࠥ࡫ࡲࡳࡱࡵࠦၕ"))
            return [None, None, None]
        os.environ[bstack1l1l11l_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡃࡗࡌࡐࡉࡥࡃࡐࡏࡓࡐࡊ࡚ࡅࡅࠩၖ")] = bstack1l1l11l_opy_ (u"ࠫࡹࡸࡵࡦࠩၗ")
        bstack1l11llllll_opy_ = response.json()
        if bstack1l11llllll_opy_.get(bstack1l1l11l_opy_ (u"ࠬࡰࡷࡵࠩၘ")):
            os.environ[bstack1l1l11l_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡎ࡜࡚ࠧၙ")] = bstack1l11llllll_opy_[bstack1l1l11l_opy_ (u"ࠧ࡫ࡹࡷࠫၚ")]
            os.environ[bstack1l1l11l_opy_ (u"ࠨࡅࡕࡉࡉࡋࡎࡕࡋࡄࡐࡘࡥࡆࡐࡔࡢࡇࡗࡇࡓࡉࡡࡕࡉࡕࡕࡒࡕࡋࡑࡋࠬၛ")] = json.dumps({
                bstack1l1l11l_opy_ (u"ࠩࡸࡷࡪࡸ࡮ࡢ࡯ࡨࠫၜ"): bstack1l1l11l1l1_opy_,
                bstack1l1l11l_opy_ (u"ࠪࡴࡦࡹࡳࡸࡱࡵࡨࠬၝ"): bstack1l1l111lll_opy_
            })
        if bstack1l11llllll_opy_.get(bstack1l1l11l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭ၞ")):
            os.environ[bstack1l1l11l_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡅ࡙ࡎࡒࡄࡠࡊࡄࡗࡍࡋࡄࡠࡋࡇࠫၟ")] = bstack1l11llllll_opy_[bstack1l1l11l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨၠ")]
        if bstack1l11llllll_opy_.get(bstack1l1l11l_opy_ (u"ࠧࡢ࡮࡯ࡳࡼࡥࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࡶࠫၡ")):
            os.environ[bstack1l1l11l_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡇࡌࡍࡑ࡚ࡣࡘࡉࡒࡆࡇࡑࡗࡍࡕࡔࡔࠩၢ")] = str(bstack1l11llllll_opy_[bstack1l1l11l_opy_ (u"ࠩࡤࡰࡱࡵࡷࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡸ࠭ၣ")])
        return [bstack1l11llllll_opy_[bstack1l1l11l_opy_ (u"ࠪ࡮ࡼࡺࠧၤ")], bstack1l11llllll_opy_[bstack1l1l11l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭ၥ")], bstack1l11llllll_opy_[bstack1l1l11l_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡣࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡴࠩၦ")]]
    @classmethod
    @bstack1ll1111l11_opy_(class_method=True)
    def stop(cls):
        if not cls.on():
            return
        if os.environ[bstack1l1l11l_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡎ࡜࡚ࠧၧ")] == bstack1l1l11l_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧၨ") or os.environ[bstack1l1l11l_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧၩ")] == bstack1l1l11l_opy_ (u"ࠤࡱࡹࡱࡲࠢၪ"):
            print(bstack1l1l11l_opy_ (u"ࠪࡉ࡝ࡉࡅࡑࡖࡌࡓࡓࠦࡉࡏࠢࡶࡸࡴࡶࡂࡶ࡫࡯ࡨ࡚ࡶࡳࡵࡴࡨࡥࡲࠦࡒࡆࡓࡘࡉࡘ࡚ࠠࡕࡑࠣࡘࡊ࡙ࡔࠡࡑࡅࡗࡊࡘࡖࡂࡄࡌࡐࡎ࡚࡙ࠡ࠼ࠣࡑ࡮ࡹࡳࡪࡰࡪࠤࡦࡻࡴࡩࡧࡱࡸ࡮ࡩࡡࡵ࡫ࡲࡲࠥࡺ࡯࡬ࡧࡱࠫၫ"))
            return {
                bstack1l1l11l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫၬ"): bstack1l1l11l_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫၭ"),
                bstack1l1l11l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧၮ"): bstack1l1l11l_opy_ (u"ࠧࡕࡱ࡮ࡩࡳ࠵ࡢࡶ࡫࡯ࡨࡎࡊࠠࡪࡵࠣࡹࡳࡪࡥࡧ࡫ࡱࡩࡩ࠲ࠠࡣࡷ࡬ࡰࡩࠦࡣࡳࡧࡤࡸ࡮ࡵ࡮ࠡ࡯࡬࡫࡭ࡺࠠࡩࡣࡹࡩࠥ࡬ࡡࡪ࡮ࡨࡨࠬၯ")
            }
        else:
            cls.bstack1l1l1ll1ll_opy_.shutdown()
            data = {
                bstack1l1l11l_opy_ (u"ࠨࡵࡷࡳࡵࡥࡴࡪ࡯ࡨࠫၰ"): datetime.datetime.now().isoformat()
            }
            config = {
                bstack1l1l11l_opy_ (u"ࠩ࡫ࡩࡦࡪࡥࡳࡵࠪၱ"): cls.default_headers()
            }
            bstack1ll111l1l1_opy_ = bstack1l1l11l_opy_ (u"ࠪࡥࡵ࡯࠯ࡷ࠳࠲ࡦࡺ࡯࡬ࡥࡵ࠲ࡿࢂ࠵ࡳࡵࡱࡳࠫၲ").format(os.environ[bstack1l1l11l_opy_ (u"ࠦࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡄࡘࡍࡑࡊ࡟ࡉࡃࡖࡌࡊࡊ࡟ࡊࡆࠥၳ")])
            bstack1l1l11111l_opy_ = cls.request_url(bstack1ll111l1l1_opy_)
            response = bstack111111l1_opy_(bstack1l1l11l_opy_ (u"ࠬࡖࡕࡕࠩၴ"), bstack1l1l11111l_opy_, data, config)
            if not response.ok:
                raise Exception(bstack1l1l11l_opy_ (u"ࠨࡓࡵࡱࡳࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡴ࡯ࡵࠢࡲ࡯ࠧၵ"))
    @classmethod
    def bstack1l1ll1l1_opy_(cls):
        if cls.on():
            print(
                bstack1l1l11l_opy_ (u"ࠧࡗ࡫ࡶ࡭ࡹࠦࡨࡵࡶࡳࡷ࠿࠵࠯ࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡦࡺ࡯࡬ࡥࡵ࠲ࡿࢂࠦࡴࡰࠢࡹ࡭ࡪࡽࠠࡣࡷ࡬ࡰࡩࠦࡲࡦࡲࡲࡶࡹ࠲ࠠࡪࡰࡶ࡭࡬࡮ࡴࡴ࠮ࠣࡥࡳࡪࠠ࡮ࡣࡱࡽࠥࡳ࡯ࡳࡧࠣࡨࡪࡨࡵࡨࡩ࡬ࡲ࡬ࠦࡩ࡯ࡨࡲࡶࡲࡧࡴࡪࡱࡱࠤࡦࡲ࡬ࠡࡣࡷࠤࡴࡴࡥࠡࡲ࡯ࡥࡨ࡫ࠡ࡝ࡰࠪၶ").format(os.environ[bstack1l1l11l_opy_ (u"ࠣࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠢၷ")]))
    @classmethod
    def bstack1l1l1l11l1_opy_(cls, bstack1l1l111l11_opy_, bstack1l1l1l111l_opy_=bstack1l1l11l_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠲࠱ࡥࡥࡹࡩࡨࠨၸ")):
        if not cls.on():
            return
        bstack11l11ll1_opy_ = bstack1l1l111l11_opy_[bstack1l1l11l_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧၹ")]
        bstack1l1l11l1ll_opy_ = {
            bstack1l1l11l_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬၺ"): bstack1l1l11l_opy_ (u"࡚ࠬࡥࡴࡶࡢࡗࡹࡧࡲࡵࡡࡘࡴࡱࡵࡡࡥࠩၻ"),
            bstack1l1l11l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨၼ"): bstack1l1l11l_opy_ (u"ࠧࡕࡧࡶࡸࡤࡋ࡮ࡥࡡࡘࡴࡱࡵࡡࡥࠩၽ"),
            bstack1l1l11l_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕ࡮࡭ࡵࡶࡥࡥࠩၾ"): bstack1l1l11l_opy_ (u"ࠩࡗࡩࡸࡺ࡟ࡔ࡭࡬ࡴࡵ࡫ࡤࡠࡗࡳࡰࡴࡧࡤࠨၿ"),
            bstack1l1l11l_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧႀ"): bstack1l1l11l_opy_ (u"ࠫࡑࡵࡧࡠࡗࡳࡰࡴࡧࡤࠨႁ"),
            bstack1l1l11l_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭ႂ"): bstack1l1l11l_opy_ (u"࠭ࡈࡰࡱ࡮ࡣࡘࡺࡡࡳࡶࡢ࡙ࡵࡲ࡯ࡢࡦࠪႃ"),
            bstack1l1l11l_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩႄ"): bstack1l1l11l_opy_ (u"ࠨࡊࡲࡳࡰࡥࡅ࡯ࡦࡢ࡙ࡵࡲ࡯ࡢࡦࠪႅ"),
            bstack1l1l11l_opy_ (u"ࠩࡆࡆ࡙࡙ࡥࡴࡵ࡬ࡳࡳࡉࡲࡦࡣࡷࡩࡩ࠭ႆ"): bstack1l1l11l_opy_ (u"ࠪࡇࡇ࡚࡟ࡖࡲ࡯ࡳࡦࡪࠧႇ")
        }.get(bstack11l11ll1_opy_)
        if bstack1l1l1l111l_opy_ == bstack1l1l11l_opy_ (u"ࠫࡦࡶࡩ࠰ࡸ࠴࠳ࡧࡧࡴࡤࡪࠪႈ"):
            cls.bstack1l1l1ll1ll_opy_.add(bstack1l1l111l11_opy_)
        elif bstack1l1l1l111l_opy_ == bstack1l1l11l_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࡵࠪႉ"):
            cls.bstack1l1l1111ll_opy_([bstack1l1l111l11_opy_], bstack1l1l1l111l_opy_)
    @classmethod
    @bstack1ll1111l11_opy_(class_method=True)
    def bstack1l1l1111ll_opy_(cls, bstack1l1l111l11_opy_, bstack1l1l1l111l_opy_=bstack1l1l11l_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡢࡢࡶࡦ࡬ࠬႊ")):
        config = {
            bstack1l1l11l_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨႋ"): cls.default_headers()
        }
        response = bstack111111l1_opy_(bstack1l1l11l_opy_ (u"ࠨࡒࡒࡗ࡙࠭ႌ"), cls.request_url(bstack1l1l1l111l_opy_), bstack1l1l111l11_opy_, config)
        bstack1l11llll1l_opy_ = response.json()
    @classmethod
    @bstack1ll1111l11_opy_(class_method=True)
    def bstack1l1l111111_opy_(cls, bstack1l1l1l11ll_opy_):
        bstack1l11lll1ll_opy_ = []
        for log in bstack1l1l1l11ll_opy_:
            bstack1l11lll1ll_opy_.append({
                bstack1l1l11l_opy_ (u"ࠩ࡮࡭ࡳࡪႍࠧ"): bstack1l1l11l_opy_ (u"ࠪࡘࡊ࡙ࡔࡠࡎࡒࡋࠬႎ"),
                bstack1l1l11l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪႏ"): log[bstack1l1l11l_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ႐")],
                bstack1l1l11l_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩ႑"): log[bstack1l1l11l_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪ႒")],
                bstack1l1l11l_opy_ (u"ࠨࡪࡷࡸࡵࡥࡲࡦࡵࡳࡳࡳࡹࡥࠨ႓"): {},
                bstack1l1l11l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ႔"): log[bstack1l1l11l_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ႕")],
                bstack1l1l11l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ႖"): log[bstack1l1l11l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ႗")]
            })
        cls.bstack1l1l1l11l1_opy_({
            bstack1l1l11l_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ႘"): bstack1l1l11l_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫ႙"),
            bstack1l1l11l_opy_ (u"ࠨ࡮ࡲ࡫ࡸ࠭ႚ"): bstack1l11lll1ll_opy_
        })
    @classmethod
    @bstack1ll1111l11_opy_(class_method=True)
    def bstack1l1l11ll1l_opy_(cls, steps):
        bstack1l1l11l111_opy_ = []
        for step in steps:
            bstack1l11llll11_opy_ = {
                bstack1l1l11l_opy_ (u"ࠩ࡮࡭ࡳࡪࠧႛ"): bstack1l1l11l_opy_ (u"ࠪࡘࡊ࡙ࡔࡠࡕࡗࡉࡕ࠭ႜ"),
                bstack1l1l11l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪႝ"): step[bstack1l1l11l_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ႞")],
                bstack1l1l11l_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩ႟"): step[bstack1l1l11l_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪႠ")],
                bstack1l1l11l_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩႡ"): step[bstack1l1l11l_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪႢ")],
                bstack1l1l11l_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࠬႣ"): step[bstack1l1l11l_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳ࠭Ⴄ")]
            }
            if bstack1l1l11l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬႥ") in step:
                bstack1l11llll11_opy_[bstack1l1l11l_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭Ⴆ")] = step[bstack1l1l11l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧႧ")]
            elif bstack1l1l11l_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨႨ") in step:
                bstack1l11llll11_opy_[bstack1l1l11l_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩႩ")] = step[bstack1l1l11l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪႪ")]
            bstack1l1l11l111_opy_.append(bstack1l11llll11_opy_)
        cls.bstack1l1l1l11l1_opy_({
            bstack1l1l11l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨႫ"): bstack1l1l11l_opy_ (u"ࠬࡒ࡯ࡨࡅࡵࡩࡦࡺࡥࡥࠩႬ"),
            bstack1l1l11l_opy_ (u"࠭࡬ࡰࡩࡶࠫႭ"): bstack1l1l11l111_opy_
        })
    @classmethod
    @bstack1ll1111l11_opy_(class_method=True)
    def bstack1l1l11llll_opy_(cls, screenshot):
        cls.bstack1l1l1l11l1_opy_({
            bstack1l1l11l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫႮ"): bstack1l1l11l_opy_ (u"ࠨࡎࡲ࡫ࡈࡸࡥࡢࡶࡨࡨࠬႯ"),
            bstack1l1l11l_opy_ (u"ࠩ࡯ࡳ࡬ࡹࠧႰ"): [{
                bstack1l1l11l_opy_ (u"ࠪ࡯࡮ࡴࡤࠨႱ"): bstack1l1l11l_opy_ (u"࡙ࠫࡋࡓࡕࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࠭Ⴒ"),
                bstack1l1l11l_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨႳ"): datetime.datetime.utcnow().isoformat() + bstack1l1l11l_opy_ (u"࡚࠭ࠨႴ"),
                bstack1l1l11l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨႵ"): screenshot[bstack1l1l11l_opy_ (u"ࠨ࡫ࡰࡥ࡬࡫ࠧႶ")],
                bstack1l1l11l_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩႷ"): screenshot[bstack1l1l11l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪႸ")]
            }]
        }, bstack1l1l1l111l_opy_=bstack1l1l11l_opy_ (u"ࠫࡦࡶࡩ࠰ࡸ࠴࠳ࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡴࠩႹ"))
    @classmethod
    @bstack1ll1111l11_opy_(class_method=True)
    def bstack111l11l11_opy_(cls, driver):
        bstack1l11ll1lll_opy_ = cls.bstack1l11ll1lll_opy_()
        if not bstack1l11ll1lll_opy_:
            return
        cls.bstack1l1l1l11l1_opy_({
            bstack1l1l11l_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩႺ"): bstack1l1l11l_opy_ (u"࠭ࡃࡃࡖࡖࡩࡸࡹࡩࡰࡰࡆࡶࡪࡧࡴࡦࡦࠪႻ"),
            bstack1l1l11l_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࠩႼ"): {
                bstack1l1l11l_opy_ (u"ࠣࡷࡸ࡭ࡩࠨႽ"): cls.bstack1l11ll1lll_opy_(),
                bstack1l1l11l_opy_ (u"ࠤ࡬ࡲࡹ࡫ࡧࡳࡣࡷ࡭ࡴࡴࡳࠣႾ"): cls.bstack1l11lll11l_opy_(driver)
            }
        })
    @classmethod
    def on(cls):
        if not getattr(cls, bstack1l1l11l_opy_ (u"ࠪࡦࡸࡥࡣࡰࡰࡩ࡭࡬࠭Ⴟ"), None):
            return False
        if not cls.bstack1l11lll111_opy_():
            return False
        if os.environ.get(bstack1l1l11l_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡌ࡚ࡘࠬჀ"), None) is None or os.environ[bstack1l1l11l_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡍ࡛࡙࠭Ⴡ")] == bstack1l1l11l_opy_ (u"ࠨ࡮ࡶ࡮࡯ࠦჂ"):
            return False
        return True
    @classmethod
    def bstack1l11lll111_opy_(cls):
        return bstack1ll111lll1_opy_(cls.bs_config.get(bstack1l1l11l_opy_ (u"ࠧࡵࡧࡶࡸࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫჃ"), False))
    @staticmethod
    def request_url(url):
        return bstack1l1l11l_opy_ (u"ࠨࡽࢀ࠳ࢀࢃࠧჄ").format(bstack1l1l11ll11_opy_, url)
    @staticmethod
    def default_headers():
        headers = {
            bstack1l1l11l_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡘࡾࡶࡥࠨჅ"): bstack1l1l11l_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭჆"),
            bstack1l1l11l_opy_ (u"ࠫ࡝࠳ࡂࡔࡖࡄࡇࡐ࠳ࡔࡆࡕࡗࡓࡕ࡙ࠧჇ"): bstack1l1l11l_opy_ (u"ࠬࡺࡲࡶࡧࠪ჈")
        }
        if os.environ.get(bstack1l1l11l_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡎ࡜࡚ࠧ჉"), None):
            headers[bstack1l1l11l_opy_ (u"ࠧࡂࡷࡷ࡬ࡴࡸࡩࡻࡣࡷ࡭ࡴࡴࠧ჊")] = bstack1l1l11l_opy_ (u"ࠨࡄࡨࡥࡷ࡫ࡲࠡࡽࢀࠫ჋").format(os.environ[bstack1l1l11l_opy_ (u"ࠤࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡊࡘࡖࠥ჌")])
        return headers
    @staticmethod
    def bstack1l11ll1lll_opy_():
        return getattr(threading.current_thread(), bstack1l1l11l_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠧჍ"), None)
    @staticmethod
    def bstack1l11lll11l_opy_(driver):
        return {
            bstack1ll1111111_opy_(): bstack1l1lll1l11_opy_(driver)
        }
    @staticmethod
    def bstack1l11lll1l1_opy_(exception_info, report):
        return [{bstack1l1l11l_opy_ (u"ࠫࡧࡧࡣ࡬ࡶࡵࡥࡨ࡫ࠧ჎"): [exception_info.exconly(), report.longreprtext]}]
    @staticmethod
    def bstack1l1l1111l1_opy_(typename):
        if bstack1l1l11l_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࠣ჏") in typename:
            return bstack1l1l11l_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࡇࡵࡶࡴࡸࠢა")
        return bstack1l1l11l_opy_ (u"ࠢࡖࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡈࡶࡷࡵࡲࠣბ")
    @staticmethod
    def bstack1l1l11l11l_opy_(func):
        def wrap(*args, **kwargs):
            if bstack1llll1lll1_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def bstack1l1l111l1l_opy_(test):
        bstack1l1l111ll1_opy_ = test.parent
        scope = []
        while bstack1l1l111ll1_opy_ is not None:
            scope.append(bstack1l1l111ll1_opy_.name)
            bstack1l1l111ll1_opy_ = bstack1l1l111ll1_opy_.parent
        scope.reverse()
        return scope[2:]
    @staticmethod
    def bstack1l1l1l1111_opy_(hook_type):
        if hook_type == bstack1l1l11l_opy_ (u"ࠣࡄࡈࡊࡔࡘࡅࡠࡇࡄࡇࡍࠨგ"):
            return bstack1l1l11l_opy_ (u"ࠤࡖࡩࡹࡻࡰࠡࡪࡲࡳࡰࠨდ")
        elif hook_type == bstack1l1l11l_opy_ (u"ࠥࡅࡋ࡚ࡅࡓࡡࡈࡅࡈࡎࠢე"):
            return bstack1l1l11l_opy_ (u"࡙ࠦ࡫ࡡࡳࡦࡲࡻࡳࠦࡨࡰࡱ࡮ࠦვ")