# coding: UTF-8
import sys
bstack1l11111l_opy_ = sys.version_info [0] == 2
bstack111llllll_opy_ = 2048
bstack1l111ll1l_opy_ = 7
def bstack11l1lll1_opy_ (bstack11llll11_opy_):
    global bstack11l1ll11l_opy_
    bstack1lll1llll_opy_ = ord (bstack11llll11_opy_ [-1])
    bstack111llll11_opy_ = bstack11llll11_opy_ [:-1]
    bstack11l111l1l_opy_ = bstack1lll1llll_opy_ % len (bstack111llll11_opy_)
    bstack11lll1ll_opy_ = bstack111llll11_opy_ [:bstack11l111l1l_opy_] + bstack111llll11_opy_ [bstack11l111l1l_opy_:]
    if bstack1l11111l_opy_:
        bstack1lll111_opy_ = unicode () .join ([unichr (ord (char) - bstack111llllll_opy_ - (bstack1lll1111_opy_ + bstack1lll1llll_opy_) % bstack1l111ll1l_opy_) for bstack1lll1111_opy_, char in enumerate (bstack11lll1ll_opy_)])
    else:
        bstack1lll111_opy_ = str () .join ([chr (ord (char) - bstack111llllll_opy_ - (bstack1lll1111_opy_ + bstack1lll1llll_opy_) % bstack1l111ll1l_opy_) for bstack1lll1111_opy_, char in enumerate (bstack11lll1ll_opy_)])
    return eval (bstack1lll111_opy_)
import atexit
import os
import signal
import sys
import time
import yaml
import requests
import logging
import threading
import socket
import datetime
import string
import random
import json
import collections.abc
import re
import multiprocessing
import traceback
import copy
from multiprocessing import Pool
from packaging import version
from browserstack.local import Local
from urllib.parse import urlparse
bstack1l1l1ll1l_opy_ = {
	bstack11l1lll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ࠀ"): bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡳࠩࠁ"),
  bstack11l1lll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩࠂ"): bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡫ࡦࡻࠪࠃ"),
  bstack11l1lll1_opy_ (u"ࠨࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠫࠄ"): bstack11l1lll1_opy_ (u"ࠩࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ࠅ"),
  bstack11l1lll1_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪࠆ"): bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫࡟ࡸ࠵ࡦࠫࠇ"),
  bstack11l1lll1_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪࠈ"): bstack11l1lll1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࠧࠉ"),
  bstack11l1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪࠊ"): bstack11l1lll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࠧࠋ"),
  bstack11l1lll1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧࠌ"): bstack11l1lll1_opy_ (u"ࠪࡲࡦࡳࡥࠨࠍ"),
  bstack11l1lll1_opy_ (u"ࠫࡩ࡫ࡢࡶࡩࠪࠎ"): bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡩ࡫ࡢࡶࡩࠪࠏ"),
  bstack11l1lll1_opy_ (u"࠭ࡣࡰࡰࡶࡳࡱ࡫ࡌࡰࡩࡶࠫࠐ"): bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰࡰࡶࡳࡱ࡫ࠧࠑ"),
  bstack11l1lll1_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸ࠭ࠒ"): bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸ࠭ࠓ"),
  bstack11l1lll1_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯ࡏࡳ࡬ࡹࠧࠔ"): bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡵࡶࡩࡶ࡯ࡏࡳ࡬ࡹࠧࠕ"),
  bstack11l1lll1_opy_ (u"ࠬࡼࡩࡥࡧࡲࠫࠖ"): bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡼࡩࡥࡧࡲࠫࠗ"),
  bstack11l1lll1_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭࠘"): bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭࠙"),
  bstack11l1lll1_opy_ (u"ࠩࡷࡩࡱ࡫࡭ࡦࡶࡵࡽࡑࡵࡧࡴࠩࠚ"): bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡷࡩࡱ࡫࡭ࡦࡶࡵࡽࡑࡵࡧࡴࠩࠛ"),
  bstack11l1lll1_opy_ (u"ࠫ࡬࡫࡯ࡍࡱࡦࡥࡹ࡯࡯࡯ࠩࠜ"): bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡬࡫࡯ࡍࡱࡦࡥࡹ࡯࡯࡯ࠩࠝ"),
  bstack11l1lll1_opy_ (u"࠭ࡴࡪ࡯ࡨࡾࡴࡴࡥࠨࠞ"): bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡪ࡯ࡨࡾࡴࡴࡥࠨࠟ"),
  bstack11l1lll1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪࠠ"): bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫࠡ"),
  bstack11l1lll1_opy_ (u"ࠪࡱࡦࡹ࡫ࡄࡱࡰࡱࡦࡴࡤࡴࠩࠢ"): bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡱࡦࡹ࡫ࡄࡱࡰࡱࡦࡴࡤࡴࠩࠣ"),
  bstack11l1lll1_opy_ (u"ࠬ࡯ࡤ࡭ࡧࡗ࡭ࡲ࡫࡯ࡶࡶࠪࠤ"): bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡯ࡤ࡭ࡧࡗ࡭ࡲ࡫࡯ࡶࡶࠪࠥ"),
  bstack11l1lll1_opy_ (u"ࠧ࡮ࡣࡶ࡯ࡇࡧࡳࡪࡥࡄࡹࡹ࡮ࠧࠦ"): bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡮ࡣࡶ࡯ࡇࡧࡳࡪࡥࡄࡹࡹ࡮ࠧࠧ"),
  bstack11l1lll1_opy_ (u"ࠩࡶࡩࡳࡪࡋࡦࡻࡶࠫࠨ"): bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶࡩࡳࡪࡋࡦࡻࡶࠫࠩ"),
  bstack11l1lll1_opy_ (u"ࠫࡦࡻࡴࡰ࡙ࡤ࡭ࡹ࠭ࠪ"): bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡻࡴࡰ࡙ࡤ࡭ࡹ࠭ࠫ"),
  bstack11l1lll1_opy_ (u"࠭ࡨࡰࡵࡷࡷࠬࠬ"): bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡨࡰࡵࡷࡷࠬ࠭"),
  bstack11l1lll1_opy_ (u"ࠨࡤࡩࡧࡦࡩࡨࡦࠩ࠮"): bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡩࡧࡦࡩࡨࡦࠩ࠯"),
  bstack11l1lll1_opy_ (u"ࠪࡻࡸࡒ࡯ࡤࡣ࡯ࡗࡺࡶࡰࡰࡴࡷࠫ࠰"): bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡻࡸࡒ࡯ࡤࡣ࡯ࡗࡺࡶࡰࡰࡴࡷࠫ࠱"),
  bstack11l1lll1_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡉ࡯ࡳࡵࡕࡩࡸࡺࡲࡪࡥࡷ࡭ࡴࡴࡳࠨ࠲"): bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡪࡩࡴࡣࡥࡰࡪࡉ࡯ࡳࡵࡕࡩࡸࡺࡲࡪࡥࡷ࡭ࡴࡴࡳࠨ࠳"),
  bstack11l1lll1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫ࠴"): bstack11l1lll1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨ࠵"),
  bstack11l1lll1_opy_ (u"ࠩࡵࡩࡦࡲࡍࡰࡤ࡬ࡰࡪ࠭࠶"): bstack11l1lll1_opy_ (u"ࠪࡶࡪࡧ࡬ࡠ࡯ࡲࡦ࡮ࡲࡥࠨ࠷"),
  bstack11l1lll1_opy_ (u"ࠫࡦࡶࡰࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫ࠸"): bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡶࡰࡪࡷࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ࠹"),
  bstack11l1lll1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡔࡥࡵࡹࡲࡶࡰ࠭࠺"): bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡶࡵࡷࡳࡲࡔࡥࡵࡹࡲࡶࡰ࠭࠻"),
  bstack11l1lll1_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡒࡵࡳ࡫࡯࡬ࡦࠩ࠼"): bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡰࡨࡸࡼࡵࡲ࡬ࡒࡵࡳ࡫࡯࡬ࡦࠩ࠽"),
  bstack11l1lll1_opy_ (u"ࠪࡥࡨࡩࡥࡱࡶࡌࡲࡸ࡫ࡣࡶࡴࡨࡇࡪࡸࡴࡴࠩ࠾"): bstack11l1lll1_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡗࡸࡲࡃࡦࡴࡷࡷࠬ࠿"),
  bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧࡀ"): bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧࡁ"),
  bstack11l1lll1_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧࡂ"): bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡴࡱࡸࡶࡨ࡫ࠧࡃ"),
  bstack11l1lll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࡄ"): bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࡅ"),
  bstack11l1lll1_opy_ (u"ࠫ࡭ࡵࡳࡵࡐࡤࡱࡪ࠭ࡆ"): bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡭ࡵࡳࡵࡐࡤࡱࡪ࠭ࡇ"),
}
bstack1ll1l1lll_opy_ = [
  bstack11l1lll1_opy_ (u"࠭࡯ࡴࠩࡈ"),
  bstack11l1lll1_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪࡉ"),
  bstack11l1lll1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪࡊ"),
  bstack11l1lll1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧࡋ"),
  bstack11l1lll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧࡌ"),
  bstack11l1lll1_opy_ (u"ࠫࡷ࡫ࡡ࡭ࡏࡲࡦ࡮ࡲࡥࠨࡍ"),
  bstack11l1lll1_opy_ (u"ࠬࡧࡰࡱ࡫ࡸࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬࡎ"),
]
bstack11l11111_opy_ = {
  bstack11l1lll1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨࡏ"): [bstack11l1lll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡕࡔࡇࡕࡒࡆࡓࡅࠨࡐ"), bstack11l1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡖࡕࡈࡖࡤࡔࡁࡎࡇࠪࡑ")],
  bstack11l1lll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬࡒ"): bstack11l1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄࡇࡈࡋࡓࡔࡡࡎࡉ࡞࠭ࡓ"),
  bstack11l1lll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧࡔ"): bstack11l1lll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇ࡛ࡉࡍࡆࡢࡒࡆࡓࡅࠨࡕ"),
  bstack11l1lll1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫࡖ"): bstack11l1lll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡓࡑࡍࡉࡈ࡚࡟ࡏࡃࡐࡉࠬࡗ"),
  bstack11l1lll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪࡘ"): bstack11l1lll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕ࡙ࠫ"),
  bstack11l1lll1_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯࡚ࠪ"): bstack11l1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡆࡘࡁࡍࡎࡈࡐࡘࡥࡐࡆࡔࡢࡔࡑࡇࡔࡇࡑࡕࡑ࡛ࠬ"),
  bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ࡜"): bstack11l1lll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡒࡏࡄࡃࡏࠫ࡝"),
  bstack11l1lll1_opy_ (u"ࠧࡳࡧࡵࡹࡳ࡚ࡥࡴࡶࡶࠫ࡞"): bstack11l1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓࡥࡔࡆࡕࡗࡗࠬ࡟"),
  bstack11l1lll1_opy_ (u"ࠩࡤࡴࡵ࠭ࡠ"): [bstack11l1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄࡔࡕࡥࡉࡅࠩࡡ"), bstack11l1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅࡕࡖࠧࡢ")],
  bstack11l1lll1_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧࡣ"): bstack11l1lll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡕࡂࡔࡇࡕ࡚ࡆࡈࡉࡍࡋࡗ࡝ࡤࡊࡅࡃࡗࡊࠫࡤ"),
  bstack11l1lll1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫࡥ"): bstack11l1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫࡦ")
}
bstack1111ll1l1_opy_ = {
  bstack11l1lll1_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫࡧ"): [bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡸࡷࡪࡸ࡟࡯ࡣࡰࡩࠬࡨ"), bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫ࡲࡏࡣࡰࡩࠬࡩ")],
  bstack11l1lll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨࡪ"): [bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷࡤࡱࡥࡺࠩ࡫"), bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ࡬")],
  bstack11l1lll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ࡭"): bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ࡮"),
  bstack11l1lll1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨ࡯"): bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨࡰ"),
  bstack11l1lll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࡱ"): bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࡲ"),
  bstack11l1lll1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧࡳ"): [bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡱࡲࡳࠫࡴ"), bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨࡵ")],
  bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧࡶ"): bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩࡷ"),
  bstack11l1lll1_opy_ (u"ࠬࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩࡸ"): bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩࡹ"),
  bstack11l1lll1_opy_ (u"ࠧࡢࡲࡳࠫࡺ"): bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡲࡳࠫࡻ"),
  bstack11l1lll1_opy_ (u"ࠩ࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫࡼ"): bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫࡽ"),
  bstack11l1lll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨࡾ"): bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨࡿ")
}
bstack11l11l1l_opy_ = {
  bstack11l1lll1_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩࢀ"): bstack11l1lll1_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫࢁ"),
  bstack11l1lll1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪࢂ"): [bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫࢃ"), bstack11l1lll1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ࢄ")],
  bstack11l1lll1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩࢅ"): bstack11l1lll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪࢆ"),
  bstack11l1lll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪࢇ"): bstack11l1lll1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧ࢈"),
  bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ࢉ"): [bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪࢊ"), bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡳࡧ࡭ࡦࠩࢋ")],
  bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬࢌ"): bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧࢍ"),
  bstack11l1lll1_opy_ (u"࠭ࡲࡦࡣ࡯ࡑࡴࡨࡩ࡭ࡧࠪࢎ"): bstack11l1lll1_opy_ (u"ࠧࡳࡧࡤࡰࡤࡳ࡯ࡣ࡫࡯ࡩࠬ࢏"),
  bstack11l1lll1_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ࢐"): [bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡳࡴ࡮ࡻ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ࢑"), bstack11l1lll1_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫ࢒")],
  bstack11l1lll1_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡍࡳࡹࡥࡤࡷࡵࡩࡈ࡫ࡲࡵࡵࠪ࢓"): [bstack11l1lll1_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡘࡹ࡬ࡄࡧࡵࡸࡸ࠭࢔"), bstack11l1lll1_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹ࡙ࡳ࡭ࡅࡨࡶࡹ࠭࢕")]
}
bstack1l1l1l1l1_opy_ = [
  bstack11l1lll1_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡉ࡯ࡵࡨࡧࡺࡸࡥࡄࡧࡵࡸࡸ࠭࢖"),
  bstack11l1lll1_opy_ (u"ࠨࡲࡤ࡫ࡪࡒ࡯ࡢࡦࡖࡸࡷࡧࡴࡦࡩࡼࠫࢗ"),
  bstack11l1lll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨ࢘"),
  bstack11l1lll1_opy_ (u"ࠪࡷࡪࡺࡗࡪࡰࡧࡳࡼࡘࡥࡤࡶ࢙ࠪ"),
  bstack11l1lll1_opy_ (u"ࠫࡹ࡯࡭ࡦࡱࡸࡸࡸ࢚࠭"),
  bstack11l1lll1_opy_ (u"ࠬࡹࡴࡳ࡫ࡦࡸࡋ࡯࡬ࡦࡋࡱࡸࡪࡸࡡࡤࡶࡤࡦ࡮ࡲࡩࡵࡻ࢛ࠪ"),
  bstack11l1lll1_opy_ (u"࠭ࡵ࡯ࡪࡤࡲࡩࡲࡥࡥࡒࡵࡳࡲࡶࡴࡃࡧ࡫ࡥࡻ࡯࡯ࡳࠩ࢜"),
  bstack11l1lll1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ࢝"),
  bstack11l1lll1_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭࢞"),
  bstack11l1lll1_opy_ (u"ࠩࡰࡷ࠿࡫ࡤࡨࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ࢟"),
  bstack11l1lll1_opy_ (u"ࠪࡷࡪࡀࡩࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩࢠ"),
  bstack11l1lll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬࢡ"),
]
bstack1llll1l_opy_ = [
  bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩࢢ"),
  bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪࢣ"),
  bstack11l1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢤ"),
  bstack11l1lll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨࢥ"),
  bstack11l1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬࢦ"),
  bstack11l1lll1_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬࢧ"),
  bstack11l1lll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧࢨ"),
  bstack11l1lll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩࢩ"),
  bstack11l1lll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩࢪ"),
  bstack11l1lll1_opy_ (u"ࠧࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠬࢫ")
]
bstack1l1l1ll11_opy_ = [
  bstack11l1lll1_opy_ (u"ࠨࡷࡳࡰࡴࡧࡤࡎࡧࡧ࡭ࡦ࠭ࢬ"),
  bstack11l1lll1_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫࢭ"),
  bstack11l1lll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ࢮ"),
  bstack11l1lll1_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩࢯ"),
  bstack11l1lll1_opy_ (u"ࠬࡺࡥࡴࡶࡓࡶ࡮ࡵࡲࡪࡶࡼࠫࢰ"),
  bstack11l1lll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩࢱ"),
  bstack11l1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩ࡚ࡡࡨࠩࢲ"),
  bstack11l1lll1_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ࢳ"),
  bstack11l1lll1_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫࢴ"),
  bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨࢵ"),
  bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬࢶ"),
  bstack11l1lll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࠫࢷ"),
  bstack11l1lll1_opy_ (u"࠭࡯ࡴࠩࢸ"),
  bstack11l1lll1_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪࢹ"),
  bstack11l1lll1_opy_ (u"ࠨࡪࡲࡷࡹࡹࠧࢺ"),
  bstack11l1lll1_opy_ (u"ࠩࡤࡹࡹࡵࡗࡢ࡫ࡷࠫࢻ"),
  bstack11l1lll1_opy_ (u"ࠪࡶࡪ࡭ࡩࡰࡰࠪࢼ"),
  bstack11l1lll1_opy_ (u"ࠫࡹ࡯࡭ࡦࡼࡲࡲࡪ࠭ࢽ"),
  bstack11l1lll1_opy_ (u"ࠬࡳࡡࡤࡪ࡬ࡲࡪ࠭ࢾ"),
  bstack11l1lll1_opy_ (u"࠭ࡲࡦࡵࡲࡰࡺࡺࡩࡰࡰࠪࢿ"),
  bstack11l1lll1_opy_ (u"ࠧࡪࡦ࡯ࡩ࡙࡯࡭ࡦࡱࡸࡸࠬࣀ"),
  bstack11l1lll1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡐࡴ࡬ࡩࡳࡺࡡࡵ࡫ࡲࡲࠬࣁ"),
  bstack11l1lll1_opy_ (u"ࠩࡹ࡭ࡩ࡫࡯ࠨࣂ"),
  bstack11l1lll1_opy_ (u"ࠪࡲࡴࡖࡡࡨࡧࡏࡳࡦࡪࡔࡪ࡯ࡨࡳࡺࡺࠧࣃ"),
  bstack11l1lll1_opy_ (u"ࠫࡧ࡬ࡣࡢࡥ࡫ࡩࠬࣄ"),
  bstack11l1lll1_opy_ (u"ࠬࡪࡥࡣࡷࡪࠫࣅ"),
  bstack11l1lll1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲ࡙ࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࡵࠪࣆ"),
  bstack11l1lll1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡓࡦࡰࡧࡏࡪࡿࡳࠨࣇ"),
  bstack11l1lll1_opy_ (u"ࠨࡴࡨࡥࡱࡓ࡯ࡣ࡫࡯ࡩࠬࣈ"),
  bstack11l1lll1_opy_ (u"ࠩࡱࡳࡕ࡯ࡰࡦ࡮࡬ࡲࡪ࠭ࣉ"),
  bstack11l1lll1_opy_ (u"ࠪࡧ࡭࡫ࡣ࡬ࡗࡕࡐࠬ࣊"),
  bstack11l1lll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭࣋"),
  bstack11l1lll1_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡈࡵ࡯࡬࡫ࡨࡷࠬ࣌"),
  bstack11l1lll1_opy_ (u"࠭ࡣࡢࡲࡷࡹࡷ࡫ࡃࡳࡣࡶ࡬ࠬ࣍"),
  bstack11l1lll1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫ࣎"),
  bstack11l1lll1_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ࣏"),
  bstack11l1lll1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࡜ࡥࡳࡵ࡬ࡳࡳ࣐࠭"),
  bstack11l1lll1_opy_ (u"ࠪࡲࡴࡈ࡬ࡢࡰ࡮ࡔࡴࡲ࡬ࡪࡰࡪ࣑ࠫ"),
  bstack11l1lll1_opy_ (u"ࠫࡲࡧࡳ࡬ࡕࡨࡲࡩࡑࡥࡺࡵ࣒ࠪ"),
  bstack11l1lll1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡑࡵࡧࡴ࣓ࠩ"),
  bstack11l1lll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡏࡤࠨࣔ"),
  bstack11l1lll1_opy_ (u"ࠧࡥࡧࡧ࡭ࡨࡧࡴࡦࡦࡇࡩࡻ࡯ࡣࡦࠩࣕ"),
  bstack11l1lll1_opy_ (u"ࠨࡪࡨࡥࡩ࡫ࡲࡑࡣࡵࡥࡲࡹࠧࣖ"),
  bstack11l1lll1_opy_ (u"ࠩࡳ࡬ࡴࡴࡥࡏࡷࡰࡦࡪࡸࠧࣗ"),
  bstack11l1lll1_opy_ (u"ࠪࡲࡪࡺࡷࡰࡴ࡮ࡐࡴ࡭ࡳࠨࣘ"),
  bstack11l1lll1_opy_ (u"ࠫࡳ࡫ࡴࡸࡱࡵ࡯ࡑࡵࡧࡴࡑࡳࡸ࡮ࡵ࡮ࡴࠩࣙ"),
  bstack11l1lll1_opy_ (u"ࠬࡩ࡯࡯ࡵࡲࡰࡪࡒ࡯ࡨࡵࠪࣚ"),
  bstack11l1lll1_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ࣛ"),
  bstack11l1lll1_opy_ (u"ࠧࡢࡲࡳ࡭ࡺࡳࡌࡰࡩࡶࠫࣜ"),
  bstack11l1lll1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡃ࡫ࡲࡱࡪࡺࡲࡪࡥࠪࣝ"),
  bstack11l1lll1_opy_ (u"ࠩࡹ࡭ࡩ࡫࡯ࡗ࠴ࠪࣞ"),
  bstack11l1lll1_opy_ (u"ࠪࡱ࡮ࡪࡓࡦࡵࡶ࡭ࡴࡴࡉ࡯ࡵࡷࡥࡱࡲࡁࡱࡲࡶࠫࣟ"),
  bstack11l1lll1_opy_ (u"ࠫࡪࡹࡰࡳࡧࡶࡷࡴ࡙ࡥࡳࡸࡨࡶࠬ࣠"),
  bstack11l1lll1_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳࡌࡰࡩࡶࠫ࣡"),
  bstack11l1lll1_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡄࡦࡳࠫ࣢"),
  bstack11l1lll1_opy_ (u"ࠧࡵࡧ࡯ࡩࡲ࡫ࡴࡳࡻࡏࡳ࡬ࡹࣣࠧ"),
  bstack11l1lll1_opy_ (u"ࠨࡵࡼࡲࡨ࡚ࡩ࡮ࡧ࡚࡭ࡹ࡮ࡎࡕࡒࠪࣤ"),
  bstack11l1lll1_opy_ (u"ࠩࡪࡩࡴࡒ࡯ࡤࡣࡷ࡭ࡴࡴࠧࣥ"),
  bstack11l1lll1_opy_ (u"ࠪ࡫ࡵࡹࡌࡰࡥࡤࡸ࡮ࡵ࡮ࠨࣦ"),
  bstack11l1lll1_opy_ (u"ࠫࡳ࡫ࡴࡸࡱࡵ࡯ࡕࡸ࡯ࡧ࡫࡯ࡩࠬࣧ"),
  bstack11l1lll1_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡓ࡫ࡴࡸࡱࡵ࡯ࠬࣨ"),
  bstack11l1lll1_opy_ (u"࠭ࡦࡰࡴࡦࡩࡈ࡮ࡡ࡯ࡩࡨࡎࡦࡸࣩࠧ"),
  bstack11l1lll1_opy_ (u"ࠧࡹ࡯ࡶࡎࡦࡸࠧ࣪"),
  bstack11l1lll1_opy_ (u"ࠨࡺࡰࡼࡏࡧࡲࠨ࣫"),
  bstack11l1lll1_opy_ (u"ࠩࡰࡥࡸࡱࡃࡰ࡯ࡰࡥࡳࡪࡳࠨ࣬"),
  bstack11l1lll1_opy_ (u"ࠪࡱࡦࡹ࡫ࡃࡣࡶ࡭ࡨࡇࡵࡵࡪ࣭ࠪ"),
  bstack11l1lll1_opy_ (u"ࠫࡼࡹࡌࡰࡥࡤࡰࡘࡻࡰࡱࡱࡵࡸ࣮ࠬ"),
  bstack11l1lll1_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡉ࡯ࡳࡵࡕࡩࡸࡺࡲࡪࡥࡷ࡭ࡴࡴࡳࠨ࣯"),
  bstack11l1lll1_opy_ (u"࠭ࡡࡱࡲ࡙ࡩࡷࡹࡩࡰࡰࣰࠪ"),
  bstack11l1lll1_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡉ࡯ࡵࡨࡧࡺࡸࡥࡄࡧࡵࡸࡸࣱ࠭"),
  bstack11l1lll1_opy_ (u"ࠨࡴࡨࡷ࡮࡭࡮ࡂࡲࡳࣲࠫ"),
  bstack11l1lll1_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡲ࡮ࡳࡡࡵ࡫ࡲࡲࡸ࠭ࣳ"),
  bstack11l1lll1_opy_ (u"ࠪࡧࡦࡴࡡࡳࡻࠪࣴ"),
  bstack11l1lll1_opy_ (u"ࠫ࡫࡯ࡲࡦࡨࡲࡼࠬࣵ"),
  bstack11l1lll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࣶࠬ"),
  bstack11l1lll1_opy_ (u"࠭ࡩࡦࠩࣷ"),
  bstack11l1lll1_opy_ (u"ࠧࡦࡦࡪࡩࠬࣸ"),
  bstack11l1lll1_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࠨࣹ"),
  bstack11l1lll1_opy_ (u"ࠩࡴࡹࡪࡻࡥࠨࣺ"),
  bstack11l1lll1_opy_ (u"ࠪ࡭ࡳࡺࡥࡳࡰࡤࡰࠬࣻ"),
  bstack11l1lll1_opy_ (u"ࠫࡦࡶࡰࡔࡶࡲࡶࡪࡉ࡯࡯ࡨ࡬࡫ࡺࡸࡡࡵ࡫ࡲࡲࠬࣼ"),
  bstack11l1lll1_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡈࡧ࡭ࡦࡴࡤࡍࡲࡧࡧࡦࡋࡱ࡮ࡪࡩࡴࡪࡱࡱࠫࣽ"),
  bstack11l1lll1_opy_ (u"࠭࡮ࡦࡶࡺࡳࡷࡱࡌࡰࡩࡶࡉࡽࡩ࡬ࡶࡦࡨࡌࡴࡹࡴࡴࠩࣾ"),
  bstack11l1lll1_opy_ (u"ࠧ࡯ࡧࡷࡻࡴࡸ࡫ࡍࡱࡪࡷࡎࡴࡣ࡭ࡷࡧࡩࡍࡵࡳࡵࡵࠪࣿ"),
  bstack11l1lll1_opy_ (u"ࠨࡷࡳࡨࡦࡺࡥࡂࡲࡳࡗࡪࡺࡴࡪࡰࡪࡷࠬऀ"),
  bstack11l1lll1_opy_ (u"ࠩࡵࡩࡸ࡫ࡲࡷࡧࡇࡩࡻ࡯ࡣࡦࠩँ"),
  bstack11l1lll1_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪं"),
  bstack11l1lll1_opy_ (u"ࠫࡸ࡫࡮ࡥࡍࡨࡽࡸ࠭ः"),
  bstack11l1lll1_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡕࡧࡳࡴࡥࡲࡨࡪ࠭ऄ"),
  bstack11l1lll1_opy_ (u"࠭ࡵࡱࡦࡤࡸࡪࡏ࡯ࡴࡆࡨࡺ࡮ࡩࡥࡔࡧࡷࡸ࡮ࡴࡧࡴࠩअ"),
  bstack11l1lll1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡁࡶࡦ࡬ࡳࡎࡴࡪࡦࡥࡷ࡭ࡴࡴࠧआ"),
  bstack11l1lll1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡂࡲࡳࡰࡪࡖࡡࡺࠩइ"),
  bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪई"),
  bstack11l1lll1_opy_ (u"ࠪࡻࡩ࡯࡯ࡔࡧࡵࡺ࡮ࡩࡥࠨउ"),
  bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ऊ"),
  bstack11l1lll1_opy_ (u"ࠬࡶࡲࡦࡸࡨࡲࡹࡉࡲࡰࡵࡶࡗ࡮ࡺࡥࡕࡴࡤࡧࡰ࡯࡮ࡨࠩऋ"),
  bstack11l1lll1_opy_ (u"࠭ࡨࡪࡩ࡫ࡇࡴࡴࡴࡳࡣࡶࡸࠬऌ"),
  bstack11l1lll1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡐࡳࡧࡩࡩࡷ࡫࡮ࡤࡧࡶࠫऍ"),
  bstack11l1lll1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡔ࡫ࡰࠫऎ"),
  bstack11l1lll1_opy_ (u"ࠩࡶ࡭ࡲࡕࡰࡵ࡫ࡲࡲࡸ࠭ए"),
  bstack11l1lll1_opy_ (u"ࠪࡶࡪࡳ࡯ࡷࡧࡌࡓࡘࡇࡰࡱࡕࡨࡸࡹ࡯࡮ࡨࡵࡏࡳࡨࡧ࡬ࡪࡼࡤࡸ࡮ࡵ࡮ࠨऐ"),
  bstack11l1lll1_opy_ (u"ࠫ࡭ࡵࡳࡵࡐࡤࡱࡪ࠭ऑ"),
  bstack11l1lll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧऒ"),
  bstack11l1lll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠨओ"),
  bstack11l1lll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪ࠭औ"),
  bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠪक"),
  bstack11l1lll1_opy_ (u"ࠩࡳࡥ࡬࡫ࡌࡰࡣࡧࡗࡹࡸࡡࡵࡧࡪࡽࠬख"),
  bstack11l1lll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩग"),
  bstack11l1lll1_opy_ (u"ࠫࡹ࡯࡭ࡦࡱࡸࡸࡸ࠭घ"),
  bstack11l1lll1_opy_ (u"ࠬࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡑࡴࡲࡱࡵࡺࡂࡦࡪࡤࡺ࡮ࡵࡲࠨङ")
]
bstack11ll111l_opy_ = {
  bstack11l1lll1_opy_ (u"࠭ࡶࠨच"): bstack11l1lll1_opy_ (u"ࠧࡷࠩछ"),
  bstack11l1lll1_opy_ (u"ࠨࡨࠪज"): bstack11l1lll1_opy_ (u"ࠩࡩࠫझ"),
  bstack11l1lll1_opy_ (u"ࠪࡪࡴࡸࡣࡦࠩञ"): bstack11l1lll1_opy_ (u"ࠫ࡫ࡵࡲࡤࡧࠪट"),
  bstack11l1lll1_opy_ (u"ࠬࡵ࡮࡭ࡻࡤࡹࡹࡵ࡭ࡢࡶࡨࠫठ"): bstack11l1lll1_opy_ (u"࠭࡯࡯࡮ࡼࡅࡺࡺ࡯࡮ࡣࡷࡩࠬड"),
  bstack11l1lll1_opy_ (u"ࠧࡧࡱࡵࡧࡪࡲ࡯ࡤࡣ࡯ࠫढ"): bstack11l1lll1_opy_ (u"ࠨࡨࡲࡶࡨ࡫࡬ࡰࡥࡤࡰࠬण"),
  bstack11l1lll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡩࡱࡶࡸࠬत"): bstack11l1lll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡊࡲࡷࡹ࠭थ"),
  bstack11l1lll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡳࡳࡷࡺࠧद"): bstack11l1lll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡔࡴࡸࡴࠨध"),
  bstack11l1lll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࡺࡹࡥࡳࠩन"): bstack11l1lll1_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡛ࡳࡦࡴࠪऩ"),
  bstack11l1lll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡰࡢࡵࡶࠫप"): bstack11l1lll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡣࡶࡷࠬफ"),
  bstack11l1lll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡲࡵࡳࡽࡿࡨࡰࡵࡷࠫब"): bstack11l1lll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡉࡱࡶࡸࠬभ"),
  bstack11l1lll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡴࡷࡵࡸࡺࡲࡲࡶࡹ࠭म"): bstack11l1lll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡓࡳࡷࡺࠧय"),
  bstack11l1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡶࡲࡰࡺࡼࡹࡸ࡫ࡲࠨर"): bstack11l1lll1_opy_ (u"ࠨ࠯࡯ࡳࡨࡧ࡬ࡑࡴࡲࡼࡾ࡛ࡳࡦࡴࠪऱ"),
  bstack11l1lll1_opy_ (u"ࠩ࠰ࡰࡴࡩࡡ࡭ࡲࡵࡳࡽࡿࡵࡴࡧࡵࠫल"): bstack11l1lll1_opy_ (u"ࠪ࠱ࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡖࡵࡨࡶࠬळ"),
  bstack11l1lll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡳࡶࡴࡾࡹࡱࡣࡶࡷࠬऴ"): bstack11l1lll1_opy_ (u"ࠬ࠳࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡓࡥࡸࡹࠧव"),
  bstack11l1lll1_opy_ (u"࠭࠭࡭ࡱࡦࡥࡱࡶࡲࡰࡺࡼࡴࡦࡹࡳࠨश"): bstack11l1lll1_opy_ (u"ࠧ࠮࡮ࡲࡧࡦࡲࡐࡳࡱࡻࡽࡕࡧࡳࡴࠩष"),
  bstack11l1lll1_opy_ (u"ࠨࡤ࡬ࡲࡦࡸࡹࡱࡣࡷ࡬ࠬस"): bstack11l1lll1_opy_ (u"ࠩࡥ࡭ࡳࡧࡲࡺࡲࡤࡸ࡭࠭ह"),
  bstack11l1lll1_opy_ (u"ࠪࡴࡦࡩࡦࡪ࡮ࡨࠫऺ"): bstack11l1lll1_opy_ (u"ࠫ࠲ࡶࡡࡤ࠯ࡩ࡭ࡱ࡫ࠧऻ"),
  bstack11l1lll1_opy_ (u"ࠬࡶࡡࡤ࠯ࡩ࡭ࡱ࡫़ࠧ"): bstack11l1lll1_opy_ (u"࠭࠭ࡱࡣࡦ࠱࡫࡯࡬ࡦࠩऽ"),
  bstack11l1lll1_opy_ (u"ࠧ࠮ࡲࡤࡧ࠲࡬ࡩ࡭ࡧࠪा"): bstack11l1lll1_opy_ (u"ࠨ࠯ࡳࡥࡨ࠳ࡦࡪ࡮ࡨࠫि"),
  bstack11l1lll1_opy_ (u"ࠩ࡯ࡳ࡬࡬ࡩ࡭ࡧࠪी"): bstack11l1lll1_opy_ (u"ࠪࡰࡴ࡭ࡦࡪ࡮ࡨࠫु"),
  bstack11l1lll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ू"): bstack11l1lll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧृ"),
}
bstack11ll11l11_opy_ = bstack11l1lll1_opy_ (u"࠭ࡨࡵࡶࡳࡷ࠿࠵࠯ࡩࡷࡥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡸࡦ࠲࡬ࡺࡨࠧॄ")
bstack11lllll1l_opy_ = bstack11l1lll1_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯ࡩࡷࡥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠪॅ")
bstack1l1l11ll_opy_ = bstack11l1lll1_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱࡫ࡹࡧ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡱࡩࡽࡺ࡟ࡩࡷࡥࡷࠬॆ")
bstack1l111l1l_opy_ = {
  bstack11l1lll1_opy_ (u"ࠩࡦࡶ࡮ࡺࡩࡤࡣ࡯ࠫे"): 50,
  bstack11l1lll1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩै"): 40,
  bstack11l1lll1_opy_ (u"ࠫࡼࡧࡲ࡯࡫ࡱ࡫ࠬॉ"): 30,
  bstack11l1lll1_opy_ (u"ࠬ࡯࡮ࡧࡱࠪॊ"): 20,
  bstack11l1lll1_opy_ (u"࠭ࡤࡦࡤࡸ࡫ࠬो"): 10
}
bstack1ll11ll_opy_ = bstack1l111l1l_opy_[bstack11l1lll1_opy_ (u"ࠧࡪࡰࡩࡳࠬौ")]
bstack1l11l1l_opy_ = bstack11l1lll1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵्ࠧ")
bstack1l1111ll_opy_ = bstack11l1lll1_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࠧॎ")
bstack1lll1ll1l_opy_ = bstack11l1lll1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧ࠰ࡴࡾࡺࡨࡰࡰࡤ࡫ࡪࡴࡴ࠰ࠩॏ")
bstack11llll1_opy_ = bstack11l1lll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡵࡿࡴࡩࡱࡱࡥ࡬࡫࡮ࡵ࠱ࠪॐ")
bstack1l11ll111_opy_ = [bstack11l1lll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ࠭॑"), bstack11l1lll1_opy_ (u"࡙࠭ࡐࡗࡕࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ॒࠭")]
bstack11lll1l1_opy_ = [bstack11l1lll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪ॓"), bstack11l1lll1_opy_ (u"ࠨ࡛ࡒ࡙ࡗࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪ॔")]
bstack1l11l1111_opy_ = [
  bstack11l1lll1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡔࡡ࡮ࡧࠪॕ"),
  bstack11l1lll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬॖ"),
  bstack11l1lll1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨॗ"),
  bstack11l1lll1_opy_ (u"ࠬࡴࡥࡸࡅࡲࡱࡲࡧ࡮ࡥࡖ࡬ࡱࡪࡵࡵࡵࠩक़"),
  bstack11l1lll1_opy_ (u"࠭ࡡࡱࡲࠪख़"),
  bstack11l1lll1_opy_ (u"ࠧࡶࡦ࡬ࡨࠬग़"),
  bstack11l1lll1_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࠪज़"),
  bstack11l1lll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡦࠩड़"),
  bstack11l1lll1_opy_ (u"ࠪࡳࡷ࡯ࡥ࡯ࡶࡤࡸ࡮ࡵ࡮ࠨढ़"),
  bstack11l1lll1_opy_ (u"ࠫࡦࡻࡴࡰ࡙ࡨࡦࡻ࡯ࡥࡸࠩफ़"),
  bstack11l1lll1_opy_ (u"ࠬࡴ࡯ࡓࡧࡶࡩࡹ࠭य़"), bstack11l1lll1_opy_ (u"࠭ࡦࡶ࡮࡯ࡖࡪࡹࡥࡵࠩॠ"),
  bstack11l1lll1_opy_ (u"ࠧࡤ࡮ࡨࡥࡷ࡙ࡹࡴࡶࡨࡱࡋ࡯࡬ࡦࡵࠪॡ"),
  bstack11l1lll1_opy_ (u"ࠨࡧࡹࡩࡳࡺࡔࡪ࡯࡬ࡲ࡬ࡹࠧॢ"),
  bstack11l1lll1_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡒࡨࡶ࡫ࡵࡲ࡮ࡣࡱࡧࡪࡒ࡯ࡨࡩ࡬ࡲ࡬࠭ॣ"),
  bstack11l1lll1_opy_ (u"ࠪࡳࡹ࡮ࡥࡳࡃࡳࡴࡸ࠭।"),
  bstack11l1lll1_opy_ (u"ࠫࡵࡸࡩ࡯ࡶࡓࡥ࡬࡫ࡓࡰࡷࡵࡧࡪࡕ࡮ࡇ࡫ࡱࡨࡋࡧࡩ࡭ࡷࡵࡩࠬ॥"),
  bstack11l1lll1_opy_ (u"ࠬࡧࡰࡱࡃࡦࡸ࡮ࡼࡩࡵࡻࠪ०"), bstack11l1lll1_opy_ (u"࠭ࡡࡱࡲࡓࡥࡨࡱࡡࡨࡧࠪ१"), bstack11l1lll1_opy_ (u"ࠧࡢࡲࡳ࡛ࡦ࡯ࡴࡂࡥࡷ࡭ࡻ࡯ࡴࡺࠩ२"), bstack11l1lll1_opy_ (u"ࠨࡣࡳࡴ࡜ࡧࡩࡵࡒࡤࡧࡰࡧࡧࡦࠩ३"), bstack11l1lll1_opy_ (u"ࠩࡤࡴࡵ࡝ࡡࡪࡶࡇࡹࡷࡧࡴࡪࡱࡱࠫ४"),
  bstack11l1lll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡕࡩࡦࡪࡹࡕ࡫ࡰࡩࡴࡻࡴࠨ५"),
  bstack11l1lll1_opy_ (u"ࠫࡦࡲ࡬ࡰࡹࡗࡩࡸࡺࡐࡢࡥ࡮ࡥ࡬࡫ࡳࠨ६"),
  bstack11l1lll1_opy_ (u"ࠬࡧ࡮ࡥࡴࡲ࡭ࡩࡉ࡯ࡷࡧࡵࡥ࡬࡫ࠧ७"), bstack11l1lll1_opy_ (u"࠭ࡡ࡯ࡦࡵࡳ࡮ࡪࡃࡰࡸࡨࡶࡦ࡭ࡥࡆࡰࡧࡍࡳࡺࡥ࡯ࡶࠪ८"),
  bstack11l1lll1_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࡅࡧࡹ࡭ࡨ࡫ࡒࡦࡣࡧࡽ࡙࡯࡭ࡦࡱࡸࡸࠬ९"),
  bstack11l1lll1_opy_ (u"ࠨࡣࡧࡦࡕࡵࡲࡵࠩ॰"),
  bstack11l1lll1_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡇࡩࡻ࡯ࡣࡦࡕࡲࡧࡰ࡫ࡴࠨॱ"),
  bstack11l1lll1_opy_ (u"ࠪࡥࡳࡪࡲࡰ࡫ࡧࡍࡳࡹࡴࡢ࡮࡯ࡘ࡮ࡳࡥࡰࡷࡷࠫॲ"),
  bstack11l1lll1_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࡎࡴࡳࡵࡣ࡯ࡰࡕࡧࡴࡩࠩॳ"),
  bstack11l1lll1_opy_ (u"ࠬࡧࡶࡥࠩॴ"), bstack11l1lll1_opy_ (u"࠭ࡡࡷࡦࡏࡥࡺࡴࡣࡩࡖ࡬ࡱࡪࡵࡵࡵࠩॵ"), bstack11l1lll1_opy_ (u"ࠧࡢࡸࡧࡖࡪࡧࡤࡺࡖ࡬ࡱࡪࡵࡵࡵࠩॶ"), bstack11l1lll1_opy_ (u"ࠨࡣࡹࡨࡆࡸࡧࡴࠩॷ"),
  bstack11l1lll1_opy_ (u"ࠩࡸࡷࡪࡑࡥࡺࡵࡷࡳࡷ࡫ࠧॸ"), bstack11l1lll1_opy_ (u"ࠪ࡯ࡪࡿࡳࡵࡱࡵࡩࡕࡧࡴࡩࠩॹ"), bstack11l1lll1_opy_ (u"ࠫࡰ࡫ࡹࡴࡶࡲࡶࡪࡖࡡࡴࡵࡺࡳࡷࡪࠧॺ"),
  bstack11l1lll1_opy_ (u"ࠬࡱࡥࡺࡃ࡯࡭ࡦࡹࠧॻ"), bstack11l1lll1_opy_ (u"࠭࡫ࡦࡻࡓࡥࡸࡹࡷࡰࡴࡧࠫॼ"),
  bstack11l1lll1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷࡋࡸࡦࡥࡸࡸࡦࡨ࡬ࡦࠩॽ"), bstack11l1lll1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡥࡴ࡬ࡺࡪࡸࡁࡳࡩࡶࠫॾ"), bstack11l1lll1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡦࡵ࡭ࡻ࡫ࡲࡆࡺࡨࡧࡺࡺࡡࡣ࡮ࡨࡈ࡮ࡸࠧॿ"), bstack11l1lll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡧࡶ࡮ࡼࡥࡳࡅ࡫ࡶࡴࡳࡥࡎࡣࡳࡴ࡮ࡴࡧࡇ࡫࡯ࡩࠬঀ"), bstack11l1lll1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࡨࡷ࡯ࡶࡦࡴࡘࡷࡪ࡙ࡹࡴࡶࡨࡱࡊࡾࡥࡤࡷࡷࡥࡧࡲࡥࠨঁ"),
  bstack11l1lll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡩࡸࡩࡷࡧࡵࡔࡴࡸࡴࠨং"), bstack11l1lll1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡪࡲࡪࡸࡨࡶࡕࡵࡲࡵࡵࠪঃ"),
  bstack11l1lll1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷࡊࡩࡴࡣࡥࡰࡪࡈࡵࡪ࡮ࡧࡇ࡭࡫ࡣ࡬ࠩ঄"),
  bstack11l1lll1_opy_ (u"ࠨࡣࡸࡸࡴ࡝ࡥࡣࡸ࡬ࡩࡼ࡚ࡩ࡮ࡧࡲࡹࡹ࠭অ"),
  bstack11l1lll1_opy_ (u"ࠩ࡬ࡲࡹ࡫࡮ࡵࡃࡦࡸ࡮ࡵ࡮ࠨআ"), bstack11l1lll1_opy_ (u"ࠪ࡭ࡳࡺࡥ࡯ࡶࡆࡥࡹ࡫ࡧࡰࡴࡼࠫই"), bstack11l1lll1_opy_ (u"ࠫ࡮ࡴࡴࡦࡰࡷࡊࡱࡧࡧࡴࠩঈ"), bstack11l1lll1_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡦࡲࡉ࡯ࡶࡨࡲࡹࡇࡲࡨࡷࡰࡩࡳࡺࡳࠨউ"),
  bstack11l1lll1_opy_ (u"࠭ࡤࡰࡰࡷࡗࡹࡵࡰࡂࡲࡳࡓࡳࡘࡥࡴࡧࡷࠫঊ"),
  bstack11l1lll1_opy_ (u"ࠧࡶࡰ࡬ࡧࡴࡪࡥࡌࡧࡼࡦࡴࡧࡲࡥࠩঋ"), bstack11l1lll1_opy_ (u"ࠨࡴࡨࡷࡪࡺࡋࡦࡻࡥࡳࡦࡸࡤࠨঌ"),
  bstack11l1lll1_opy_ (u"ࠩࡱࡳࡘ࡯ࡧ࡯ࠩ঍"),
  bstack11l1lll1_opy_ (u"ࠪ࡭࡬ࡴ࡯ࡳࡧࡘࡲ࡮ࡳࡰࡰࡴࡷࡥࡳࡺࡖࡪࡧࡺࡷࠬ঎"),
  bstack11l1lll1_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡆࡴࡤࡳࡱ࡬ࡨ࡜ࡧࡴࡤࡪࡨࡶࡸ࠭এ"),
  bstack11l1lll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬঐ"),
  bstack11l1lll1_opy_ (u"࠭ࡲࡦࡥࡵࡩࡦࡺࡥࡄࡪࡵࡳࡲ࡫ࡄࡳ࡫ࡹࡩࡷ࡙ࡥࡴࡵ࡬ࡳࡳࡹࠧ঑"),
  bstack11l1lll1_opy_ (u"ࠧ࡯ࡣࡷ࡭ࡻ࡫ࡗࡦࡤࡖࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹ࠭঒"),
  bstack11l1lll1_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࡕࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡕࡧࡴࡩࠩও"),
  bstack11l1lll1_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡖࡴࡪ࡫ࡤࠨঔ"),
  bstack11l1lll1_opy_ (u"ࠪ࡫ࡵࡹࡅ࡯ࡣࡥࡰࡪࡪࠧক"),
  bstack11l1lll1_opy_ (u"ࠫ࡮ࡹࡈࡦࡣࡧࡰࡪࡹࡳࠨখ"),
  bstack11l1lll1_opy_ (u"ࠬࡧࡤࡣࡇࡻࡩࡨ࡚ࡩ࡮ࡧࡲࡹࡹ࠭গ"),
  bstack11l1lll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡪ࡙ࡣࡳ࡫ࡳࡸࠬঘ"),
  bstack11l1lll1_opy_ (u"ࠧࡴ࡭࡬ࡴࡉ࡫ࡶࡪࡥࡨࡍࡳ࡯ࡴࡪࡣ࡯࡭ࡿࡧࡴࡪࡱࡱࠫঙ"),
  bstack11l1lll1_opy_ (u"ࠨࡣࡸࡸࡴࡍࡲࡢࡰࡷࡔࡪࡸ࡭ࡪࡵࡶ࡭ࡴࡴࡳࠨচ"),
  bstack11l1lll1_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡑࡥࡹࡻࡲࡢ࡮ࡒࡶ࡮࡫࡮ࡵࡣࡷ࡭ࡴࡴࠧছ"),
  bstack11l1lll1_opy_ (u"ࠪࡷࡾࡹࡴࡦ࡯ࡓࡳࡷࡺࠧজ"),
  bstack11l1lll1_opy_ (u"ࠫࡷ࡫࡭ࡰࡶࡨࡅࡩࡨࡈࡰࡵࡷࠫঝ"),
  bstack11l1lll1_opy_ (u"ࠬࡹ࡫ࡪࡲࡘࡲࡱࡵࡣ࡬ࠩঞ"), bstack11l1lll1_opy_ (u"࠭ࡵ࡯࡮ࡲࡧࡰ࡚ࡹࡱࡧࠪট"), bstack11l1lll1_opy_ (u"ࠧࡶࡰ࡯ࡳࡨࡱࡋࡦࡻࠪঠ"),
  bstack11l1lll1_opy_ (u"ࠨࡣࡸࡸࡴࡒࡡࡶࡰࡦ࡬ࠬড"),
  bstack11l1lll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡌࡰࡩࡦࡥࡹࡉࡡࡱࡶࡸࡶࡪ࠭ঢ"),
  bstack11l1lll1_opy_ (u"ࠪࡹࡳ࡯࡮ࡴࡶࡤࡰࡱࡕࡴࡩࡧࡵࡔࡦࡩ࡫ࡢࡩࡨࡷࠬণ"),
  bstack11l1lll1_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩ࡜࡯࡮ࡥࡱࡺࡅࡳ࡯࡭ࡢࡶ࡬ࡳࡳ࠭ত"),
  bstack11l1lll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡘࡴࡵ࡬ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩথ"),
  bstack11l1lll1_opy_ (u"࠭ࡥ࡯ࡨࡲࡶࡨ࡫ࡁࡱࡲࡌࡲࡸࡺࡡ࡭࡮ࠪদ"),
  bstack11l1lll1_opy_ (u"ࠧࡦࡰࡶࡹࡷ࡫ࡗࡦࡤࡹ࡭ࡪࡽࡳࡉࡣࡹࡩࡕࡧࡧࡦࡵࠪধ"), bstack11l1lll1_opy_ (u"ࠨࡹࡨࡦࡻ࡯ࡥࡸࡆࡨࡺࡹࡵ࡯࡭ࡵࡓࡳࡷࡺࠧন"), bstack11l1lll1_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦ࡙ࡨࡦࡻ࡯ࡥࡸࡆࡨࡸࡦ࡯࡬ࡴࡅࡲࡰࡱ࡫ࡣࡵ࡫ࡲࡲࠬ঩"),
  bstack11l1lll1_opy_ (u"ࠪࡶࡪࡳ࡯ࡵࡧࡄࡴࡵࡹࡃࡢࡥ࡫ࡩࡑ࡯࡭ࡪࡶࠪপ"),
  bstack11l1lll1_opy_ (u"ࠫࡨࡧ࡬ࡦࡰࡧࡥࡷࡌ࡯ࡳ࡯ࡤࡸࠬফ"),
  bstack11l1lll1_opy_ (u"ࠬࡨࡵ࡯ࡦ࡯ࡩࡎࡪࠧব"),
  bstack11l1lll1_opy_ (u"࠭࡬ࡢࡷࡱࡧ࡭࡚ࡩ࡮ࡧࡲࡹࡹ࠭ভ"),
  bstack11l1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡹ࡯࡯࡯ࡕࡨࡶࡻ࡯ࡣࡦࡵࡈࡲࡦࡨ࡬ࡦࡦࠪম"), bstack11l1lll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࡖࡩࡷࡼࡩࡤࡧࡶࡅࡺࡺࡨࡰࡴ࡬ࡾࡪࡪࠧয"),
  bstack11l1lll1_opy_ (u"ࠩࡤࡹࡹࡵࡁࡤࡥࡨࡴࡹࡇ࡬ࡦࡴࡷࡷࠬর"), bstack11l1lll1_opy_ (u"ࠪࡥࡺࡺ࡯ࡅ࡫ࡶࡱ࡮ࡹࡳࡂ࡮ࡨࡶࡹࡹࠧ঱"),
  bstack11l1lll1_opy_ (u"ࠫࡳࡧࡴࡪࡸࡨࡍࡳࡹࡴࡳࡷࡰࡩࡳࡺࡳࡍ࡫ࡥࠫল"),
  bstack11l1lll1_opy_ (u"ࠬࡴࡡࡵ࡫ࡹࡩ࡜࡫ࡢࡕࡣࡳࠫ঳"),
  bstack11l1lll1_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮ࡏ࡮ࡪࡶ࡬ࡥࡱ࡛ࡲ࡭ࠩ঴"), bstack11l1lll1_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯ࡁ࡭࡮ࡲࡻࡕࡵࡰࡶࡲࡶࠫ঵"), bstack11l1lll1_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࡊࡩࡱࡳࡷ࡫ࡆࡳࡣࡸࡨ࡜ࡧࡲ࡯࡫ࡱ࡫ࠬশ"), bstack11l1lll1_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࡑࡳࡩࡳࡒࡩ࡯࡭ࡶࡍࡳࡈࡡࡤ࡭ࡪࡶࡴࡻ࡮ࡥࠩষ"),
  bstack11l1lll1_opy_ (u"ࠪ࡯ࡪ࡫ࡰࡌࡧࡼࡇ࡭ࡧࡩ࡯ࡵࠪস"),
  bstack11l1lll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮࡬ࡾࡦࡨ࡬ࡦࡕࡷࡶ࡮ࡴࡧࡴࡆ࡬ࡶࠬহ"),
  bstack11l1lll1_opy_ (u"ࠬࡶࡲࡰࡥࡨࡷࡸࡇࡲࡨࡷࡰࡩࡳࡺࡳࠨ঺"),
  bstack11l1lll1_opy_ (u"࠭ࡩ࡯ࡶࡨࡶࡐ࡫ࡹࡅࡧ࡯ࡥࡾ࠭঻"),
  bstack11l1lll1_opy_ (u"ࠧࡴࡪࡲࡻࡎࡕࡓࡍࡱࡪ়ࠫ"),
  bstack11l1lll1_opy_ (u"ࠨࡵࡨࡲࡩࡑࡥࡺࡕࡷࡶࡦࡺࡥࡨࡻࠪঽ"),
  bstack11l1lll1_opy_ (u"ࠩࡺࡩࡧࡱࡩࡵࡔࡨࡷࡵࡵ࡮ࡴࡧࡗ࡭ࡲ࡫࡯ࡶࡶࠪা"), bstack11l1lll1_opy_ (u"ࠪࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡗࡢ࡫ࡷࡘ࡮ࡳࡥࡰࡷࡷࠫি"),
  bstack11l1lll1_opy_ (u"ࠫࡷ࡫࡭ࡰࡶࡨࡈࡪࡨࡵࡨࡒࡵࡳࡽࡿࠧী"),
  bstack11l1lll1_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡆࡹࡹ࡯ࡥࡈࡼࡪࡩࡵࡵࡧࡉࡶࡴࡳࡈࡵࡶࡳࡷࠬু"),
  bstack11l1lll1_opy_ (u"࠭ࡳ࡬࡫ࡳࡐࡴ࡭ࡃࡢࡲࡷࡹࡷ࡫ࠧূ"),
  bstack11l1lll1_opy_ (u"ࠧࡸࡧࡥ࡯࡮ࡺࡄࡦࡤࡸ࡫ࡕࡸ࡯ࡹࡻࡓࡳࡷࡺࠧৃ"),
  bstack11l1lll1_opy_ (u"ࠨࡨࡸࡰࡱࡉ࡯࡯ࡶࡨࡼࡹࡒࡩࡴࡶࠪৄ"),
  bstack11l1lll1_opy_ (u"ࠩࡺࡥ࡮ࡺࡆࡰࡴࡄࡴࡵ࡙ࡣࡳ࡫ࡳࡸࠬ৅"),
  bstack11l1lll1_opy_ (u"ࠪࡻࡪࡨࡶࡪࡧࡺࡇࡴࡴ࡮ࡦࡥࡷࡖࡪࡺࡲࡪࡧࡶࠫ৆"),
  bstack11l1lll1_opy_ (u"ࠫࡦࡶࡰࡏࡣࡰࡩࠬে"),
  bstack11l1lll1_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡘ࡙ࡌࡄࡧࡵࡸࠬৈ"),
  bstack11l1lll1_opy_ (u"࠭ࡴࡢࡲ࡚࡭ࡹ࡮ࡓࡩࡱࡵࡸࡕࡸࡥࡴࡵࡇࡹࡷࡧࡴࡪࡱࡱࠫ৉"),
  bstack11l1lll1_opy_ (u"ࠧࡴࡥࡤࡰࡪࡌࡡࡤࡶࡲࡶࠬ৊"),
  bstack11l1lll1_opy_ (u"ࠨࡹࡧࡥࡑࡵࡣࡢ࡮ࡓࡳࡷࡺࠧো"),
  bstack11l1lll1_opy_ (u"ࠩࡶ࡬ࡴࡽࡘࡤࡱࡧࡩࡑࡵࡧࠨৌ"),
  bstack11l1lll1_opy_ (u"ࠪ࡭ࡴࡹࡉ࡯ࡵࡷࡥࡱࡲࡐࡢࡷࡶࡩ্ࠬ"),
  bstack11l1lll1_opy_ (u"ࠫࡽࡩ࡯ࡥࡧࡆࡳࡳ࡬ࡩࡨࡈ࡬ࡰࡪ࠭ৎ"),
  bstack11l1lll1_opy_ (u"ࠬࡱࡥࡺࡥ࡫ࡥ࡮ࡴࡐࡢࡵࡶࡻࡴࡸࡤࠨ৏"),
  bstack11l1lll1_opy_ (u"࠭ࡵࡴࡧࡓࡶࡪࡨࡵࡪ࡮ࡷ࡛ࡉࡇࠧ৐"),
  bstack11l1lll1_opy_ (u"ࠧࡱࡴࡨࡺࡪࡴࡴࡘࡆࡄࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠨ৑"),
  bstack11l1lll1_opy_ (u"ࠨࡹࡨࡦࡉࡸࡩࡷࡧࡵࡅ࡬࡫࡮ࡵࡗࡵࡰࠬ৒"),
  bstack11l1lll1_opy_ (u"ࠩ࡮ࡩࡾࡩࡨࡢ࡫ࡱࡔࡦࡺࡨࠨ৓"),
  bstack11l1lll1_opy_ (u"ࠪࡹࡸ࡫ࡎࡦࡹ࡚ࡈࡆ࠭৔"),
  bstack11l1lll1_opy_ (u"ࠫࡼࡪࡡࡍࡣࡸࡲࡨ࡮ࡔࡪ࡯ࡨࡳࡺࡺࠧ৕"), bstack11l1lll1_opy_ (u"ࠬࡽࡤࡢࡅࡲࡲࡳ࡫ࡣࡵ࡫ࡲࡲ࡙࡯࡭ࡦࡱࡸࡸࠬ৖"),
  bstack11l1lll1_opy_ (u"࠭ࡸࡤࡱࡧࡩࡔࡸࡧࡊࡦࠪৗ"), bstack11l1lll1_opy_ (u"ࠧࡹࡥࡲࡨࡪ࡙ࡩࡨࡰ࡬ࡲ࡬ࡏࡤࠨ৘"),
  bstack11l1lll1_opy_ (u"ࠨࡷࡳࡨࡦࡺࡥࡥ࡙ࡇࡅࡇࡻ࡮ࡥ࡮ࡨࡍࡩ࠭৙"),
  bstack11l1lll1_opy_ (u"ࠩࡵࡩࡸ࡫ࡴࡐࡰࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡸࡴࡐࡰ࡯ࡽࠬ৚"),
  bstack11l1lll1_opy_ (u"ࠪࡧࡴࡳ࡭ࡢࡰࡧࡘ࡮ࡳࡥࡰࡷࡷࡷࠬ৛"),
  bstack11l1lll1_opy_ (u"ࠫࡼࡪࡡࡔࡶࡤࡶࡹࡻࡰࡓࡧࡷࡶ࡮࡫ࡳࠨড়"), bstack11l1lll1_opy_ (u"ࠬࡽࡤࡢࡕࡷࡥࡷࡺࡵࡱࡔࡨࡸࡷࡿࡉ࡯ࡶࡨࡶࡻࡧ࡬ࠨঢ়"),
  bstack11l1lll1_opy_ (u"࠭ࡣࡰࡰࡱࡩࡨࡺࡈࡢࡴࡧࡻࡦࡸࡥࡌࡧࡼࡦࡴࡧࡲࡥࠩ৞"),
  bstack11l1lll1_opy_ (u"ࠧ࡮ࡣࡻࡘࡾࡶࡩ࡯ࡩࡉࡶࡪࡷࡵࡦࡰࡦࡽࠬয়"),
  bstack11l1lll1_opy_ (u"ࠨࡵ࡬ࡱࡵࡲࡥࡊࡵ࡙࡭ࡸ࡯ࡢ࡭ࡧࡆ࡬ࡪࡩ࡫ࠨৠ"),
  bstack11l1lll1_opy_ (u"ࠩࡸࡷࡪࡉࡡࡳࡶ࡫ࡥ࡬࡫ࡓࡴ࡮ࠪৡ"),
  bstack11l1lll1_opy_ (u"ࠪࡷ࡭ࡵࡵ࡭ࡦࡘࡷࡪ࡙ࡩ࡯ࡩ࡯ࡩࡹࡵ࡮ࡕࡧࡶࡸࡒࡧ࡮ࡢࡩࡨࡶࠬৢ"),
  bstack11l1lll1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡌ࡛ࡉࡖࠧৣ"),
  bstack11l1lll1_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡘࡴࡻࡣࡩࡋࡧࡉࡳࡸ࡯࡭࡮ࠪ৤"),
  bstack11l1lll1_opy_ (u"࠭ࡩࡨࡰࡲࡶࡪࡎࡩࡥࡦࡨࡲࡆࡶࡩࡑࡱ࡯࡭ࡨࡿࡅࡳࡴࡲࡶࠬ৥"),
  bstack11l1lll1_opy_ (u"ࠧ࡮ࡱࡦ࡯ࡑࡵࡣࡢࡶ࡬ࡳࡳࡇࡰࡱࠩ০"),
  bstack11l1lll1_opy_ (u"ࠨ࡮ࡲ࡫ࡨࡧࡴࡇࡱࡵࡱࡦࡺࠧ১"), bstack11l1lll1_opy_ (u"ࠩ࡯ࡳ࡬ࡩࡡࡵࡈ࡬ࡰࡹ࡫ࡲࡔࡲࡨࡧࡸ࠭২"),
  bstack11l1lll1_opy_ (u"ࠪࡥࡱࡲ࡯ࡸࡆࡨࡰࡦࡿࡁࡥࡤࠪ৩")
]
bstack1l1lll111_opy_ = bstack11l1lll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡧࡰࡪ࠯ࡦࡰࡴࡻࡤ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡦࡶࡰ࠮ࡣࡸࡸࡴࡳࡡࡵࡧ࠲ࡹࡵࡲ࡯ࡢࡦࠪ৪")
bstack111ll11l1_opy_ = [bstack11l1lll1_opy_ (u"ࠬ࠴ࡡࡱ࡭ࠪ৫"), bstack11l1lll1_opy_ (u"࠭࠮ࡢࡣࡥࠫ৬"), bstack11l1lll1_opy_ (u"ࠧ࠯࡫ࡳࡥࠬ৭")]
bstack111l1l1l_opy_ = [bstack11l1lll1_opy_ (u"ࠨ࡫ࡧࠫ৮"), bstack11l1lll1_opy_ (u"ࠩࡳࡥࡹ࡮ࠧ৯"), bstack11l1lll1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡢ࡭ࡩ࠭ৰ"), bstack11l1lll1_opy_ (u"ࠫࡸ࡮ࡡࡳࡧࡤࡦࡱ࡫࡟ࡪࡦࠪৱ")]
bstack1l1ll1l1l_opy_ = {
  bstack11l1lll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ৲"): bstack11l1lll1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ৳"),
  bstack11l1lll1_opy_ (u"ࠧࡧ࡫ࡵࡩ࡫ࡵࡸࡐࡲࡷ࡭ࡴࡴࡳࠨ৴"): bstack11l1lll1_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭৵"),
  bstack11l1lll1_opy_ (u"ࠩࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ৶"): bstack11l1lll1_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫ৷"),
  bstack11l1lll1_opy_ (u"ࠫ࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ৸"): bstack11l1lll1_opy_ (u"ࠬࡹࡥ࠻࡫ࡨࡓࡵࡺࡩࡰࡰࡶࠫ৹"),
  bstack11l1lll1_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮ࡕࡰࡵ࡫ࡲࡲࡸ࠭৺"): bstack11l1lll1_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯࠮ࡰࡲࡷ࡭ࡴࡴࡳࠨ৻")
}
bstack11llllll1_opy_ = [
  bstack11l1lll1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ৼ"),
  bstack11l1lll1_opy_ (u"ࠩࡰࡳࡿࡀࡦࡪࡴࡨࡪࡴࡾࡏࡱࡶ࡬ࡳࡳࡹࠧ৽"),
  bstack11l1lll1_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫ৾"),
  bstack11l1lll1_opy_ (u"ࠫࡸ࡫࠺ࡪࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ৿"),
  bstack11l1lll1_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭਀"),
]
bstack111ll1111_opy_ = bstack1llll1l_opy_ + bstack1l1l1ll11_opy_ + bstack1l11l1111_opy_
bstack1lll111l1_opy_ = [
  bstack11l1lll1_opy_ (u"࠭࡞࡭ࡱࡦࡥࡱ࡮࡯ࡴࡶࠧࠫਁ"),
  bstack11l1lll1_opy_ (u"ࠧ࡟ࡤࡶ࠱ࡱࡵࡣࡢ࡮࠱ࡧࡴࡳࠤࠨਂ"),
  bstack11l1lll1_opy_ (u"ࠨࡠ࠴࠶࠼࠴ࠧਃ"),
  bstack11l1lll1_opy_ (u"ࠩࡡ࠵࠵࠴ࠧ਄"),
  bstack11l1lll1_opy_ (u"ࠪࡢ࠶࠽࠲࠯࠳࡞࠺࠲࠿࡝࠯ࠩਅ"),
  bstack11l1lll1_opy_ (u"ࠫࡣ࠷࠷࠳࠰࠵࡟࠵࠳࠹࡞࠰ࠪਆ"),
  bstack11l1lll1_opy_ (u"ࠬࡤ࠱࠸࠴࠱࠷ࡠ࠶࠭࠲࡟࠱ࠫਇ"),
  bstack11l1lll1_opy_ (u"࠭࡞࠲࠻࠵࠲࠶࠼࠸࠯ࠩਈ")
]
bstack1llllll11_opy_ = bstack11l1lll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡣࡳ࡭࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡽࢀࠫਉ")
bstack11111l_opy_ = bstack11l1lll1_opy_ (u"ࠨࡵࡧ࡯࠴ࡼ࠱࠰ࡧࡹࡩࡳࡺࠧਊ")
bstack11ll1l1ll_opy_ = [ bstack11l1lll1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶࡨࠫ਋") ]
bstack1l11lll1_opy_ = [ bstack11l1lll1_opy_ (u"ࠪࡥࡵࡶ࠭ࡢࡷࡷࡳࡲࡧࡴࡦࠩ਌") ]
bstack111l111l1_opy_ = [ bstack11l1lll1_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ਍") ]
bstack1ll1lll11_opy_ = bstack11l1lll1_opy_ (u"࡙ࠬࡄࡌࡕࡨࡸࡺࡶࠧ਎")
bstack11l11ll1l_opy_ = bstack11l1lll1_opy_ (u"࠭ࡓࡅࡍࡗࡩࡸࡺࡁࡵࡶࡨࡱࡵࡺࡥࡥࠩਏ")
bstack1llllll1l_opy_ = bstack11l1lll1_opy_ (u"ࠧࡔࡆࡎࡘࡪࡹࡴࡔࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࠫਐ")
bstack11l1l1ll1_opy_ = bstack11l1lll1_opy_ (u"ࠨ࠶࠱࠴࠳࠶ࠧ਑")
bstack1ll11l1l_opy_ = [
  bstack11l1lll1_opy_ (u"ࠩࡈࡖࡗࡥࡆࡂࡋࡏࡉࡉ࠭਒"),
  bstack11l1lll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡕࡋࡐࡉࡉࡥࡏࡖࡖࠪਓ"),
  bstack11l1lll1_opy_ (u"ࠫࡊࡘࡒࡠࡄࡏࡓࡈࡑࡅࡅࡡࡅ࡝ࡤࡉࡌࡊࡇࡑࡘࠬਔ"),
  bstack11l1lll1_opy_ (u"ࠬࡋࡒࡓࡡࡑࡉ࡙࡝ࡏࡓࡍࡢࡇࡍࡇࡎࡈࡇࡇࠫਕ"),
  bstack11l1lll1_opy_ (u"࠭ࡅࡓࡔࡢࡗࡔࡉࡋࡆࡖࡢࡒࡔ࡚࡟ࡄࡑࡑࡒࡊࡉࡔࡆࡆࠪਖ"),
  bstack11l1lll1_opy_ (u"ࠧࡆࡔࡕࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡅࡏࡓࡘࡋࡄࠨਗ"),
  bstack11l1lll1_opy_ (u"ࠨࡇࡕࡖࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡕࡉࡘࡋࡔࠨਘ"),
  bstack11l1lll1_opy_ (u"ࠩࡈࡖࡗࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡖࡊࡌࡕࡔࡇࡇࠫਙ"),
  bstack11l1lll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡄࡑࡑࡒࡊࡉࡔࡊࡑࡑࡣࡆࡈࡏࡓࡖࡈࡈࠬਚ"),
  bstack11l1lll1_opy_ (u"ࠫࡊࡘࡒࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡌࡁࡊࡎࡈࡈࠬਛ"),
  bstack11l1lll1_opy_ (u"ࠬࡋࡒࡓࡡࡑࡅࡒࡋ࡟ࡏࡑࡗࡣࡗࡋࡓࡐࡎ࡙ࡉࡉ࠭ਜ"),
  bstack11l1lll1_opy_ (u"࠭ࡅࡓࡔࡢࡅࡉࡊࡒࡆࡕࡖࡣࡎࡔࡖࡂࡎࡌࡈࠬਝ"),
  bstack11l1lll1_opy_ (u"ࠧࡆࡔࡕࡣࡆࡊࡄࡓࡇࡖࡗࡤ࡛ࡎࡓࡇࡄࡇࡍࡇࡂࡍࡇࠪਞ"),
  bstack11l1lll1_opy_ (u"ࠨࡇࡕࡖࡤ࡚ࡕࡏࡐࡈࡐࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡉࡅࡎࡒࡅࡅࠩਟ"),
  bstack11l1lll1_opy_ (u"ࠩࡈࡖࡗࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡘࡎࡓࡅࡅࡡࡒ࡙࡙࠭ਠ"),
  bstack11l1lll1_opy_ (u"ࠪࡉࡗࡘ࡟ࡔࡑࡆࡏࡘࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡊࡆࡏࡌࡆࡆࠪਡ"),
  bstack11l1lll1_opy_ (u"ࠫࡊࡘࡒࡠࡕࡒࡇࡐ࡙࡟ࡄࡑࡑࡒࡊࡉࡔࡊࡑࡑࡣࡍࡕࡓࡕࡡࡘࡒࡗࡋࡁࡄࡊࡄࡆࡑࡋࠧਢ"),
  bstack11l1lll1_opy_ (u"ࠬࡋࡒࡓࡡࡓࡖࡔ࡞࡙ࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡌࡁࡊࡎࡈࡈࠬਣ"),
  bstack11l1lll1_opy_ (u"࠭ࡅࡓࡔࡢࡒࡆࡓࡅࡠࡐࡒࡘࡤࡘࡅࡔࡑࡏ࡚ࡊࡊࠧਤ"),
  bstack11l1lll1_opy_ (u"ࠧࡆࡔࡕࡣࡓࡇࡍࡆࡡࡕࡉࡘࡕࡌࡖࡖࡌࡓࡓࡥࡆࡂࡋࡏࡉࡉ࠭ਥ"),
  bstack11l1lll1_opy_ (u"ࠨࡇࡕࡖࡤࡓࡁࡏࡆࡄࡘࡔࡘ࡙ࡠࡒࡕࡓ࡝࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟ࡇࡃࡌࡐࡊࡊࠧਦ"),
]
bstack11lll1lll_opy_ = bstack11l1lll1_opy_ (u"ࠩ࠱࠳ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠰ࡥࡷࡺࡩࡧࡣࡦࡸࡸ࠵ࠧਧ")
def bstack1lll1l1_opy_():
  global CONFIG
  headers = {
        bstack11l1lll1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩਨ"): bstack11l1lll1_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧ਩"),
      }
  proxies = bstack11ll1l1l1_opy_(CONFIG, bstack1l1l11ll_opy_)
  try:
    response = requests.get(bstack1l1l11ll_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack1l111ll_opy_ = response.json()[bstack11l1lll1_opy_ (u"ࠬ࡮ࡵࡣࡵࠪਪ")]
      logger.debug(bstack1l1lll1_opy_.format(response.json()))
      return bstack1l111ll_opy_
    else:
      logger.debug(bstack111l1111l_opy_.format(bstack11l1lll1_opy_ (u"ࠨࡒࡦࡵࡳࡳࡳࡹࡥࠡࡌࡖࡓࡓࠦࡰࡢࡴࡶࡩࠥ࡫ࡲࡳࡱࡵࠤࠧਫ")))
  except Exception as e:
    logger.debug(bstack111l1111l_opy_.format(e))
def bstack11ll1llll_opy_(hub_url):
  global CONFIG
  url = bstack11l1lll1_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤਬ")+  hub_url + bstack11l1lll1_opy_ (u"ࠣ࠱ࡦ࡬ࡪࡩ࡫ࠣਭ")
  headers = {
        bstack11l1lll1_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨਮ"): bstack11l1lll1_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ਯ"),
      }
  proxies = bstack11ll1l1l1_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack11l1l1l11_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack1l1ll1ll1_opy_.format(hub_url, e))
def bstack11ll1lll_opy_():
  try:
    global bstack1lllll111_opy_
    bstack1l111ll_opy_ = bstack1lll1l1_opy_()
    bstack1111l1ll_opy_ = []
    results = []
    for bstack11ll1l111_opy_ in bstack1l111ll_opy_:
      bstack1111l1ll_opy_.append(bstack1l1llllll_opy_(target=bstack11ll1llll_opy_,args=(bstack11ll1l111_opy_,)))
    for t in bstack1111l1ll_opy_:
      t.start()
    for t in bstack1111l1ll_opy_:
      results.append(t.join())
    bstack11111ll_opy_ = {}
    for item in results:
      hub_url = item[bstack11l1lll1_opy_ (u"ࠫ࡭ࡻࡢࡠࡷࡵࡰࠬਰ")]
      latency = item[bstack11l1lll1_opy_ (u"ࠬࡲࡡࡵࡧࡱࡧࡾ࠭਱")]
      bstack11111ll_opy_[hub_url] = latency
    bstack11lll1111_opy_ = min(bstack11111ll_opy_, key= lambda x: bstack11111ll_opy_[x])
    bstack1lllll111_opy_ = bstack11lll1111_opy_
    logger.debug(bstack1l11ll1ll_opy_.format(bstack11lll1111_opy_))
  except Exception as e:
    logger.debug(bstack11l111l1_opy_.format(e))
bstack1lll1ll11_opy_ = bstack11l1lll1_opy_ (u"࠭ࡓࡦࡶࡷ࡭ࡳ࡭ࠠࡶࡲࠣࡪࡴࡸࠠࡃࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠲ࠠࡶࡵ࡬ࡲ࡬ࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬࠼ࠣࡿࢂ࠭ਲ")
bstack1lll1lll_opy_ = bstack11l1lll1_opy_ (u"ࠧࡄࡱࡰࡴࡱ࡫ࡴࡦࡦࠣࡷࡪࡺࡵࡱࠣࠪਲ਼")
bstack11ll11ll1_opy_ = bstack11l1lll1_opy_ (u"ࠨࡒࡤࡶࡸ࡫ࡤࠡࡥࡲࡲ࡫࡯ࡧࠡࡨ࡬ࡰࡪࡀࠠࡼࡿࠪ਴")
bstack11ll1l_opy_ = bstack11l1lll1_opy_ (u"ࠩࡖࡥࡳ࡯ࡴࡪࡼࡨࡨࠥࡩ࡯࡯ࡨ࡬࡫ࠥ࡬ࡩ࡭ࡧ࠽ࠤࢀࢃࠧਵ")
bstack1111111l_opy_ = bstack11l1lll1_opy_ (u"࡙ࠪࡸ࡯࡮ࡨࠢ࡫ࡹࡧࠦࡵࡳ࡮࠽ࠤࢀࢃࠧਸ਼")
bstack1l111l111_opy_ = bstack11l1lll1_opy_ (u"ࠫࡘ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡴࡷࡩࡩࠦࡷࡪࡶ࡫ࠤ࡮ࡪ࠺ࠡࡽࢀࠫ਷")
bstack1l11lll1l_opy_ = bstack11l1lll1_opy_ (u"ࠬࡘࡥࡤࡧ࡬ࡺࡪࡪࠠࡪࡰࡷࡩࡷࡸࡵࡱࡶ࠯ࠤࡪࡾࡩࡵ࡫ࡱ࡫ࠬਸ")
bstack111l1l111_opy_ = bstack11l1lll1_opy_ (u"࠭ࡐ࡭ࡧࡤࡷࡪࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠢࡷࡳࠥࡸࡵ࡯ࠢࡷࡩࡸࡺࡳ࠯ࠢࡣࡴ࡮ࡶࠠࡪࡰࡶࡸࡦࡲ࡬ࠡࡵࡨࡰࡪࡴࡩࡶ࡯ࡣࠫਹ")
bstack1l111ll1_opy_ = bstack11l1lll1_opy_ (u"ࠧࡑ࡮ࡨࡥࡸ࡫ࠠࡪࡰࡶࡸࡦࡲ࡬ࠡࡲࡼࡸࡪࡹࡴࠡࡣࡱࡨࠥࡶࡹࡵࡧࡶࡸ࠲ࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠠࡱࡣࡦ࡯ࡦ࡭ࡥࡴ࠰ࠣࡤࡵ࡯ࡰࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡶࡩࡱ࡫࡮ࡪࡷࡰࡤࠬ਺")
bstack1lll1_opy_ = bstack11l1lll1_opy_ (u"ࠨࡒ࡯ࡩࡦࡹࡥࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡄࡴࡵ࡯ࡵ࡮ࡎ࡬ࡦࡷࡧࡲࡺࠢࡳࡥࡨࡱࡡࡨࡧ࠱ࠤࡥࡶࡩࡱࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡶࡴࡨ࡯ࡵࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮࠱ࡦࡶࡰࡪࡷࡰࡰ࡮ࡨࡲࡢࡴࡼࡤࠬ਻")
bstack11l111lll_opy_ = bstack11l1lll1_opy_ (u"ࠩࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡶࡴࡨ࡯ࡵ࠮ࠣࡴࡦࡨ࡯ࡵࠢࡤࡲࡩࠦࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࡭࡫ࡥࡶࡦࡸࡹࠡࡲࡤࡧࡰࡧࡧࡦࡵࠣࡸࡴࠦࡲࡶࡰࠣࡶࡴࡨ࡯ࡵࠢࡷࡩࡸࡺࡳࠡ࡫ࡱࠤࡵࡧࡲࡢ࡮࡯ࡩࡱ࠴ࠠࡡࡲ࡬ࡴࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡲࡰࡤࡲࡸ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠠࡳࡱࡥࡳࡹ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠮ࡲࡤࡦࡴࡺࠠࡳࡱࡥࡳࡹ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠮ࡵࡨࡰࡪࡴࡩࡶ࡯࡯࡭ࡧࡸࡡࡳࡻࡣ਼ࠫ")
bstack111lll11_opy_ = bstack11l1lll1_opy_ (u"ࠪࡔࡱ࡫ࡡࡴࡧࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡧ࡫ࡨࡢࡸࡨࠤࡹࡵࠠࡳࡷࡱࠤࡹ࡫ࡳࡵࡵ࠱ࠤࡥࡶࡩࡱࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡦࡪ࡮ࡡࡷࡧࡣࠫ਽")
bstack1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠫࡕࡲࡥࡢࡵࡨࠤ࡮ࡴࡳࡵࡣ࡯ࡰࠥࡧࡰࡱ࡫ࡸࡱ࠲ࡩ࡬ࡪࡧࡱࡸࠥࡺ࡯ࠡࡴࡸࡲࠥࡺࡥࡴࡶࡶ࠲ࠥࡦࡰࡪࡲࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡆࡶࡰࡪࡷࡰ࠱ࡕࡿࡴࡩࡱࡱ࠱ࡈࡲࡩࡦࡰࡷࡤࠬਾ")
bstack111ll11ll_opy_ = bstack11l1lll1_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡸࡴࠦࡲࡶࡰࠣࡸࡪࡹࡴࡴ࠰ࠣࡤࡵ࡯ࡰࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡦࠧਿ")
bstack1l11l11_opy_ = bstack11l1lll1_opy_ (u"࠭ࡃࡰࡷ࡯ࡨࠥࡴ࡯ࡵࠢࡩ࡭ࡳࡪࠠࡦ࡫ࡷ࡬ࡪࡸࠠࡔࡧ࡯ࡩࡳ࡯ࡵ࡮ࠢࡲࡶࠥࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡷࡳࠥࡸࡵ࡯ࠢࡷࡩࡸࡺࡳ࠯ࠢࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡹࡧ࡬࡭ࠢࡷ࡬ࡪࠦࡲࡦ࡮ࡨࡺࡦࡴࡴࠡࡲࡤࡧࡰࡧࡧࡦࡵࠣࡹࡸ࡯࡮ࡨࠢࡳ࡭ࡵࠦࡴࡰࠢࡵࡹࡳࠦࡴࡦࡵࡷࡷ࠳࠭ੀ")
bstack11l1_opy_ = bstack11l1lll1_opy_ (u"ࠧࡉࡣࡱࡨࡱ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡧࡱࡵࡳࡦࠩੁ")
bstack1lll11l1l_opy_ = bstack11l1lll1_opy_ (u"ࠨࡃ࡯ࡰࠥࡪ࡯࡯ࡧࠤࠫੂ")
bstack1l1lllll1_opy_ = bstack11l1lll1_opy_ (u"ࠩࡆࡳࡳ࡬ࡩࡨࠢࡩ࡭ࡱ࡫ࠠࡥࡱࡨࡷࠥࡴ࡯ࡵࠢࡨࡼ࡮ࡹࡴࠡࡣࡷࠤࡦࡴࡹࠡࡲࡤࡶࡪࡴࡴࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡴ࡬ࠠࠣࡽࢀࠦ࠳ࠦࡐ࡭ࡧࡤࡷࡪࠦࡩ࡯ࡥ࡯ࡹࡩ࡫ࠠࡢࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡻࡰࡰ࠴ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡧ࡭࡭ࠢࡩ࡭ࡱ࡫ࠠࡤࡱࡱࡸࡦ࡯࡮ࡪࡰࡪࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࡫ࡵࡲࠡࡶࡨࡷࡹࡹ࠮ࠨ੃")
bstack11l1lll_opy_ = bstack11l1lll1_opy_ (u"ࠪࡆࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡦࡶࡪࡪࡥ࡯ࡶ࡬ࡥࡱࡹࠠ࡯ࡱࡷࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡩ࠴ࠠࡑ࡮ࡨࡥࡸ࡫ࠠࡢࡦࡧࠤࡹ࡮ࡥ࡮ࠢ࡬ࡲࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠡࡥࡲࡲ࡫࡯ࡧࠡࡨ࡬ࡰࡪࠦࡡࡴࠢࠥࡹࡸ࡫ࡲࡏࡣࡰࡩࠧࠦࡡ࡯ࡦࠣࠦࡦࡩࡣࡦࡵࡶࡏࡪࡿࠢࠡࡱࡵࠤࡸ࡫ࡴࠡࡶ࡫ࡩࡲࠦࡡࡴࠢࡨࡲࡻ࡯ࡲࡰࡰࡰࡩࡳࡺࠠࡷࡣࡵ࡭ࡦࡨ࡬ࡦࡵ࠽ࠤࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡐࡄࡑࡊࠨࠠࡢࡰࡧࠤࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆࡉࡃࡆࡕࡖࡣࡐࡋ࡙ࠣࠩ੄")
bstack111ll1l1_opy_ = bstack11l1lll1_opy_ (u"ࠫࡒࡧ࡬ࡧࡱࡵࡱࡪࡪࠠࡤࡱࡱࡪ࡮࡭ࠠࡧ࡫࡯ࡩ࠿ࠨࡻࡾࠤࠪ੅")
bstack1l11ll1_opy_ = bstack11l1lll1_opy_ (u"ࠬࡋ࡮ࡤࡱࡸࡲࡹ࡫ࡲࡦࡦࠣࡩࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡸࡴࠥ࠳ࠠࡼࡿࠪ੆")
bstack1111ll11l_opy_ = bstack11l1lll1_opy_ (u"࠭ࡓࡵࡣࡵࡸ࡮ࡴࡧࠡࡄࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡍࡱࡦࡥࡱ࠭ੇ")
bstack1l11l11l_opy_ = bstack11l1lll1_opy_ (u"ࠧࡔࡶࡲࡴࡵ࡯࡮ࡨࠢࡅࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡎࡲࡧࡦࡲࠧੈ")
bstack1llll1lll_opy_ = bstack11l1lll1_opy_ (u"ࠨࡄࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡍࡱࡦࡥࡱࠦࡩࡴࠢࡱࡳࡼࠦࡲࡶࡰࡱ࡭ࡳ࡭ࠡࠨ੉")
bstack111l11lll_opy_ = bstack11l1lll1_opy_ (u"ࠩࡆࡳࡺࡲࡤࠡࡰࡲࡸࠥࡹࡴࡢࡴࡷࠤࡇࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡐࡴࡩࡡ࡭࠼ࠣࡿࢂ࠭੊")
bstack1ll11l1_opy_ = bstack11l1lll1_opy_ (u"ࠪࡗࡹࡧࡲࡵ࡫ࡱ࡫ࠥࡲ࡯ࡤࡣ࡯ࠤࡧ࡯࡮ࡢࡴࡼࠤࡼ࡯ࡴࡩࠢࡲࡴࡹ࡯࡯࡯ࡵ࠽ࠤࢀࢃࠧੋ")
bstack111ll1ll_opy_ = bstack11l1lll1_opy_ (u"࡚ࠫࡶࡤࡢࡶ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡥࡧࡷࡥ࡮ࡲࡳ࠻ࠢࡾࢁࠬੌ")
bstack1lllllll1_opy_ = bstack11l1lll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡷࡳࡨࡦࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡵࡷࡥࡹࡻࡳࠡࡽࢀ੍ࠫ")
bstack1lll1l1ll_opy_ = bstack11l1lll1_opy_ (u"࠭ࡐ࡭ࡧࡤࡷࡪࠦࡰࡳࡱࡹ࡭ࡩ࡫ࠠࡢࡰࠣࡥࡵࡶࡲࡰࡲࡵ࡭ࡦࡺࡥࠡࡈ࡚ࠤ࠭ࡸ࡯ࡣࡱࡷ࠳ࡵࡧࡢࡰࡶࠬࠤ࡮ࡴࠠࡤࡱࡱࡪ࡮࡭ࠠࡧ࡫࡯ࡩ࠱ࠦࡳ࡬࡫ࡳࠤࡹ࡮ࡥࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠤࡰ࡫ࡹࠡ࡫ࡱࠤࡨࡵ࡮ࡧ࡫ࡪࠤ࡮࡬ࠠࡳࡷࡱࡲ࡮ࡴࡧࠡࡵ࡬ࡱࡵࡲࡥࠡࡲࡼࡸ࡭ࡵ࡮ࠡࡵࡦࡶ࡮ࡶࡴࠡࡹ࡬ࡸ࡭ࡵࡵࡵࠢࡤࡲࡾࠦࡆࡘ࠰ࠪ੎")
bstack1l111lll1_opy_ = bstack11l1lll1_opy_ (u"ࠧࡔࡧࡷࡸ࡮ࡴࡧࠡࡪࡷࡸࡵࡖࡲࡰࡺࡼ࠳࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠡ࡫ࡶࠤࡳࡵࡴࠡࡵࡸࡴࡵࡵࡲࡵࡧࡧࠤࡴࡴࠠࡤࡷࡵࡶࡪࡴࡴ࡭ࡻࠣ࡭ࡳࡹࡴࡢ࡮࡯ࡩࡩࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡰࡨࠣࡷࡪࡲࡥ࡯࡫ࡸࡱࠥ࠮ࡻࡾࠫ࠯ࠤࡵࡲࡥࡢࡵࡨࠤࡺࡶࡧࡳࡣࡧࡩࠥࡺ࡯ࠡࡕࡨࡰࡪࡴࡩࡶ࡯ࡁࡁ࠹࠴࠰࠯࠲ࠣࡳࡷࠦࡲࡦࡨࡨࡶࠥࡺ࡯ࠡࡪࡷࡸࡵࡹ࠺࠰࠱ࡺࡻࡼ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡧࡳࡨࡹ࠯ࡢࡷࡷࡳࡲࡧࡴࡦ࠱ࡶࡩࡱ࡫࡮ࡪࡷࡰ࠳ࡷࡻ࡮࠮ࡶࡨࡷࡹࡹ࠭ࡣࡧ࡫࡭ࡳࡪ࠭ࡱࡴࡲࡼࡾࠩࡰࡺࡶ࡫ࡳࡳࠦࡦࡰࡴࠣࡥࠥࡽ࡯ࡳ࡭ࡤࡶࡴࡻ࡮ࡥ࠰ࠪ੏")
bstack1lllll11l_opy_ = bstack11l1lll1_opy_ (u"ࠨࡉࡨࡲࡪࡸࡡࡵ࡫ࡱ࡫ࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤࡾࡳ࡬ࠡࡨ࡬ࡰࡪ࠴࠮ࠨ੐")
bstack1ll1ll11_opy_ = bstack11l1lll1_opy_ (u"ࠩࡖࡹࡨࡩࡥࡴࡵࡩࡹࡱࡲࡹࠡࡩࡨࡲࡪࡸࡡࡵࡧࡧࠤࡹ࡮ࡥࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠡࡨ࡬ࡰࡪࠧࠧੑ")
bstack1l11l1l11_opy_ = bstack11l1lll1_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡧࡦࡰࡨࡶࡦࡺࡥࠡࡶ࡫ࡩࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࡫࡯࡬ࡦ࠰ࠣࡿࢂ࠭੒")
bstack1ll111lll_opy_ = bstack11l1lll1_opy_ (u"ࠫࡊࡾࡰࡦࡥࡷࡩࡩࠦࡡࡵࠢ࡯ࡩࡦࡹࡴࠡ࠳ࠣ࡭ࡳࡶࡵࡵ࠮ࠣࡶࡪࡩࡥࡪࡸࡨࡨࠥ࠶ࠧ੓")
bstack1l11ll1l_opy_ = bstack11l1lll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤࡩࡻࡲࡪࡰࡪࠤࡆࡶࡰࠡࡷࡳࡰࡴࡧࡤ࠯ࠢࡾࢁࠬ੔")
bstack1111llll_opy_ = bstack11l1lll1_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡸࡴࡱࡵࡡࡥࠢࡄࡴࡵ࠴ࠠࡊࡰࡹࡥࡱ࡯ࡤࠡࡨ࡬ࡰࡪࠦࡰࡢࡶ࡫ࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡩࠦࡻࡾ࠰ࠪ੕")
bstack11l1ll1l1_opy_ = bstack11l1lll1_opy_ (u"ࠧࡌࡧࡼࡷࠥࡩࡡ࡯ࡰࡲࡸࠥࡩ࡯࠮ࡧࡻ࡭ࡸࡺࠠࡢࡵࠣࡥࡵࡶࠠࡷࡣ࡯ࡹࡪࡹࠬࠡࡷࡶࡩࠥࡧ࡮ࡺࠢࡲࡲࡪࠦࡰࡳࡱࡳࡩࡷࡺࡹࠡࡨࡵࡳࡲࠦࡻࡪࡦ࠿ࡷࡹࡸࡩ࡯ࡩࡁ࠰ࠥࡶࡡࡵࡪ࠿ࡷࡹࡸࡩ࡯ࡩࡁ࠰ࠥࡩࡵࡴࡶࡲࡱࡤ࡯ࡤ࠽ࡵࡷࡶ࡮ࡴࡧ࠿࠮ࠣࡷ࡭ࡧࡲࡦࡣࡥࡰࡪࡥࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀࢀ࠰ࠥࡵ࡮࡭ࡻࠣࠦࡵࡧࡴࡩࠤࠣࡥࡳࡪࠠࠣࡥࡸࡷࡹࡵ࡭ࡠ࡫ࡧࠦࠥࡩࡡ࡯ࠢࡦࡳ࠲࡫ࡸࡪࡵࡷࠤࡹࡵࡧࡦࡶ࡫ࡩࡷ࠴ࠧ੖")
bstack1lll111l_opy_ = bstack11l1lll1_opy_ (u"ࠨ࡝ࡌࡲࡻࡧ࡬ࡪࡦࠣࡥࡵࡶࠠࡱࡴࡲࡴࡪࡸࡴࡺ࡟ࠣࡷࡺࡶࡰࡰࡴࡷࡩࡩࠦࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠣࡥࡷ࡫ࠠࡼ࡫ࡧࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡰࡢࡶ࡫ࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡣࡶࡵࡷࡳࡲࡥࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀ࠯ࠤࡸ࡮ࡡࡳࡧࡤࡦࡱ࡫࡟ࡪࡦ࠿ࡷࡹࡸࡩ࡯ࡩࡁࢁ࠳ࠦࡆࡰࡴࠣࡱࡴࡸࡥࠡࡦࡨࡸࡦ࡯࡬ࡴࠢࡳࡰࡪࡧࡳࡦࠢࡹ࡭ࡸ࡯ࡴࠡࡪࡷࡸࡵࡹ࠺࠰࠱ࡺࡻࡼ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡧࡳࡨࡹ࠯ࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠵ࡡࡱࡲ࡬ࡹࡲ࠵ࡳࡦࡶ࠰ࡹࡵ࠳ࡴࡦࡵࡷࡷ࠴ࡹࡰࡦࡥ࡬ࡪࡾ࠳ࡡࡱࡲࠪ੗")
bstack1l1ll1ll_opy_ = bstack11l1lll1_opy_ (u"ࠩ࡞ࡍࡳࡼࡡ࡭࡫ࡧࠤࡦࡶࡰࠡࡲࡵࡳࡵ࡫ࡲࡵࡻࡠࠤࡘࡻࡰࡱࡱࡵࡸࡪࡪࠠࡷࡣ࡯ࡹࡪࡹࠠࡰࡨࠣࡥࡵࡶࠠࡢࡴࡨࠤࡴ࡬ࠠࡼ࡫ࡧࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡰࡢࡶ࡫ࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡣࡶࡵࡷࡳࡲࡥࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀ࠯ࠤࡸ࡮ࡡࡳࡧࡤࡦࡱ࡫࡟ࡪࡦ࠿ࡷࡹࡸࡩ࡯ࡩࡁࢁ࠳ࠦࡆࡰࡴࠣࡱࡴࡸࡥࠡࡦࡨࡸࡦ࡯࡬ࡴࠢࡳࡰࡪࡧࡳࡦࠢࡹ࡭ࡸ࡯ࡴࠡࡪࡷࡸࡵࡹ࠺࠰࠱ࡺࡻࡼ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡧࡳࡨࡹ࠯ࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠵ࡡࡱࡲ࡬ࡹࡲ࠵ࡳࡦࡶ࠰ࡹࡵ࠳ࡴࡦࡵࡷࡷ࠴ࡹࡰࡦࡥ࡬ࡪࡾ࠳ࡡࡱࡲࠪ੘")
bstack1ll1l11_opy_ = bstack11l1lll1_opy_ (u"࡙ࠪࡸ࡯࡮ࡨࠢࡨࡼ࡮ࡹࡴࡪࡰࡪࠤࡦࡶࡰࠡ࡫ࡧࠤࢀࢃࠠࡧࡱࡵࠤ࡭ࡧࡳࡩࠢ࠽ࠤࢀࢃ࠮ࠨਖ਼")
bstack11l11lll1_opy_ = bstack11l1lll1_opy_ (u"ࠫࡆࡶࡰࠡࡗࡳࡰࡴࡧࡤࡦࡦࠣࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲ࡬ࡺ࠰ࠣࡍࡉࠦ࠺ࠡࡽࢀࠫਗ਼")
bstack11lllllll_opy_ = bstack11l1lll1_opy_ (u"࡛ࠬࡳࡪࡰࡪࠤࡆࡶࡰࠡ࠼ࠣࡿࢂ࠴ࠧਜ਼")
bstack111l1lll_opy_ = bstack11l1lll1_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲࠦࡩࡴࠢࡱࡳࡹࠦࡳࡶࡲࡳࡳࡷࡺࡥࡥࠢࡩࡳࡷࠦࡶࡢࡰ࡬ࡰࡱࡧࠠࡱࡻࡷ࡬ࡴࡴࠠࡵࡧࡶࡸࡸ࠲ࠠࡳࡷࡱࡲ࡮ࡴࡧࠡࡹ࡬ࡸ࡭ࠦࡰࡢࡴࡤࡰࡱ࡫࡬ࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠥࡃࠠ࠲ࠩੜ")
bstack1lll1111l_opy_ = bstack11l1lll1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡦࡶࡪࡧࡴࡪࡰࡪࠤࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷࡀࠠࡼࡿࠪ੝")
bstack11l1lll1l_opy_ = bstack11l1lll1_opy_ (u"ࠨࡅࡲࡹࡱࡪࠠ࡯ࡱࡷࠤࡨࡲ࡯ࡴࡧࠣࡦࡷࡵࡷࡴࡧࡵ࠾ࠥࢁࡽࠨਫ਼")
bstack1lllll1l_opy_ = bstack11l1lll1_opy_ (u"ࠩࡆࡳࡺࡲࡤࠡࡰࡲࡸࠥ࡭ࡥࡵࠢࡵࡩࡦࡹ࡯࡯ࠢࡩࡳࡷࠦࡢࡦࡪࡤࡺࡪࠦࡦࡦࡣࡷࡹࡷ࡫ࠠࡧࡣ࡬ࡰࡺࡸࡥ࠯ࠢࡾࢁࠬ੟")
bstack1111l11_opy_ = bstack11l1lll1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡵࡩࡸࡶ࡯࡯ࡵࡨࠤ࡫ࡸ࡯࡮ࠢࡤࡴ࡮ࠦࡣࡢ࡮࡯࠲ࠥࡋࡲࡳࡱࡵ࠾ࠥࢁࡽࠨ੠")
bstack1l11lllll_opy_ = bstack11l1lll1_opy_ (u"࡚ࠫࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡪࡲࡻࠥࡨࡵࡪ࡮ࡧࠤ࡚ࡘࡌ࠭ࠢࡤࡷࠥࡨࡵࡪ࡮ࡧࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠡ࡫ࡶࠤࡳࡵࡴࠡࡷࡶࡩࡩ࠴ࠧ੡")
bstack1ll1l1l_opy_ = bstack11l1lll1_opy_ (u"࡙ࠬࡥࡳࡸࡨࡶࠥࡹࡩࡥࡧࠣࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠮ࡻࡾࠫࠣ࡭ࡸࠦ࡮ࡰࡶࠣࡷࡦࡳࡥࠡࡣࡶࠤࡨࡲࡩࡦࡰࡷࠤࡸ࡯ࡤࡦࠢࡥࡹ࡮ࡲࡤࡏࡣࡰࡩ࠭ࢁࡽࠪࠩ੢")
bstack1111l_opy_ = bstack11l1lll1_opy_ (u"࠭ࡖࡪࡧࡺࠤࡧࡻࡩ࡭ࡦࠣࡳࡳࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡪࡡࡴࡪࡥࡳࡦࡸࡤ࠻ࠢࡾࢁࠬ੣")
bstack1l1lllll_opy_ = bstack11l1lll1_opy_ (u"ࠧࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡥࡨࡩࡥࡴࡵࠣࡥࠥࡶࡲࡪࡸࡤࡸࡪࠦࡤࡰ࡯ࡤ࡭ࡳࡀࠠࡼࡿࠣ࠲࡙ࠥࡥࡵࠢࡷ࡬ࡪࠦࡦࡰ࡮࡯ࡳࡼ࡯࡮ࡨࠢࡦࡳࡳ࡬ࡩࡨࠢ࡬ࡲࠥࡿ࡯ࡶࡴࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡼࡱࡱࠦࡦࡪ࡮ࡨ࠾ࠥࡢ࡮࠮࠯࠰࠱࠲࠳࠭࠮࠯࠰࠱ࠥࡢ࡮ࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰ࠿ࠦࡴࡳࡷࡨࠤࡡࡴ࠭࠮࠯࠰࠱࠲࠳࠭࠮࠯࠰ࠫ੤")
bstack1l1ll1l11_opy_ = bstack11l1lll1_opy_ (u"ࠨࡕࡲࡱࡪࡺࡨࡪࡰࡪࠤࡼ࡫࡮ࡵࠢࡺࡶࡴࡴࡧࠡࡹ࡫࡭ࡱ࡫ࠠࡦࡺࡨࡧࡺࡺࡩ࡯ࡩࠣ࡫ࡪࡺ࡟࡯ࡷࡧ࡫ࡪࡥ࡬ࡰࡥࡤࡰࡤ࡫ࡲࡳࡱࡵࠤ࠿ࠦࡻࡾࠩ੥")
bstack1ll11ll11_opy_ = bstack11l1lll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫࡮ࡥࡡࡤࡱࡵࡲࡩࡵࡷࡧࡩࡤ࡫ࡶࡦࡰࡷࠤ࡫ࡵࡲࠡࡕࡇࡏࡘ࡫ࡴࡶࡲࠣࡿࢂࠨ੦")
bstack111lll1l_opy_ = bstack11l1lll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥ࡯ࡦࡢࡥࡲࡶ࡬ࡪࡶࡸࡨࡪࡥࡥࡷࡧࡱࡸࠥ࡬࡯ࡳࠢࡖࡈࡐ࡚ࡥࡴࡶࡄࡸࡹ࡫࡭ࡱࡶࡨࡨࠥࢁࡽࠣ੧")
bstack1l1111l1l_opy_ = bstack11l1lll1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡳࡦࡰࡧࡣࡦࡳࡰ࡭࡫ࡷࡹࡩ࡫࡟ࡦࡸࡨࡲࡹࠦࡦࡰࡴࠣࡗࡉࡑࡔࡦࡵࡷࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲࠠࡼࡿࠥ੨")
bstack1ll111ll1_opy_ = bstack11l1lll1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧ࡫ࡵࡩࡤࡸࡥࡲࡷࡨࡷࡹࠦࡻࡾࠤ੩")
bstack1llll11l_opy_ = bstack11l1lll1_opy_ (u"ࠨࡐࡐࡕࡗࠤࡊࡼࡥ࡯ࡶࠣࡿࢂࠦࡲࡦࡵࡳࡳࡳࡹࡥࠡ࠼ࠣࡿࢂࠨ੪")
bstack111lll11l_opy_ = bstack11l1lll1_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡧࡴࡴࡦࡪࡩࡸࡶࡪࠦࡰࡳࡱࡻࡽࠥࡹࡥࡵࡶ࡬ࡲ࡬ࡹࠬࠡࡧࡵࡶࡴࡸ࠺ࠡࡽࢀࠫ੫")
bstack1l1lll1_opy_ = bstack11l1lll1_opy_ (u"ࠨࡔࡨࡷࡵࡵ࡮ࡴࡧࠣࡪࡷࡵ࡭ࠡ࠱ࡱࡩࡽࡺ࡟ࡩࡷࡥࡷࠥࢁࡽࠨ੬")
bstack111l1111l_opy_ = bstack11l1lll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠠࡧࡴࡲࡱࠥ࠵࡮ࡦࡺࡷࡣ࡭ࡻࡢࡴ࠼ࠣࡿࢂ࠭੭")
bstack1l11ll1ll_opy_ = bstack11l1lll1_opy_ (u"ࠪࡒࡪࡧࡲࡦࡵࡷࠤ࡭ࡻࡢࠡࡣ࡯ࡰࡴࡩࡡࡵࡧࡧࠤ࡮ࡹ࠺ࠡࡽࢀࠫ੮")
bstack11l111l1_opy_ = bstack11l1lll1_opy_ (u"ࠫࡊࡘࡒࡐࡔࠣࡍࡓࠦࡁࡍࡎࡒࡇࡆ࡚ࡅࠡࡊࡘࡆࠥࢁࡽࠨ੯")
bstack11l1l1l11_opy_ = bstack11l1lll1_opy_ (u"ࠬࡒࡡࡵࡧࡱࡧࡾࠦ࡯ࡧࠢ࡫ࡹࡧࡀࠠࡼࡿࠣ࡭ࡸࡀࠠࡼࡿࠪੰ")
bstack1l1ll1ll1_opy_ = bstack11l1lll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡩࡨࡸࡹ࡯࡮ࡨࠢ࡯ࡥࡹ࡫࡮ࡤࡻࠣࡪࡴࡸࠠࡼࡿࠣ࡬ࡺࡨ࠺ࠡࡽࢀࠫੱ")
bstack1l1111lll_opy_ = bstack11l1lll1_opy_ (u"ࠧࡉࡷࡥࠤࡺࡸ࡬ࠡࡥ࡫ࡥࡳ࡭ࡥࡥࠢࡷࡳࠥࡺࡨࡦࠢࡲࡴࡹ࡯࡭ࡢ࡮ࠣ࡬ࡺࡨ࠺ࠡࡽࢀࠫੲ")
bstack11l1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡳࡦࡶࡷ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡴࡶࡴࡪ࡯ࡤࡰࠥ࡮ࡵࡣࠢࡸࡶࡱࡀࠠࡼࡿࠪੳ")
bstack11l1lll11_opy_ = bstack11l1lll1_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡭ࡥࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡰ࡮ࡹࡴࡴ࠼ࠣࡿࢂ࠭ੴ")
bstack11lll_opy_ = bstack11l1lll1_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡧࡦࡰࡨࡶࡦࡺࡥࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡣࡷ࡬ࡰࡩࠦࡡࡳࡶ࡬ࡪࡦࡩࡴࡴ࠼ࠣࡿࢂ࠭ੵ")
bstack11l11l111_opy_ = bstack11l1lll1_opy_ (u"࡚ࠫࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡱࡣࡵࡷࡪࠦࡰࡢࡥࠣࡪ࡮ࡲࡥࠡࡽࢀ࠲ࠥࡋࡲࡳࡱࡵࠤ࠲ࠦࡻࡾࠩ੶")
bstack1l1lll11_opy_ = bstack11l1lll1_opy_ (u"ࠬࠦࠠ࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱࡟ࡲࠥࠦࡩࡧࠪࡳࡥ࡬࡫ࠠ࠾࠿ࡀࠤࡻࡵࡩࡥࠢ࠳࠭ࠥࢁ࡜࡯ࠢࠣࠤࡹࡸࡹࡼ࡞ࡱࠤࡨࡵ࡮ࡴࡶࠣࡪࡸࠦ࠽ࠡࡴࡨࡵࡺ࡯ࡲࡦࠪ࡟ࠫ࡫ࡹ࡜ࠨࠫ࠾ࡠࡳࠦࠠࠡࠢࠣࡪࡸ࠴ࡡࡱࡲࡨࡲࡩࡌࡩ࡭ࡧࡖࡽࡳࡩࠨࡣࡵࡷࡥࡨࡱ࡟ࡱࡣࡷ࡬࠱ࠦࡊࡔࡑࡑ࠲ࡸࡺࡲࡪࡰࡪ࡭࡫ࡿࠨࡱࡡ࡬ࡲࡩ࡫ࡸࠪࠢ࠮ࠤࠧࡀࠢࠡ࠭ࠣࡎࡘࡕࡎ࠯ࡵࡷࡶ࡮ࡴࡧࡪࡨࡼࠬࡏ࡙ࡏࡏ࠰ࡳࡥࡷࡹࡥࠩࠪࡤࡻࡦ࡯ࡴࠡࡰࡨࡻࡕࡧࡧࡦ࠴࠱ࡩࡻࡧ࡬ࡶࡣࡷࡩ࠭ࠨࠨࠪࠢࡀࡂࠥࢁࡽࠣ࠮ࠣࡠࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧ࡭ࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡆࡨࡸࡦ࡯࡬ࡴࠤࢀࡠࠬ࠯ࠩࠪ࡝ࠥ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩࠨ࡝ࠪࠢ࠮ࠤࠧ࠲࡜࡝ࡰࠥ࠭ࡡࡴࠠࠡࠢࠣࢁࡨࡧࡴࡤࡪࠫࡩࡽ࠯ࡻ࡝ࡰࠣࠤࠥࠦࡽ࡝ࡰࠣࠤࢂࡢ࡮ࠡࠢ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࠬ੷")
bstack1l11l11l1_opy_ = bstack11l1lll1_opy_ (u"࠭࡜࡯࠱࠭ࠤࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽ࠡࠬ࠲ࡠࡳࡩ࡯࡯ࡵࡷࠤࡧࡹࡴࡢࡥ࡮ࡣࡵࡧࡴࡩࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࡞ࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠸ࡣ࡜࡯ࡥࡲࡲࡸࡺࠠࡣࡵࡷࡥࡨࡱ࡟ࡤࡣࡳࡷࠥࡃࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻࡡࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡲࡥ࡯ࡩࡷ࡬ࠥ࠳ࠠ࠲࡟࡟ࡲࡨࡵ࡮ࡴࡶࠣࡴࡤ࡯࡮ࡥࡧࡻࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺࡠࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠲࡞࡞ࡱࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡷࡱ࡯ࡣࡦࠪ࠳࠰ࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠳ࠪ࡞ࡱࡧࡴࡴࡳࡵࠢ࡬ࡱࡵࡵࡲࡵࡡࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠺࡟ࡣࡵࡷࡥࡨࡱࠠ࠾ࠢࡵࡩࡶࡻࡩࡳࡧࠫࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣࠫ࠾ࡠࡳ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡲࡡࡶࡰࡦ࡬ࠥࡃࠠࡢࡵࡼࡲࡨࠦࠨ࡭ࡣࡸࡲࡨ࡮ࡏࡱࡶ࡬ࡳࡳࡹࠩࠡ࠿ࡁࠤࢀࡢ࡮࡭ࡧࡷࠤࡨࡧࡰࡴ࠽࡟ࡲࡹࡸࡹࠡࡽ࡟ࡲࡨࡧࡰࡴࠢࡀࠤࡏ࡙ࡏࡏ࠰ࡳࡥࡷࡹࡥࠩࡤࡶࡸࡦࡩ࡫ࡠࡥࡤࡴࡸ࠯࡜࡯ࠢࠣࢁࠥࡩࡡࡵࡥ࡫ࠬࡪࡾࠩࠡࡽ࡟ࡲࠥࠦࠠࠡࡿ࡟ࡲࠥࠦࡲࡦࡶࡸࡶࡳࠦࡡࡸࡣ࡬ࡸࠥ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡩ࡯࡯ࡰࡨࡧࡹ࠮ࡻ࡝ࡰࠣࠤࠥࠦࡷࡴࡇࡱࡨࡵࡵࡩ࡯ࡶ࠽ࠤࡥࡽࡳࡴ࠼࠲࠳ࡨࡪࡰ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡀࡥࡤࡴࡸࡃࠤࡼࡧࡱࡧࡴࡪࡥࡖࡔࡌࡇࡴࡳࡰࡰࡰࡨࡲࡹ࠮ࡊࡔࡑࡑ࠲ࡸࡺࡲࡪࡰࡪ࡭࡫ࡿࠨࡤࡣࡳࡷ࠮࠯ࡽࡡ࠮࡟ࡲࠥࠦࠠࠡ࠰࠱࠲ࡱࡧࡵ࡯ࡥ࡫ࡓࡵࡺࡩࡰࡰࡶࡠࡳࠦࠠࡾࠫ࡟ࡲࢂࡢ࡮࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱࡟ࡲࠬ੸")
from ._version import __version__
bstack1lll11ll_opy_ = None
CONFIG = {}
bstack1l1l1ll1_opy_ = {}
bstack11l1l1111_opy_ = {}
bstack1ll11ll1_opy_ = None
bstack11l11lll_opy_ = None
bstack1l1lll1ll_opy_ = None
bstack11llll1l_opy_ = -1
bstack11l1l1l1_opy_ = bstack1ll11ll_opy_
bstack1111lll1_opy_ = 1
bstack11l1l11ll_opy_ = False
bstack1l1l1ll_opy_ = False
bstack1l11l1lll_opy_ = bstack11l1lll1_opy_ (u"ࠧࠨ੹")
bstack1l11_opy_ = bstack11l1lll1_opy_ (u"ࠨࠩ੺")
bstack111l1l11l_opy_ = False
bstack111ll111l_opy_ = True
bstack11l11l11_opy_ = bstack11l1lll1_opy_ (u"ࠩࠪ੻")
bstack11llll11l_opy_ = []
bstack1lllll111_opy_ = bstack11l1lll1_opy_ (u"ࠪࠫ੼")
bstack11ll1_opy_ = False
bstack11ll1lll1_opy_ = None
bstack1ll1l1l1_opy_ = None
bstack11lll111_opy_ = -1
bstack1ll1lll_opy_ = os.path.join(os.path.expanduser(bstack11l1lll1_opy_ (u"ࠫࢃ࠭੽")), bstack11l1lll1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ੾"), bstack11l1lll1_opy_ (u"࠭࠮ࡳࡱࡥࡳࡹ࠳ࡲࡦࡲࡲࡶࡹ࠳ࡨࡦ࡮ࡳࡩࡷ࠴ࡪࡴࡱࡱࠫ੿"))
bstack1l1ll1_opy_ = []
bstack1ll11l1ll_opy_ = False
bstack1llll11l1_opy_ = False
bstack1l1l1l11l_opy_ = None
bstack1lll_opy_ = None
bstack11_opy_ = None
bstack11ll1ll_opy_ = None
bstack1l1111l_opy_ = None
bstack1l111l_opy_ = None
bstack1ll111l_opy_ = None
bstack11l1l11l_opy_ = None
bstackl_opy_ = None
bstack11l111l11_opy_ = None
bstack11l1l_opy_ = None
bstack11llll1l1_opy_ = None
bstack11l1111ll_opy_ = None
bstack11l111ll_opy_ = None
bstack11l1111l_opy_ = None
bstack111lll1ll_opy_ = None
bstack111l11111_opy_ = None
bstack1111l1l1_opy_ = None
bstack1l1111l1_opy_ = bstack11l1lll1_opy_ (u"ࠢࠣ઀")
class bstack1l1llllll_opy_(threading.Thread):
  def run(self):
    self.exc = None
    try:
      self.ret = self._target(*self._args, **self._kwargs)
    except Exception as e:
      self.exc = e
  def join(self, timeout=None):
    super(bstack1l1llllll_opy_, self).join(timeout)
    if self.exc:
      raise self.exc
    return self.ret
logger = logging.getLogger(__name__)
logging.basicConfig(level=bstack11l1l1l1_opy_,
                    format=bstack11l1lll1_opy_ (u"ࠨ࡞ࡱࠩ࠭ࡧࡳࡤࡶ࡬ࡱࡪ࠯ࡳࠡ࡝ࠨࠬࡳࡧ࡭ࡦࠫࡶࡡࡠࠫࠨ࡭ࡧࡹࡩࡱࡴࡡ࡮ࡧࠬࡷࡢࠦ࠭ࠡࠧࠫࡱࡪࡹࡳࡢࡩࡨ࠭ࡸ࠭ઁ"),
                    datefmt=bstack11l1lll1_opy_ (u"ࠩࠨࡌ࠿ࠫࡍ࠻ࠧࡖࠫં"))
def bstack1l111ll11_opy_():
  global CONFIG
  global bstack11l1l1l1_opy_
  if bstack11l1lll1_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬઃ") in CONFIG:
    bstack11l1l1l1_opy_ = bstack1l111l1l_opy_[CONFIG[bstack11l1lll1_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭઄")]]
    logging.getLogger().setLevel(bstack11l1l1l1_opy_)
def bstack1l11111l1_opy_():
  global CONFIG
  global bstack1ll11l1ll_opy_
  bstack1ll1l1111_opy_ = bstack111ll1l1l_opy_(CONFIG)
  if(bstack11l1lll1_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧઅ") in bstack1ll1l1111_opy_ and str(bstack1ll1l1111_opy_[bstack11l1lll1_opy_ (u"࠭ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨઆ")]).lower() == bstack11l1lll1_opy_ (u"ࠧࡵࡴࡸࡩࠬઇ")):
    bstack1ll11l1ll_opy_ = True
def bstack1l1l111l_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack1111lllll_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack111111ll_opy_():
  args = sys.argv
  for i in range(len(args)):
    if bstack11l1lll1_opy_ (u"ࠣ࠯࠰ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡥࡲࡲ࡫࡯ࡧࡧ࡫࡯ࡩࠧઈ") == args[i].lower() or bstack11l1lll1_opy_ (u"ࠤ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡴࡦࡪࡩࠥઉ") == args[i].lower():
      path = args[i+1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      global bstack11l11l11_opy_
      bstack11l11l11_opy_ += bstack11l1lll1_opy_ (u"ࠪ࠱࠲ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡇࡴࡴࡦࡪࡩࡉ࡭ࡱ࡫ࠠࠨઊ") + path
      return path
  return None
bstack111l11l11_opy_ = re.compile(bstack11l1lll1_opy_ (u"ࡶࠧ࠴ࠪࡀ࡞ࠧࡿ࠭࠴ࠪࡀࠫࢀ࠲࠯ࡅࠢઋ"))
def bstack1ll1l1ll1_opy_(loader, node):
    value = loader.construct_scalar(node)
    for group in bstack111l11l11_opy_.findall(value):
        if group is not None and os.environ.get(group) is not None:
          value = value.replace(bstack11l1lll1_opy_ (u"ࠧࠪࡻࠣઌ") + group + bstack11l1lll1_opy_ (u"ࠨࡽࠣઍ"), os.environ.get(group))
    return value
def bstack11ll11_opy_():
  bstack1l1l1l1ll_opy_ = bstack111111ll_opy_()
  if bstack1l1l1l1ll_opy_ and os.path.exists(os.path.abspath(bstack1l1l1l1ll_opy_)):
    fileName = bstack1l1l1l1ll_opy_
  if bstack11l1lll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌࡥࡆࡊࡎࡈࠫ઎") in os.environ and os.path.exists(os.path.abspath(os.environ[bstack11l1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍ࡟ࡇࡋࡏࡉࠬએ")])) and not bstack11l1lll1_opy_ (u"ࠩࡩ࡭ࡱ࡫ࡎࡢ࡯ࡨࠫઐ") in locals():
    fileName = os.environ[bstack11l1lll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡓࡓࡌࡉࡈࡡࡉࡍࡑࡋࠧઑ")]
  if bstack11l1lll1_opy_ (u"ࠫ࡫࡯࡬ࡦࡐࡤࡱࡪ࠭઒") in locals():
    bstack1_opy_ = os.path.abspath(fileName)
  else:
    bstack1_opy_ = bstack11l1lll1_opy_ (u"ࠬ࠭ઓ")
  bstack11ll1l1_opy_ = os.getcwd()
  bstack1l11l_opy_ = bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩઔ")
  bstack1l1111l11_opy_ = bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹࡢ࡯࡯ࠫક")
  while (not os.path.exists(bstack1_opy_)) and bstack11ll1l1_opy_ != bstack11l1lll1_opy_ (u"ࠣࠤખ"):
    bstack1_opy_ = os.path.join(bstack11ll1l1_opy_, bstack1l11l_opy_)
    if not os.path.exists(bstack1_opy_):
      bstack1_opy_ = os.path.join(bstack11ll1l1_opy_, bstack1l1111l11_opy_)
    if bstack11ll1l1_opy_ != os.path.dirname(bstack11ll1l1_opy_):
      bstack11ll1l1_opy_ = os.path.dirname(bstack11ll1l1_opy_)
    else:
      bstack11ll1l1_opy_ = bstack11l1lll1_opy_ (u"ࠤࠥગ")
  if not os.path.exists(bstack1_opy_):
    bstack1lll1l1l_opy_(
      bstack1l1lllll1_opy_.format(os.getcwd()))
  try:
    with open(bstack1_opy_, bstack11l1lll1_opy_ (u"ࠪࡶࠬઘ")) as stream:
        yaml.add_implicit_resolver(bstack11l1lll1_opy_ (u"ࠦࠦࡶࡡࡵࡪࡨࡼࠧઙ"), bstack111l11l11_opy_)
        yaml.add_constructor(bstack11l1lll1_opy_ (u"ࠧࠧࡰࡢࡶ࡫ࡩࡽࠨચ"), bstack1ll1l1ll1_opy_)
        config = yaml.load(stream, yaml.FullLoader)
        return config
  except:
    with open(bstack1_opy_, bstack11l1lll1_opy_ (u"࠭ࡲࠨછ")) as stream:
      try:
        config = yaml.safe_load(stream)
        return config
      except yaml.YAMLError as exc:
        bstack1lll1l1l_opy_(bstack111ll1l1_opy_.format(str(exc)))
def bstack1111ll11_opy_(config):
  bstack1l111111_opy_ = bstack1l1l11l1_opy_(config)
  for option in list(bstack1l111111_opy_):
    if option.lower() in bstack11ll111l_opy_ and option != bstack11ll111l_opy_[option.lower()]:
      bstack1l111111_opy_[bstack11ll111l_opy_[option.lower()]] = bstack1l111111_opy_[option]
      del bstack1l111111_opy_[option]
  return config
def bstack1ll1l111l_opy_():
  global bstack11l1l1111_opy_
  for key, bstack111l1llll_opy_ in bstack11l11111_opy_.items():
    if isinstance(bstack111l1llll_opy_, list):
      for var in bstack111l1llll_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack11l1l1111_opy_[key] = os.environ[var]
          break
    elif bstack111l1llll_opy_ in os.environ and os.environ[bstack111l1llll_opy_] and str(os.environ[bstack111l1llll_opy_]).strip():
      bstack11l1l1111_opy_[key] = os.environ[bstack111l1llll_opy_]
  if bstack11l1lll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩજ") in os.environ:
    bstack11l1l1111_opy_[bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬઝ")] = {}
    bstack11l1l1111_opy_[bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ઞ")][bstack11l1lll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬટ")] = os.environ[bstack11l1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭ઠ")]
def bstack11l1l1_opy_():
  global bstack1l1l1ll1_opy_
  global bstack11l11l11_opy_
  for idx, val in enumerate(sys.argv):
    if idx<len(sys.argv) and bstack11l1lll1_opy_ (u"ࠬ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨડ").lower() == val.lower():
      bstack1l1l1ll1_opy_[bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪઢ")] = {}
      bstack1l1l1ll1_opy_[bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫણ")][bstack11l1lll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪત")] = sys.argv[idx+1]
      del sys.argv[idx:idx+2]
      break
  for key, bstack11lll1l1l_opy_ in bstack1111ll1l1_opy_.items():
    if isinstance(bstack11lll1l1l_opy_, list):
      for idx, val in enumerate(sys.argv):
        for var in bstack11lll1l1l_opy_:
          if idx<len(sys.argv) and bstack11l1lll1_opy_ (u"ࠩ࠰࠱ࠬથ") + var.lower() == val.lower() and not key in bstack1l1l1ll1_opy_:
            bstack1l1l1ll1_opy_[key] = sys.argv[idx+1]
            bstack11l11l11_opy_ += bstack11l1lll1_opy_ (u"ࠪࠤ࠲࠳ࠧદ") + var + bstack11l1lll1_opy_ (u"ࠫࠥ࠭ધ") + sys.argv[idx+1]
            del sys.argv[idx:idx+2]
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx<len(sys.argv) and bstack11l1lll1_opy_ (u"ࠬ࠳࠭ࠨન") + bstack11lll1l1l_opy_.lower() == val.lower() and not key in bstack1l1l1ll1_opy_:
          bstack1l1l1ll1_opy_[key] = sys.argv[idx+1]
          bstack11l11l11_opy_ += bstack11l1lll1_opy_ (u"࠭ࠠ࠮࠯ࠪ઩") + bstack11lll1l1l_opy_ + bstack11l1lll1_opy_ (u"ࠧࠡࠩપ") + sys.argv[idx+1]
          del sys.argv[idx:idx+2]
def bstack111lllll_opy_(config):
  bstack1ll1llll_opy_ = config.keys()
  for bstack11l111_opy_, bstack1lllllll_opy_ in bstack1l1l1ll1l_opy_.items():
    if bstack1lllllll_opy_ in bstack1ll1llll_opy_:
      config[bstack11l111_opy_] = config[bstack1lllllll_opy_]
      del config[bstack1lllllll_opy_]
  for bstack11l111_opy_, bstack1lllllll_opy_ in bstack11l11l1l_opy_.items():
    if isinstance(bstack1lllllll_opy_, list):
      for bstack1lll1ll1_opy_ in bstack1lllllll_opy_:
        if bstack1lll1ll1_opy_ in bstack1ll1llll_opy_:
          config[bstack11l111_opy_] = config[bstack1lll1ll1_opy_]
          del config[bstack1lll1ll1_opy_]
          break
    elif bstack1lllllll_opy_ in bstack1ll1llll_opy_:
        config[bstack11l111_opy_] = config[bstack1lllllll_opy_]
        del config[bstack1lllllll_opy_]
  for bstack1lll1ll1_opy_ in list(config):
    for bstack1111llll1_opy_ in bstack111ll1111_opy_:
      if bstack1lll1ll1_opy_.lower() == bstack1111llll1_opy_.lower() and bstack1lll1ll1_opy_ != bstack1111llll1_opy_:
        config[bstack1111llll1_opy_] = config[bstack1lll1ll1_opy_]
        del config[bstack1lll1ll1_opy_]
  bstack1lllll1l1_opy_ = []
  if bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫફ") in config:
    bstack1lllll1l1_opy_ = config[bstack11l1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬબ")]
  for platform in bstack1lllll1l1_opy_:
    for bstack1lll1ll1_opy_ in list(platform):
      for bstack1111llll1_opy_ in bstack111ll1111_opy_:
        if bstack1lll1ll1_opy_.lower() == bstack1111llll1_opy_.lower() and bstack1lll1ll1_opy_ != bstack1111llll1_opy_:
          platform[bstack1111llll1_opy_] = platform[bstack1lll1ll1_opy_]
          del platform[bstack1lll1ll1_opy_]
  for bstack11l111_opy_, bstack1lllllll_opy_ in bstack11l11l1l_opy_.items():
    for platform in bstack1lllll1l1_opy_:
      if isinstance(bstack1lllllll_opy_, list):
        for bstack1lll1ll1_opy_ in bstack1lllllll_opy_:
          if bstack1lll1ll1_opy_ in platform:
            platform[bstack11l111_opy_] = platform[bstack1lll1ll1_opy_]
            del platform[bstack1lll1ll1_opy_]
            break
      elif bstack1lllllll_opy_ in platform:
        platform[bstack11l111_opy_] = platform[bstack1lllllll_opy_]
        del platform[bstack1lllllll_opy_]
  for bstack1lll1l11l_opy_ in bstack1l1ll1l1l_opy_:
    if bstack1lll1l11l_opy_ in config:
      if not bstack1l1ll1l1l_opy_[bstack1lll1l11l_opy_] in config:
        config[bstack1l1ll1l1l_opy_[bstack1lll1l11l_opy_]] = {}
      config[bstack1l1ll1l1l_opy_[bstack1lll1l11l_opy_]].update(config[bstack1lll1l11l_opy_])
      del config[bstack1lll1l11l_opy_]
  for platform in bstack1lllll1l1_opy_:
    for bstack1lll1l11l_opy_ in bstack1l1ll1l1l_opy_:
      if bstack1lll1l11l_opy_ in list(platform):
        if not bstack1l1ll1l1l_opy_[bstack1lll1l11l_opy_] in platform:
          platform[bstack1l1ll1l1l_opy_[bstack1lll1l11l_opy_]] = {}
        platform[bstack1l1ll1l1l_opy_[bstack1lll1l11l_opy_]].update(platform[bstack1lll1l11l_opy_])
        del platform[bstack1lll1l11l_opy_]
  config = bstack1111ll11_opy_(config)
  return config
def bstack1ll1l1l1l_opy_(config):
  global bstack1l11_opy_
  if bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧભ") in config and str(config[bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨમ")]).lower() != bstack11l1lll1_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫય"):
    if not bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪર") in config:
      config[bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫ઱")] = {}
    if not bstack11l1lll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪલ") in config[bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ળ")]:
      bstack1ll111111_opy_ = datetime.datetime.now()
      bstack1ll111l1l_opy_ = bstack1ll111111_opy_.strftime(bstack11l1lll1_opy_ (u"ࠪࠩࡩࡥࠥࡣࡡࠨࡌࠪࡓࠧ઴"))
      hostname = socket.gethostname()
      bstack1l111l11_opy_ = bstack11l1lll1_opy_ (u"ࠫࠬવ").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack11l1lll1_opy_ (u"ࠬࢁࡽࡠࡽࢀࡣࢀࢃࠧશ").format(bstack1ll111l1l_opy_, hostname, bstack1l111l11_opy_)
      config[bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪષ")][bstack11l1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩસ")] = identifier
    bstack1l11_opy_ = config[bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬહ")][bstack11l1lll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ઺")]
  return config
def bstack11l11llll_opy_():
  if (
    isinstance(os.getenv(bstack11l1lll1_opy_ (u"ࠪࡎࡊࡔࡋࡊࡐࡖࡣ࡚ࡘࡌࠨ઻")), str) and len(os.getenv(bstack11l1lll1_opy_ (u"ࠫࡏࡋࡎࡌࡋࡑࡗࡤ࡛ࡒࡍ઼ࠩ"))) > 0
  ) or (
    isinstance(os.getenv(bstack11l1lll1_opy_ (u"ࠬࡐࡅࡏࡍࡌࡒࡘࡥࡈࡐࡏࡈࠫઽ")), str) and len(os.getenv(bstack11l1lll1_opy_ (u"࠭ࡊࡆࡐࡎࡍࡓ࡙࡟ࡉࡑࡐࡉࠬા"))) > 0
  ):
    return os.getenv(bstack11l1lll1_opy_ (u"ࠧࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗ࠭િ"), 0)
  if str(os.getenv(bstack11l1lll1_opy_ (u"ࠨࡅࡌࠫી"))).lower() == bstack11l1lll1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧુ") and str(os.getenv(bstack11l1lll1_opy_ (u"ࠪࡇࡎࡘࡃࡍࡇࡆࡍࠬૂ"))).lower() == bstack11l1lll1_opy_ (u"ࠫࡹࡸࡵࡦࠩૃ"):
    return os.getenv(bstack11l1lll1_opy_ (u"ࠬࡉࡉࡓࡅࡏࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࠨૄ"), 0)
  if str(os.getenv(bstack11l1lll1_opy_ (u"࠭ࡃࡊࠩૅ"))).lower() == bstack11l1lll1_opy_ (u"ࠧࡵࡴࡸࡩࠬ૆") and str(os.getenv(bstack11l1lll1_opy_ (u"ࠨࡖࡕࡅ࡛ࡏࡓࠨે"))).lower() == bstack11l1lll1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧૈ"):
    return os.getenv(bstack11l1lll1_opy_ (u"ࠪࡘࡗࡇࡖࡊࡕࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠩૉ"), 0)
  if str(os.getenv(bstack11l1lll1_opy_ (u"ࠫࡈࡏࠧ૊"))).lower() == bstack11l1lll1_opy_ (u"ࠬࡺࡲࡶࡧࠪો") and str(os.getenv(bstack11l1lll1_opy_ (u"࠭ࡃࡊࡡࡑࡅࡒࡋࠧૌ"))).lower() == bstack11l1lll1_opy_ (u"ࠧࡤࡱࡧࡩࡸ࡮ࡩࡱ્ࠩ"):
    return 0 # bstack111l1lll1_opy_ bstack1l1l1l_opy_ not set build number env
  if os.getenv(bstack11l1lll1_opy_ (u"ࠨࡄࡌࡘࡇ࡛ࡃࡌࡇࡗࡣࡇࡘࡁࡏࡅࡋࠫ૎")) and os.getenv(bstack11l1lll1_opy_ (u"ࠩࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡉࡏࡎࡏࡌࡘࠬ૏")):
    return os.getenv(bstack11l1lll1_opy_ (u"ࠪࡆࡎ࡚ࡂࡖࡅࡎࡉ࡙ࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠬૐ"), 0)
  if str(os.getenv(bstack11l1lll1_opy_ (u"ࠫࡈࡏࠧ૑"))).lower() == bstack11l1lll1_opy_ (u"ࠬࡺࡲࡶࡧࠪ૒") and str(os.getenv(bstack11l1lll1_opy_ (u"࠭ࡄࡓࡑࡑࡉࠬ૓"))).lower() == bstack11l1lll1_opy_ (u"ࠧࡵࡴࡸࡩࠬ૔"):
    return os.getenv(bstack11l1lll1_opy_ (u"ࠨࡆࡕࡓࡓࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗ࠭૕"), 0)
  if str(os.getenv(bstack11l1lll1_opy_ (u"ࠩࡆࡍࠬ૖"))).lower() == bstack11l1lll1_opy_ (u"ࠪࡸࡷࡻࡥࠨ૗") and str(os.getenv(bstack11l1lll1_opy_ (u"ࠫࡘࡋࡍࡂࡒࡋࡓࡗࡋࠧ૘"))).lower() == bstack11l1lll1_opy_ (u"ࠬࡺࡲࡶࡧࠪ૙"):
    return os.getenv(bstack11l1lll1_opy_ (u"࠭ࡓࡆࡏࡄࡔࡍࡕࡒࡆࡡࡍࡓࡇࡥࡉࡅࠩ૚"), 0)
  if str(os.getenv(bstack11l1lll1_opy_ (u"ࠧࡄࡋࠪ૛"))).lower() == bstack11l1lll1_opy_ (u"ࠨࡶࡵࡹࡪ࠭૜") and str(os.getenv(bstack11l1lll1_opy_ (u"ࠩࡊࡍ࡙ࡒࡁࡃࡡࡆࡍࠬ૝"))).lower() == bstack11l1lll1_opy_ (u"ࠪࡸࡷࡻࡥࠨ૞"):
    return os.getenv(bstack11l1lll1_opy_ (u"ࠫࡈࡏ࡟ࡋࡑࡅࡣࡎࡊࠧ૟"), 0)
  if str(os.getenv(bstack11l1lll1_opy_ (u"ࠬࡉࡉࠨૠ"))).lower() == bstack11l1lll1_opy_ (u"࠭ࡴࡳࡷࡨࠫૡ") and str(os.getenv(bstack11l1lll1_opy_ (u"ࠧࡃࡗࡌࡐࡉࡑࡉࡕࡇࠪૢ"))).lower() == bstack11l1lll1_opy_ (u"ࠨࡶࡵࡹࡪ࠭ૣ"):
    return os.getenv(bstack11l1lll1_opy_ (u"ࠩࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠫ૤"), 0)
  if str(os.getenv(bstack11l1lll1_opy_ (u"ࠪࡘࡋࡥࡂࡖࡋࡏࡈࠬ૥"))).lower() == bstack11l1lll1_opy_ (u"ࠫࡹࡸࡵࡦࠩ૦"):
    return os.getenv(bstack11l1lll1_opy_ (u"ࠬࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠬ૧"), 0)
  return -1
def bstack1l111lll_opy_(bstack11l1ll111_opy_):
  global CONFIG
  if not bstack11l1lll1_opy_ (u"࠭ࠤࡼࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࡽࠨ૨") in CONFIG[bstack11l1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૩")]:
    return
  CONFIG[bstack11l1lll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ૪")] = CONFIG[bstack11l1lll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ૫")].replace(
    bstack11l1lll1_opy_ (u"ࠪࠨࢀࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࢁࠬ૬"),
    str(bstack11l1ll111_opy_)
  )
def bstack1111_opy_():
  global CONFIG
  if not bstack11l1lll1_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪ૭") in CONFIG[bstack11l1lll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ૮")]:
    return
  bstack1ll111111_opy_ = datetime.datetime.now()
  bstack1ll111l1l_opy_ = bstack1ll111111_opy_.strftime(bstack11l1lll1_opy_ (u"࠭ࠥࡥ࠯ࠨࡦ࠲ࠫࡈ࠻ࠧࡐࠫ૯"))
  CONFIG[bstack11l1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૰")] = CONFIG[bstack11l1lll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ૱")].replace(
    bstack11l1lll1_opy_ (u"ࠩࠧࡿࡉࡇࡔࡆࡡࡗࡍࡒࡋࡽࠨ૲"),
    bstack1ll111l1l_opy_
  )
def bstack1ll11111_opy_():
  global CONFIG
  if bstack11l1lll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ૳") in CONFIG and not bool(CONFIG[bstack11l1lll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭૴")]):
    del CONFIG[bstack11l1lll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ૵")]
    return
  if not bstack11l1lll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ૶") in CONFIG:
    CONFIG[bstack11l1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૷")] = bstack11l1lll1_opy_ (u"ࠨࠥࠧࡿࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࢀࠫ૸")
  if bstack11l1lll1_opy_ (u"ࠩࠧࡿࡉࡇࡔࡆࡡࡗࡍࡒࡋࡽࠨૹ") in CONFIG[bstack11l1lll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬૺ")]:
    bstack1111_opy_()
    os.environ[bstack11l1lll1_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡣࡈࡕࡍࡃࡋࡑࡉࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨૻ")] = CONFIG[bstack11l1lll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧૼ")]
  if not bstack11l1lll1_opy_ (u"࠭ࠤࡼࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࡽࠨ૽") in CONFIG[bstack11l1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૾")]:
    return
  bstack11l1ll111_opy_ = bstack11l1lll1_opy_ (u"ࠨࠩ૿")
  bstack111ll111_opy_ = bstack11l11llll_opy_()
  if bstack111ll111_opy_ != -1:
    bstack11l1ll111_opy_ = bstack11l1lll1_opy_ (u"ࠩࡆࡍࠥ࠭଀") + str(bstack111ll111_opy_)
  if bstack11l1ll111_opy_ == bstack11l1lll1_opy_ (u"ࠪࠫଁ"):
    bstack1l1l111_opy_ = bstack1lll1l111_opy_(CONFIG[bstack11l1lll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧଂ")])
    if bstack1l1l111_opy_ != -1:
      bstack11l1ll111_opy_ = str(bstack1l1l111_opy_)
  if bstack11l1ll111_opy_:
    bstack1l111lll_opy_(bstack11l1ll111_opy_)
    os.environ[bstack11l1lll1_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡤࡉࡏࡎࡄࡌࡒࡊࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠩଃ")] = CONFIG[bstack11l1lll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ଄")]
def bstack1l1ll11_opy_(bstack1l11llll1_opy_, bstack11lll11_opy_, path):
  bstack11ll1111_opy_ = {
    bstack11l1lll1_opy_ (u"ࠧࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫଅ"): bstack11lll11_opy_
  }
  if os.path.exists(path):
    bstack1ll1l11l_opy_ = json.load(open(path, bstack11l1lll1_opy_ (u"ࠨࡴࡥࠫଆ")))
  else:
    bstack1ll1l11l_opy_ = {}
  bstack1ll1l11l_opy_[bstack1l11llll1_opy_] = bstack11ll1111_opy_
  with open(path, bstack11l1lll1_opy_ (u"ࠤࡺ࠯ࠧଇ")) as outfile:
    json.dump(bstack1ll1l11l_opy_, outfile)
def bstack1lll1l111_opy_(bstack1l11llll1_opy_):
  bstack1l11llll1_opy_ = str(bstack1l11llll1_opy_)
  bstack1l11l111l_opy_ = os.path.join(os.path.expanduser(bstack11l1lll1_opy_ (u"ࠪࢂࠬଈ")), bstack11l1lll1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫଉ"))
  try:
    if not os.path.exists(bstack1l11l111l_opy_):
      os.makedirs(bstack1l11l111l_opy_)
    file_path = os.path.join(os.path.expanduser(bstack11l1lll1_opy_ (u"ࠬࢄࠧଊ")), bstack11l1lll1_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ଋ"), bstack11l1lll1_opy_ (u"ࠧ࠯ࡤࡸ࡭ࡱࡪ࠭࡯ࡣࡰࡩ࠲ࡩࡡࡤࡪࡨ࠲࡯ࡹ࡯࡯ࠩଌ"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack11l1lll1_opy_ (u"ࠨࡹࠪ଍")):
        pass
      with open(file_path, bstack11l1lll1_opy_ (u"ࠤࡺ࠯ࠧ଎")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack11l1lll1_opy_ (u"ࠪࡶࠬଏ")) as bstack111l11_opy_:
      bstack111111l1_opy_ = json.load(bstack111l11_opy_)
    if bstack1l11llll1_opy_ in bstack111111l1_opy_:
      bstack1lll1l11_opy_ = bstack111111l1_opy_[bstack1l11llll1_opy_][bstack11l1lll1_opy_ (u"ࠫ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨଐ")]
      bstack1ll1l_opy_ = int(bstack1lll1l11_opy_) + 1
      bstack1l1ll11_opy_(bstack1l11llll1_opy_, bstack1ll1l_opy_, file_path)
      return bstack1ll1l_opy_
    else:
      bstack1l1ll11_opy_(bstack1l11llll1_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warn(bstack1lll1111l_opy_.format(str(e)))
    return -1
def bstack111l_opy_(config):
  if not config[bstack11l1lll1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧ଑")] or not config[bstack11l1lll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ଒")]:
    return True
  else:
    return False
def bstack111llll_opy_(config):
  if bstack11l1lll1_opy_ (u"ࠧࡪࡵࡓࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ଓ") in config:
    del(config[bstack11l1lll1_opy_ (u"ࠨ࡫ࡶࡔࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧଔ")])
    return False
  if bstack1111lllll_opy_() < version.parse(bstack11l1lll1_opy_ (u"ࠩ࠶࠲࠹࠴࠰ࠨକ")):
    return False
  if bstack1111lllll_opy_() >= version.parse(bstack11l1lll1_opy_ (u"ࠪ࠸࠳࠷࠮࠶ࠩଖ")):
    return True
  if bstack11l1lll1_opy_ (u"ࠫࡺࡹࡥࡘ࠵ࡆࠫଗ") in config and config[bstack11l1lll1_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬଘ")] == False:
    return False
  else:
    return True
def bstack11ll1ll1l_opy_(config, index = 0):
  global bstack111l1l11l_opy_
  bstack1l111l1_opy_ = {}
  caps = bstack1llll1l_opy_ + bstack1l1l1l1l1_opy_
  if bstack111l1l11l_opy_:
    caps += bstack1l11l1111_opy_
  for key in config:
    if key in caps + [bstack11l1lll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩଙ")]:
      continue
    bstack1l111l1_opy_[key] = config[key]
  if bstack11l1lll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪଚ") in config:
    for bstack11lll11l_opy_ in config[bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫଛ")][index]:
      if bstack11lll11l_opy_ in caps + [bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧଜ"), bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫଝ")]:
        continue
      bstack1l111l1_opy_[bstack11lll11l_opy_] = config[bstack11l1lll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧଞ")][index][bstack11lll11l_opy_]
  bstack1l111l1_opy_[bstack11l1lll1_opy_ (u"ࠬ࡮࡯ࡴࡶࡑࡥࡲ࡫ࠧଟ")] = socket.gethostname()
  if bstack11l1lll1_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧଠ") in bstack1l111l1_opy_:
    del(bstack1l111l1_opy_[bstack11l1lll1_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨଡ")])
  return bstack1l111l1_opy_
def bstack111l11l_opy_(config):
  global bstack111l1l11l_opy_
  bstack1l11111_opy_ = {}
  caps = bstack1l1l1l1l1_opy_
  if bstack111l1l11l_opy_:
    caps+= bstack1l11l1111_opy_
  for key in caps:
    if key in config:
      bstack1l11111_opy_[key] = config[key]
  return bstack1l11111_opy_
def bstack11ll11l1l_opy_(bstack1l111l1_opy_, bstack1l11111_opy_):
  bstack1lllll1_opy_ = {}
  for key in bstack1l111l1_opy_.keys():
    if key in bstack1l1l1ll1l_opy_:
      bstack1lllll1_opy_[bstack1l1l1ll1l_opy_[key]] = bstack1l111l1_opy_[key]
    else:
      bstack1lllll1_opy_[key] = bstack1l111l1_opy_[key]
  for key in bstack1l11111_opy_:
    if key in bstack1l1l1ll1l_opy_:
      bstack1lllll1_opy_[bstack1l1l1ll1l_opy_[key]] = bstack1l11111_opy_[key]
    else:
      bstack1lllll1_opy_[key] = bstack1l11111_opy_[key]
  return bstack1lllll1_opy_
def bstack111111_opy_(config, index = 0):
  global bstack111l1l11l_opy_
  config = copy.deepcopy(config)
  caps = {}
  bstack1l11111_opy_ = bstack111l11l_opy_(config)
  bstack1lllll1ll_opy_ = bstack1l1l1l1l1_opy_
  bstack1lllll1ll_opy_ += bstack11llllll1_opy_
  if bstack111l1l11l_opy_:
    bstack1lllll1ll_opy_ += bstack1l11l1111_opy_
  if bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫଢ") in config:
    if bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧଣ") in config[bstack11l1lll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ତ")][index]:
      caps[bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩଥ")] = config[bstack11l1lll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨଦ")][index][bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫଧ")]
    if bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨନ") in config[bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ଩")][index]:
      caps[bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪପ")] = str(config[bstack11l1lll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଫ")][index][bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬବ")])
    bstack1l11ll11l_opy_ = {}
    for bstack1ll1l11ll_opy_ in bstack1lllll1ll_opy_:
      if bstack1ll1l11ll_opy_ in config[bstack11l1lll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨଭ")][index]:
        if bstack1ll1l11ll_opy_ == bstack11l1lll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨମ"):
          try:
            bstack1l11ll11l_opy_[bstack1ll1l11ll_opy_] = str(config[bstack11l1lll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪଯ")][index][bstack1ll1l11ll_opy_] * 1.0)
          except:
            bstack1l11ll11l_opy_[bstack1ll1l11ll_opy_] = str(config[bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫର")][index][bstack1ll1l11ll_opy_])
        else:
          bstack1l11ll11l_opy_[bstack1ll1l11ll_opy_] = config[bstack11l1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ଱")][index][bstack1ll1l11ll_opy_]
        del(config[bstack11l1lll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଲ")][index][bstack1ll1l11ll_opy_])
    bstack1l11111_opy_ = update(bstack1l11111_opy_, bstack1l11ll11l_opy_)
  bstack1l111l1_opy_ = bstack11ll1ll1l_opy_(config, index)
  for bstack1lll1ll1_opy_ in bstack1l1l1l1l1_opy_ + [bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩଳ"), bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭଴")]:
    if bstack1lll1ll1_opy_ in bstack1l111l1_opy_:
      bstack1l11111_opy_[bstack1lll1ll1_opy_] = bstack1l111l1_opy_[bstack1lll1ll1_opy_]
      del(bstack1l111l1_opy_[bstack1lll1ll1_opy_])
  if bstack111llll_opy_(config):
    bstack1l111l1_opy_[bstack11l1lll1_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ଵ")] = True
    caps.update(bstack1l11111_opy_)
    caps[bstack11l1lll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨଶ")] = bstack1l111l1_opy_
  else:
    bstack1l111l1_opy_[bstack11l1lll1_opy_ (u"ࠨࡷࡶࡩ࡜࠹ࡃࠨଷ")] = False
    caps.update(bstack11ll11l1l_opy_(bstack1l111l1_opy_, bstack1l11111_opy_))
    if bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧସ") in caps:
      caps[bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫହ")] = caps[bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩ଺")]
      del(caps[bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ଻")])
    if bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴ଼ࠧ") in caps:
      caps[bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩଽ")] = caps[bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩା")]
      del(caps[bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪି")])
  return caps
def bstack1l1l111ll_opy_():
  global bstack1lllll111_opy_
  if bstack1111lllll_opy_() <= version.parse(bstack11l1lll1_opy_ (u"ࠪ࠷࠳࠷࠳࠯࠲ࠪୀ")):
    if bstack1lllll111_opy_ != bstack11l1lll1_opy_ (u"ࠫࠬୁ"):
      return bstack11l1lll1_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨୂ") + bstack1lllll111_opy_ + bstack11l1lll1_opy_ (u"ࠨ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠥୃ")
    return bstack11lllll1l_opy_
  if  bstack1lllll111_opy_ != bstack11l1lll1_opy_ (u"ࠧࠨୄ"):
    return bstack11l1lll1_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࠥ୅") + bstack1lllll111_opy_ + bstack11l1lll1_opy_ (u"ࠤ࠲ࡻࡩ࠵ࡨࡶࡤࠥ୆")
  return bstack11ll11l11_opy_
def bstack1llll11_opy_(options):
  return hasattr(options, bstack11l1lll1_opy_ (u"ࠪࡷࡪࡺ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶࡼࠫେ"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1ll1l1l11_opy_(options, bstack11ll111ll_opy_):
  for bstack11ll1111l_opy_ in bstack11ll111ll_opy_:
    if bstack11ll1111l_opy_ in [bstack11l1lll1_opy_ (u"ࠫࡦࡸࡧࡴࠩୈ"), bstack11l1lll1_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩ୉")]:
      next
    if bstack11ll1111l_opy_ in options._experimental_options:
      options._experimental_options[bstack11ll1111l_opy_]= update(options._experimental_options[bstack11ll1111l_opy_], bstack11ll111ll_opy_[bstack11ll1111l_opy_])
    else:
      options.add_experimental_option(bstack11ll1111l_opy_, bstack11ll111ll_opy_[bstack11ll1111l_opy_])
  if bstack11l1lll1_opy_ (u"࠭ࡡࡳࡩࡶࠫ୊") in bstack11ll111ll_opy_:
    for arg in bstack11ll111ll_opy_[bstack11l1lll1_opy_ (u"ࠧࡢࡴࡪࡷࠬୋ")]:
      options.add_argument(arg)
    del(bstack11ll111ll_opy_[bstack11l1lll1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ୌ")])
  if bstack11l1lll1_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ୍࠭") in bstack11ll111ll_opy_:
    for ext in bstack11ll111ll_opy_[bstack11l1lll1_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧ୎")]:
      options.add_extension(ext)
    del(bstack11ll111ll_opy_[bstack11l1lll1_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨ୏")])
def bstack11111_opy_(options, bstack1ll1111ll_opy_):
  if bstack11l1lll1_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫ୐") in bstack1ll1111ll_opy_:
    for bstack1l1ll1l1_opy_ in bstack1ll1111ll_opy_[bstack11l1lll1_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬ୑")]:
      if bstack1l1ll1l1_opy_ in options._preferences:
        options._preferences[bstack1l1ll1l1_opy_] = update(options._preferences[bstack1l1ll1l1_opy_], bstack1ll1111ll_opy_[bstack11l1lll1_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭୒")][bstack1l1ll1l1_opy_])
      else:
        options.set_preference(bstack1l1ll1l1_opy_, bstack1ll1111ll_opy_[bstack11l1lll1_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧ୓")][bstack1l1ll1l1_opy_])
  if bstack11l1lll1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ୔") in bstack1ll1111ll_opy_:
    for arg in bstack1ll1111ll_opy_[bstack11l1lll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ୕")]:
      options.add_argument(arg)
def bstack1l1ll1lll_opy_(options, bstack1111l11l_opy_):
  if bstack11l1lll1_opy_ (u"ࠫࡼ࡫ࡢࡷ࡫ࡨࡻࠬୖ") in bstack1111l11l_opy_:
    options.use_webview(bool(bstack1111l11l_opy_[bstack11l1lll1_opy_ (u"ࠬࡽࡥࡣࡸ࡬ࡩࡼ࠭ୗ")]))
  bstack1ll1l1l11_opy_(options, bstack1111l11l_opy_)
def bstack1l1l1l111_opy_(options, bstack111l1111_opy_):
  for bstack1lll11l_opy_ in bstack111l1111_opy_:
    if bstack1lll11l_opy_ in [bstack11l1lll1_opy_ (u"࠭ࡴࡦࡥ࡫ࡲࡴࡲ࡯ࡨࡻࡓࡶࡪࡼࡩࡦࡹࠪ୘"), bstack11l1lll1_opy_ (u"ࠧࡢࡴࡪࡷࠬ୙")]:
      next
    options.set_capability(bstack1lll11l_opy_, bstack111l1111_opy_[bstack1lll11l_opy_])
  if bstack11l1lll1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭୚") in bstack111l1111_opy_:
    for arg in bstack111l1111_opy_[bstack11l1lll1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ୛")]:
      options.add_argument(arg)
  if bstack11l1lll1_opy_ (u"ࠪࡸࡪࡩࡨ࡯ࡱ࡯ࡳ࡬ࡿࡐࡳࡧࡹ࡭ࡪࡽࠧଡ଼") in bstack111l1111_opy_:
    options.bstack1l1lll11l_opy_(bool(bstack111l1111_opy_[bstack11l1lll1_opy_ (u"ࠫࡹ࡫ࡣࡩࡰࡲࡰࡴ࡭ࡹࡑࡴࡨࡺ࡮࡫ࡷࠨଢ଼")]))
def bstack11l1ll1_opy_(options, bstack1llll1l1_opy_):
  for bstack11lllll_opy_ in bstack1llll1l1_opy_:
    if bstack11lllll_opy_ in [bstack11l1lll1_opy_ (u"ࠬࡧࡤࡥ࡫ࡷ࡭ࡴࡴࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ୞"), bstack11l1lll1_opy_ (u"࠭ࡡࡳࡩࡶࠫୟ")]:
      next
    options._options[bstack11lllll_opy_] = bstack1llll1l1_opy_[bstack11lllll_opy_]
  if bstack11l1lll1_opy_ (u"ࠧࡢࡦࡧ࡭ࡹ࡯࡯࡯ࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫୠ") in bstack1llll1l1_opy_:
    for bstack1lll11l1_opy_ in bstack1llll1l1_opy_[bstack11l1lll1_opy_ (u"ࠨࡣࡧࡨ࡮ࡺࡩࡰࡰࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬୡ")]:
      options.bstack11111l1_opy_(
          bstack1lll11l1_opy_, bstack1llll1l1_opy_[bstack11l1lll1_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ୢ")][bstack1lll11l1_opy_])
  if bstack11l1lll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨୣ") in bstack1llll1l1_opy_:
    for arg in bstack1llll1l1_opy_[bstack11l1lll1_opy_ (u"ࠫࡦࡸࡧࡴࠩ୤")]:
      options.add_argument(arg)
def bstack1111l111_opy_(options, caps):
  if not hasattr(options, bstack11l1lll1_opy_ (u"ࠬࡑࡅ࡚ࠩ୥")):
    return
  if options.KEY == bstack11l1lll1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ୦") and options.KEY in caps:
    bstack1ll1l1l11_opy_(options, caps[bstack11l1lll1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ୧")])
  elif options.KEY == bstack11l1lll1_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭୨") and options.KEY in caps:
    bstack11111_opy_(options, caps[bstack11l1lll1_opy_ (u"ࠩࡰࡳࡿࡀࡦࡪࡴࡨࡪࡴࡾࡏࡱࡶ࡬ࡳࡳࡹࠧ୩")])
  elif options.KEY == bstack11l1lll1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫࠱ࡳࡵࡺࡩࡰࡰࡶࠫ୪") and options.KEY in caps:
    bstack1l1l1l111_opy_(options, caps[bstack11l1lll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬ୫")])
  elif options.KEY == bstack11l1lll1_opy_ (u"ࠬࡳࡳ࠻ࡧࡧ࡫ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭୬") and options.KEY in caps:
    bstack1l1ll1lll_opy_(options, caps[bstack11l1lll1_opy_ (u"࠭࡭ࡴ࠼ࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ୭")])
  elif options.KEY == bstack11l1lll1_opy_ (u"ࠧࡴࡧ࠽࡭ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭୮") and options.KEY in caps:
    bstack11l1ll1_opy_(options, caps[bstack11l1lll1_opy_ (u"ࠨࡵࡨ࠾࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ୯")])
def bstack1l1ll1111_opy_(caps):
  global bstack111l1l11l_opy_
  if bstack111l1l11l_opy_:
    if bstack1l1l111l_opy_() < version.parse(bstack11l1lll1_opy_ (u"ࠩ࠵࠲࠸࠴࠰ࠨ୰")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack11l1lll1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪୱ")
    if bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩ୲") in caps:
      browser = caps[bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ୳")]
    elif bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧ୴") in caps:
      browser = caps[bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨ୵")]
    browser = str(browser).lower()
    if browser == bstack11l1lll1_opy_ (u"ࠨ࡫ࡳ࡬ࡴࡴࡥࠨ୶") or browser == bstack11l1lll1_opy_ (u"ࠩ࡬ࡴࡦࡪࠧ୷"):
      browser = bstack11l1lll1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪ୸")
    if browser == bstack11l1lll1_opy_ (u"ࠫࡸࡧ࡭ࡴࡷࡱ࡫ࠬ୹"):
      browser = bstack11l1lll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬ୺")
    if browser not in [bstack11l1lll1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭୻"), bstack11l1lll1_opy_ (u"ࠧࡦࡦࡪࡩࠬ୼"), bstack11l1lll1_opy_ (u"ࠨ࡫ࡨࠫ୽"), bstack11l1lll1_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࠩ୾"), bstack11l1lll1_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫ୿")]:
      return None
    try:
      package = bstack11l1lll1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳ࠰ࡾࢁ࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭஀").format(browser)
      name = bstack11l1lll1_opy_ (u"ࠬࡕࡰࡵ࡫ࡲࡲࡸ࠭஁")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack1llll11_opy_(options):
        return None
      for bstack1lll1ll1_opy_ in caps.keys():
        options.set_capability(bstack1lll1ll1_opy_, caps[bstack1lll1ll1_opy_])
      bstack1111l111_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack11ll11l1_opy_(options, bstack111l1ll1_opy_):
  if not bstack1llll11_opy_(options):
    return
  for bstack1lll1ll1_opy_ in bstack111l1ll1_opy_.keys():
    if bstack1lll1ll1_opy_ in bstack11llllll1_opy_:
      next
    if bstack1lll1ll1_opy_ in options._caps and type(options._caps[bstack1lll1ll1_opy_]) in [dict, list]:
      options._caps[bstack1lll1ll1_opy_] = update(options._caps[bstack1lll1ll1_opy_], bstack111l1ll1_opy_[bstack1lll1ll1_opy_])
    else:
      options.set_capability(bstack1lll1ll1_opy_, bstack111l1ll1_opy_[bstack1lll1ll1_opy_])
  bstack1111l111_opy_(options, bstack111l1ll1_opy_)
  if bstack11l1lll1_opy_ (u"࠭࡭ࡰࡼ࠽ࡨࡪࡨࡵࡨࡩࡨࡶࡆࡪࡤࡳࡧࡶࡷࠬஂ") in options._caps:
    if options._caps[bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬஃ")] and options._caps[bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭஄")].lower() != bstack11l1lll1_opy_ (u"ࠩࡩ࡭ࡷ࡫ࡦࡰࡺࠪஅ"):
      del options._caps[bstack11l1lll1_opy_ (u"ࠪࡱࡴࢀ࠺ࡥࡧࡥࡹ࡬࡭ࡥࡳࡃࡧࡨࡷ࡫ࡳࡴࠩஆ")]
def bstack1lll1lll1_opy_(proxy_config):
  if bstack11l1lll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨஇ") in proxy_config:
    proxy_config[bstack11l1lll1_opy_ (u"ࠬࡹࡳ࡭ࡒࡵࡳࡽࡿࠧஈ")] = proxy_config[bstack11l1lll1_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪஉ")]
    del(proxy_config[bstack11l1lll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫஊ")])
  if bstack11l1lll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫ஋") in proxy_config and proxy_config[bstack11l1lll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡕࡻࡳࡩࠬ஌")].lower() != bstack11l1lll1_opy_ (u"ࠪࡨ࡮ࡸࡥࡤࡶࠪ஍"):
    proxy_config[bstack11l1lll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡗࡽࡵ࡫ࠧஎ")] = bstack11l1lll1_opy_ (u"ࠬࡳࡡ࡯ࡷࡤࡰࠬஏ")
  if bstack11l1lll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࡆࡻࡴࡰࡥࡲࡲ࡫࡯ࡧࡖࡴ࡯ࠫஐ") in proxy_config:
    proxy_config[bstack11l1lll1_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡚ࡹࡱࡧࠪ஑")] = bstack11l1lll1_opy_ (u"ࠨࡲࡤࡧࠬஒ")
  return proxy_config
def bstack1l1l1l1_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack11l1lll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨஓ") in config:
    return proxy
  config[bstack11l1lll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩஔ")] = bstack1lll1lll1_opy_(config[bstack11l1lll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪக")])
  if proxy == None:
    proxy = Proxy(config[bstack11l1lll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫ஖")])
  return proxy
def bstack111_opy_(self):
  global CONFIG
  global bstack11l1l_opy_
  try:
    proxy = bstack11lll1ll1_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack11l1lll1_opy_ (u"࠭࠮ࡱࡣࡦࠫ஗")):
        proxies = bstack1l11lll11_opy_(proxy, bstack1l1l111ll_opy_())
        if len(proxies) > 0:
          protocol, bstack11l111111_opy_ = proxies.popitem()
          if bstack11l1lll1_opy_ (u"ࠢ࠻࠱࠲ࠦ஘") in bstack11l111111_opy_:
            return bstack11l111111_opy_
          else:
            return bstack11l1lll1_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤங") + bstack11l111111_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack11l1lll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡶࡲࡰࡺࡼࠤࡺࡸ࡬ࠡ࠼ࠣࡿࢂࠨச").format(str(e)))
  return bstack11l1l_opy_(self)
def bstack11ll11111_opy_():
  global CONFIG
  return bstack11l1lll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ࠭஛") in CONFIG or bstack11l1lll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨஜ") in CONFIG
def bstack11lll1ll1_opy_(config):
  if not bstack11ll11111_opy_():
    return
  if config.get(bstack11l1lll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨ஝")):
    return config.get(bstack11l1lll1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩஞ"))
  if config.get(bstack11l1lll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫட")):
    return config.get(bstack11l1lll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ஠"))
def bstack1l11l111_opy_(url):
  try:
      result = urlparse(url)
      return all([result.scheme, result.netloc])
  except:
      return False
def bstack1l1lll1l_opy_(bstack1l1llll1l_opy_, bstack11ll1l11_opy_):
  from pypac import get_pac
  from pypac import PACSession
  from pypac.parser import PACFile
  import socket
  if os.path.isfile(bstack1l1llll1l_opy_):
    with open(bstack1l1llll1l_opy_) as f:
      pac = PACFile(f.read())
  elif bstack1l11l111_opy_(bstack1l1llll1l_opy_):
    pac = get_pac(url=bstack1l1llll1l_opy_)
  else:
    raise Exception(bstack11l1lll1_opy_ (u"ࠩࡓࡥࡨࠦࡦࡪ࡮ࡨࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡥࡹ࡫ࡶࡸ࠿ࠦࡻࡾࠩ஡").format(bstack1l1llll1l_opy_))
  session = PACSession(pac)
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((bstack11l1lll1_opy_ (u"ࠥ࠼࠳࠾࠮࠹࠰࠻ࠦ஢"), 80))
    bstack111l1ll_opy_ = s.getsockname()[0]
    s.close()
  except:
    bstack111l1ll_opy_ = bstack11l1lll1_opy_ (u"ࠫ࠵࠴࠰࠯࠲࠱࠴ࠬண")
  proxy_url = session.get_pac().find_proxy_for_url(bstack11ll1l11_opy_, bstack111l1ll_opy_)
  return proxy_url
def bstack1l11lll11_opy_(bstack1l1llll1l_opy_, bstack11ll1l11_opy_):
  proxies = {}
  global bstack111l11l1l_opy_
  if bstack11l1lll1_opy_ (u"ࠬࡖࡁࡄࡡࡓࡖࡔ࡞࡙ࠨத") in globals():
    return bstack111l11l1l_opy_
  try:
    proxy = bstack1l1lll1l_opy_(bstack1l1llll1l_opy_,bstack11ll1l11_opy_)
    if bstack11l1lll1_opy_ (u"ࠨࡄࡊࡔࡈࡇ࡙ࠨ஥") in proxy:
      proxies = {}
    elif bstack11l1lll1_opy_ (u"ࠢࡉࡖࡗࡔࠧ஦") in proxy or bstack11l1lll1_opy_ (u"ࠣࡊࡗࡘࡕ࡙ࠢ஧") in proxy or bstack11l1lll1_opy_ (u"ࠤࡖࡓࡈࡑࡓࠣந") in proxy:
      bstack1ll1lllll_opy_ = proxy.split(bstack11l1lll1_opy_ (u"ࠥࠤࠧன"))
      if bstack11l1lll1_opy_ (u"ࠦ࠿࠵࠯ࠣப") in bstack11l1lll1_opy_ (u"ࠧࠨ஫").join(bstack1ll1lllll_opy_[1:]):
        proxies = {
          bstack11l1lll1_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬ஬"): bstack11l1lll1_opy_ (u"ࠢࠣ஭").join(bstack1ll1lllll_opy_[1:])
        }
      else:
        proxies = {
          bstack11l1lll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧம") : str(bstack1ll1lllll_opy_[0]).lower()+ bstack11l1lll1_opy_ (u"ࠤ࠽࠳࠴ࠨய") + bstack11l1lll1_opy_ (u"ࠥࠦர").join(bstack1ll1lllll_opy_[1:])
        }
    elif bstack11l1lll1_opy_ (u"ࠦࡕࡘࡏ࡙࡛ࠥற") in proxy:
      bstack1ll1lllll_opy_ = proxy.split(bstack11l1lll1_opy_ (u"ࠧࠦࠢல"))
      if bstack11l1lll1_opy_ (u"ࠨ࠺࠰࠱ࠥள") in bstack11l1lll1_opy_ (u"ࠢࠣழ").join(bstack1ll1lllll_opy_[1:]):
        proxies = {
          bstack11l1lll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧவ"): bstack11l1lll1_opy_ (u"ࠤࠥஶ").join(bstack1ll1lllll_opy_[1:])
        }
      else:
        proxies = {
          bstack11l1lll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩஷ"): bstack11l1lll1_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧஸ") + bstack11l1lll1_opy_ (u"ࠧࠨஹ").join(bstack1ll1lllll_opy_[1:])
        }
    else:
      proxies = {
        bstack11l1lll1_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬ஺"): proxy
      }
  except Exception as e:
    logger.error(bstack11l11l111_opy_.format(bstack1l1llll1l_opy_, str(e)))
  bstack111l11l1l_opy_ = proxies
  return proxies
def bstack11ll1l1l1_opy_(config, bstack11ll1l11_opy_):
  proxy = bstack11lll1ll1_opy_(config)
  proxies = {}
  if config.get(bstack11l1lll1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪ஻")) or config.get(bstack11l1lll1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ஼")):
    if proxy.endswith(bstack11l1lll1_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ஽")):
      proxies = bstack1l11lll11_opy_(proxy,bstack11ll1l11_opy_)
    else:
      proxies = {
        bstack11l1lll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩா"): proxy
      }
  return proxies
def bstack1111ll1ll_opy_():
  return bstack11ll11111_opy_() and bstack1111lllll_opy_() >= version.parse(bstack11l1l1ll1_opy_)
def bstack1l1l11l1_opy_(config):
  bstack1l111111_opy_ = {}
  if bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨி") in config:
    bstack1l111111_opy_ =  config[bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩீ")]
  if bstack11l1lll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬு") in config:
    bstack1l111111_opy_ = config[bstack11l1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ூ")]
  proxy = bstack11lll1ll1_opy_(config)
  if proxy:
    if proxy.endswith(bstack11l1lll1_opy_ (u"ࠨ࠰ࡳࡥࡨ࠭௃")) and os.path.isfile(proxy):
      bstack1l111111_opy_[bstack11l1lll1_opy_ (u"ࠩ࠰ࡴࡦࡩ࠭ࡧ࡫࡯ࡩࠬ௄")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack11l1lll1_opy_ (u"ࠪ࠲ࡵࡧࡣࠨ௅")):
        proxies = bstack11ll1l1l1_opy_(config, bstack1l1l111ll_opy_())
        if len(proxies) > 0:
          protocol, bstack11l111111_opy_ = proxies.popitem()
          if bstack11l1lll1_opy_ (u"ࠦ࠿࠵࠯ࠣெ") in bstack11l111111_opy_:
            parsed_url = urlparse(bstack11l111111_opy_)
          else:
            parsed_url = urlparse(protocol + bstack11l1lll1_opy_ (u"ࠧࡀ࠯࠰ࠤே") + bstack11l111111_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack1l111111_opy_[bstack11l1lll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࡍࡵࡳࡵࠩை")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack1l111111_opy_[bstack11l1lll1_opy_ (u"ࠧࡱࡴࡲࡼࡾࡖ࡯ࡳࡶࠪ௉")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack1l111111_opy_[bstack11l1lll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡕࡴࡧࡵࠫொ")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack1l111111_opy_[bstack11l1lll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡣࡶࡷࠬோ")] = str(parsed_url.password)
  return bstack1l111111_opy_
def bstack111ll1l1l_opy_(config):
  if bstack11l1lll1_opy_ (u"ࠪࡸࡪࡹࡴࡄࡱࡱࡸࡪࡾࡴࡐࡲࡷ࡭ࡴࡴࡳࠨௌ") in config:
    return config[bstack11l1lll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴ்ࠩ")]
  return {}
def bstack11ll11ll_opy_(caps):
  global bstack1l11_opy_
  if bstack11l1lll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭௎") in caps:
    caps[bstack11l1lll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ௏")][bstack11l1lll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࠭ௐ")] = True
    if bstack1l11_opy_:
      caps[bstack11l1lll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ௑")][bstack11l1lll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ௒")] = bstack1l11_opy_
  else:
    caps[bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳࡨࡧ࡬ࠨ௓")] = True
    if bstack1l11_opy_:
      caps[bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ௔")] = bstack1l11_opy_
def bstack111l1l11_opy_():
  global CONFIG
  if bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ௕") in CONFIG and CONFIG[bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ௖")]:
    bstack1l111111_opy_ = bstack1l1l11l1_opy_(CONFIG)
    bstack1111ll_opy_(CONFIG[bstack11l1lll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪௗ")], bstack1l111111_opy_)
def bstack1111ll_opy_(key, bstack1l111111_opy_):
  global bstack1lll11ll_opy_
  logger.info(bstack1111ll11l_opy_)
  try:
    bstack1lll11ll_opy_ = Local()
    bstack1l1l11l11_opy_ = {bstack11l1lll1_opy_ (u"ࠨ࡭ࡨࡽࠬ௘"): key}
    bstack1l1l11l11_opy_.update(bstack1l111111_opy_)
    logger.debug(bstack1ll11l1_opy_.format(str(bstack1l1l11l11_opy_)))
    bstack1lll11ll_opy_.start(**bstack1l1l11l11_opy_)
    if bstack1lll11ll_opy_.isRunning():
      logger.info(bstack1llll1lll_opy_)
  except Exception as e:
    bstack1lll1l1l_opy_(bstack111l11lll_opy_.format(str(e)))
def bstack1111111_opy_():
  global bstack1lll11ll_opy_
  if bstack1lll11ll_opy_.isRunning():
    logger.info(bstack1l11l11l_opy_)
    bstack1lll11ll_opy_.stop()
  bstack1lll11ll_opy_ = None
def bstack11l11ll11_opy_(bstack1l111l11l_opy_=[]):
  global CONFIG
  bstack11l1llll_opy_ = []
  bstack11111l1l_opy_ = [bstack11l1lll1_opy_ (u"ࠩࡲࡷࠬ௙"), bstack11l1lll1_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭௚"), bstack11l1lll1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨ௛"), bstack11l1lll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧ௜"), bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫ௝"), bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ௞")]
  try:
    for err in bstack1l111l11l_opy_:
      bstack1111lll_opy_ = {}
      for k in bstack11111l1l_opy_:
        val = CONFIG[bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ௟")][int(err[bstack11l1lll1_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨ௠")])].get(k)
        if val:
          bstack1111lll_opy_[k] = val
      bstack1111lll_opy_[bstack11l1lll1_opy_ (u"ࠪࡸࡪࡹࡴࡴࠩ௡")] = {
        err[bstack11l1lll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ௢")]: err[bstack11l1lll1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ௣")]
      }
      bstack11l1llll_opy_.append(bstack1111lll_opy_)
  except Exception as e:
    logger.debug(bstack11l1lll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡨࡲࡶࡲࡧࡴࡵ࡫ࡱ࡫ࠥࡪࡡࡵࡣࠣࡪࡴࡸࠠࡦࡸࡨࡲࡹࡀࠠࠨ௤") +str(e))
  finally:
    return bstack11l1llll_opy_
def bstack1l1l11l_opy_():
  global bstack1l1111l1_opy_
  global bstack11llll11l_opy_
  global bstack1l1ll1_opy_
  if bstack1l1111l1_opy_:
    logger.warning(bstack1l1lllll_opy_.format(str(bstack1l1111l1_opy_)))
  logger.info(bstack11l1_opy_)
  global bstack1lll11ll_opy_
  if bstack1lll11ll_opy_:
    bstack1111111_opy_()
  try:
    for driver in bstack11llll11l_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack1lll11l1l_opy_)
  bstack1lllll11_opy_()
  if len(bstack1l1ll1_opy_) > 0:
    message = bstack11l11ll11_opy_(bstack1l1ll1_opy_)
    bstack1lllll11_opy_(message)
  else:
    bstack1lllll11_opy_()
def bstack11ll_opy_(self, *args):
  logger.error(bstack1l11lll1l_opy_)
  bstack1l1l11l_opy_()
  sys.exit(1)
def bstack1lll1l1l_opy_(err):
  logger.critical(bstack1l11ll1_opy_.format(str(err)))
  bstack1lllll11_opy_(bstack1l11ll1_opy_.format(str(err)))
  atexit.unregister(bstack1l1l11l_opy_)
  sys.exit(1)
def bstack111ll1l11_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack1lllll11_opy_(message)
  atexit.unregister(bstack1l1l11l_opy_)
  sys.exit(1)
def bstack1l1llll1_opy_():
  global CONFIG
  global bstack1l1l1ll1_opy_
  global bstack11l1l1111_opy_
  global bstack111ll111l_opy_
  CONFIG = bstack11ll11_opy_()
  bstack1ll1l111l_opy_()
  bstack11l1l1_opy_()
  CONFIG = bstack111lllll_opy_(CONFIG)
  update(CONFIG, bstack11l1l1111_opy_)
  update(CONFIG, bstack1l1l1ll1_opy_)
  CONFIG = bstack1ll1l1l1l_opy_(CONFIG)
  if bstack11l1lll1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫ௥") in CONFIG and str(CONFIG[bstack11l1lll1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬ௦")]).lower() == bstack11l1lll1_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ௧"):
    bstack111ll111l_opy_ = False
  if (bstack11l1lll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭௨") in CONFIG and bstack11l1lll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ௩") in bstack1l1l1ll1_opy_) or (bstack11l1lll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ௪") in CONFIG and bstack11l1lll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ௫") not in bstack11l1l1111_opy_):
    if os.getenv(bstack11l1lll1_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑ࡟ࡄࡑࡐࡆࡎࡔࡅࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠫ௬")):
      CONFIG[bstack11l1lll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ௭")] = os.getenv(bstack11l1lll1_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡡࡆࡓࡒࡈࡉࡏࡇࡇࡣࡇ࡛ࡉࡍࡆࡢࡍࡉ࠭௮"))
    else:
      bstack1ll11111_opy_()
  elif (bstack11l1lll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭௯") not in CONFIG and bstack11l1lll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭௰") in CONFIG) or (bstack11l1lll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ௱") in bstack11l1l1111_opy_ and bstack11l1lll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ௲") not in bstack1l1l1ll1_opy_):
    del(CONFIG[bstack11l1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ௳")])
  if bstack111l_opy_(CONFIG):
    bstack1lll1l1l_opy_(bstack11l1lll_opy_)
  bstack1llll11ll_opy_()
  bstack11ll11lll_opy_()
  if bstack111l1l11l_opy_:
    CONFIG[bstack11l1lll1_opy_ (u"ࠨࡣࡳࡴࠬ௴")] = bstack111ll_opy_(CONFIG)
    logger.info(bstack11lllllll_opy_.format(CONFIG[bstack11l1lll1_opy_ (u"ࠩࡤࡴࡵ࠭௵")]))
def bstack11ll11lll_opy_():
  global CONFIG
  global bstack111l1l11l_opy_
  if bstack11l1lll1_opy_ (u"ࠪࡥࡵࡶࠧ௶") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack111ll1l11_opy_(e, bstack1llll1_opy_)
    bstack111l1l11l_opy_ = True
def bstack111ll_opy_(config):
  bstack1l1ll111l_opy_ = bstack11l1lll1_opy_ (u"ࠫࠬ௷")
  app = config[bstack11l1lll1_opy_ (u"ࠬࡧࡰࡱࠩ௸")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack111ll11l1_opy_:
      if os.path.exists(app):
        bstack1l1ll111l_opy_ = bstack111ll11l_opy_(config, app)
      elif bstack1ll1ll1ll_opy_(app):
        bstack1l1ll111l_opy_ = app
      else:
        bstack1lll1l1l_opy_(bstack1111llll_opy_.format(app))
    else:
      if bstack1ll1ll1ll_opy_(app):
        bstack1l1ll111l_opy_ = app
      elif os.path.exists(app):
        bstack1l1ll111l_opy_ = bstack111ll11l_opy_(app)
      else:
        bstack1lll1l1l_opy_(bstack1l1ll1ll_opy_)
  else:
    if len(app) > 2:
      bstack1lll1l1l_opy_(bstack11l1ll1l1_opy_)
    elif len(app) == 2:
      if bstack11l1lll1_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ௹") in app and bstack11l1lll1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳ࡟ࡪࡦࠪ௺") in app:
        if os.path.exists(app[bstack11l1lll1_opy_ (u"ࠨࡲࡤࡸ࡭࠭௻")]):
          bstack1l1ll111l_opy_ = bstack111ll11l_opy_(config, app[bstack11l1lll1_opy_ (u"ࠩࡳࡥࡹ࡮ࠧ௼")], app[bstack11l1lll1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡢ࡭ࡩ࠭௽")])
        else:
          bstack1lll1l1l_opy_(bstack1111llll_opy_.format(app))
      else:
        bstack1lll1l1l_opy_(bstack11l1ll1l1_opy_)
    else:
      for key in app:
        if key in bstack111l1l1l_opy_:
          if key == bstack11l1lll1_opy_ (u"ࠫࡵࡧࡴࡩࠩ௾"):
            if os.path.exists(app[key]):
              bstack1l1ll111l_opy_ = bstack111ll11l_opy_(config, app[key])
            else:
              bstack1lll1l1l_opy_(bstack1111llll_opy_.format(app))
          else:
            bstack1l1ll111l_opy_ = app[key]
        else:
          bstack1lll1l1l_opy_(bstack1lll111l_opy_)
  return bstack1l1ll111l_opy_
def bstack1ll1ll1ll_opy_(bstack1l1ll111l_opy_):
  import re
  bstack1ll1lll1_opy_ = re.compile(bstack11l1lll1_opy_ (u"ࡷࠨ࡞࡜ࡣ࠰ࡾࡆ࠳࡚࠱࠯࠼ࡠࡤ࠴࡜࠮࡟࠭ࠨࠧ௿"))
  bstack1llllll_opy_ = re.compile(bstack11l1lll1_opy_ (u"ࡸࠢ࡟࡝ࡤ࠱ࡿࡇ࡛࠭࠲࠰࠽ࡡࡥ࠮࡝࠯ࡠ࠮࠴ࡡࡡ࠮ࡼࡄ࠱࡟࠶࠭࠺࡞ࡢ࠲ࡡ࠳࡝ࠫࠦࠥఀ"))
  if bstack11l1lll1_opy_ (u"ࠧࡣࡵ࠽࠳࠴࠭ఁ") in bstack1l1ll111l_opy_ or re.fullmatch(bstack1ll1lll1_opy_, bstack1l1ll111l_opy_) or re.fullmatch(bstack1llllll_opy_, bstack1l1ll111l_opy_):
    return True
  else:
    return False
def bstack111ll11l_opy_(config, path, bstack1ll111l11_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack11l1lll1_opy_ (u"ࠨࡴࡥࠫం")).read()).hexdigest()
  bstack11l11l_opy_ = bstack1lll1l1l1_opy_(md5_hash)
  bstack1l1ll111l_opy_ = None
  if bstack11l11l_opy_:
    logger.info(bstack1ll1l11_opy_.format(bstack11l11l_opy_, md5_hash))
    return bstack11l11l_opy_
  bstack1l1l1llll_opy_ = MultipartEncoder(
    fields={
        bstack11l1lll1_opy_ (u"ࠩࡩ࡭ࡱ࡫ࠧః"): (os.path.basename(path), open(os.path.abspath(path), bstack11l1lll1_opy_ (u"ࠪࡶࡧ࠭ఄ")), bstack11l1lll1_opy_ (u"ࠫࡹ࡫ࡸࡵ࠱ࡳࡰࡦ࡯࡮ࠨఅ")),
        bstack11l1lll1_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡤ࡯ࡤࠨఆ"): bstack1ll111l11_opy_
    }
  )
  response = requests.post(bstack1l1lll111_opy_, data=bstack1l1l1llll_opy_,
                         headers={bstack11l1lll1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬఇ"): bstack1l1l1llll_opy_.content_type}, auth=(config[bstack11l1lll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩఈ")], config[bstack11l1lll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫఉ")]))
  try:
    res = json.loads(response.text)
    bstack1l1ll111l_opy_ = res[bstack11l1lll1_opy_ (u"ࠩࡤࡴࡵࡥࡵࡳ࡮ࠪఊ")]
    logger.info(bstack11l11lll1_opy_.format(bstack1l1ll111l_opy_))
    bstack1ll1l1_opy_(md5_hash, bstack1l1ll111l_opy_)
  except ValueError as err:
    bstack1lll1l1l_opy_(bstack1l11ll1l_opy_.format(str(err)))
  return bstack1l1ll111l_opy_
def bstack1llll11ll_opy_():
  global CONFIG
  global bstack1111lll1_opy_
  bstack1l1l1_opy_ = 0
  bstack1l11l1ll_opy_ = 1
  if bstack11l1lll1_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪఋ") in CONFIG:
    bstack1l11l1ll_opy_ = CONFIG[bstack11l1lll1_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫఌ")]
  if bstack11l1lll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ఍") in CONFIG:
    bstack1l1l1_opy_ = len(CONFIG[bstack11l1lll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩఎ")])
  bstack1111lll1_opy_ = int(bstack1l11l1ll_opy_) * int(bstack1l1l1_opy_)
def bstack1lll1l1l1_opy_(md5_hash):
  bstack111ll1lll_opy_ = os.path.join(os.path.expanduser(bstack11l1lll1_opy_ (u"ࠧࡿࠩఏ")), bstack11l1lll1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨఐ"), bstack11l1lll1_opy_ (u"ࠩࡤࡴࡵ࡛ࡰ࡭ࡱࡤࡨࡒࡊ࠵ࡉࡣࡶ࡬࠳ࡰࡳࡰࡰࠪ఑"))
  if os.path.exists(bstack111ll1lll_opy_):
    bstack1l_opy_ = json.load(open(bstack111ll1lll_opy_,bstack11l1lll1_opy_ (u"ࠪࡶࡧ࠭ఒ")))
    if md5_hash in bstack1l_opy_:
      bstack1ll111ll_opy_ = bstack1l_opy_[md5_hash]
      bstack1lll11_opy_ = datetime.datetime.now()
      bstack11l1lllll_opy_ = datetime.datetime.strptime(bstack1ll111ll_opy_[bstack11l1lll1_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧఓ")], bstack11l1lll1_opy_ (u"ࠬࠫࡤ࠰ࠧࡰ࠳ࠪ࡟ࠠࠦࡊ࠽ࠩࡒࡀࠥࡔࠩఔ"))
      if (bstack1lll11_opy_ - bstack11l1lllll_opy_).days > 60:
        return None
      elif version.parse(str(__version__)) > version.parse(bstack1ll111ll_opy_[bstack11l1lll1_opy_ (u"࠭ࡳࡥ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠫక")]):
        return None
      return bstack1ll111ll_opy_[bstack11l1lll1_opy_ (u"ࠧࡪࡦࠪఖ")]
  else:
    return None
def bstack1ll1l1_opy_(md5_hash, bstack1l1ll111l_opy_):
  bstack1l11l111l_opy_ = os.path.join(os.path.expanduser(bstack11l1lll1_opy_ (u"ࠨࢀࠪగ")), bstack11l1lll1_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩఘ"))
  if not os.path.exists(bstack1l11l111l_opy_):
    os.makedirs(bstack1l11l111l_opy_)
  bstack111ll1lll_opy_ = os.path.join(os.path.expanduser(bstack11l1lll1_opy_ (u"ࠪࢂࠬఙ")), bstack11l1lll1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫచ"), bstack11l1lll1_opy_ (u"ࠬࡧࡰࡱࡗࡳࡰࡴࡧࡤࡎࡆ࠸ࡌࡦࡹࡨ࠯࡬ࡶࡳࡳ࠭ఛ"))
  bstack111l1ll1l_opy_ = {
    bstack11l1lll1_opy_ (u"࠭ࡩࡥࠩజ"): bstack1l1ll111l_opy_,
    bstack11l1lll1_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪఝ"): datetime.datetime.strftime(datetime.datetime.now(), bstack11l1lll1_opy_ (u"ࠨࠧࡧ࠳ࠪࡳ࠯࡛ࠦࠣࠩࡍࡀࠥࡎ࠼ࠨࡗࠬఞ")),
    bstack11l1lll1_opy_ (u"ࠩࡶࡨࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠧట"): str(__version__)
  }
  if os.path.exists(bstack111ll1lll_opy_):
    bstack1l_opy_ = json.load(open(bstack111ll1lll_opy_,bstack11l1lll1_opy_ (u"ࠪࡶࡧ࠭ఠ")))
  else:
    bstack1l_opy_ = {}
  bstack1l_opy_[md5_hash] = bstack111l1ll1l_opy_
  with open(bstack111ll1lll_opy_, bstack11l1lll1_opy_ (u"ࠦࡼ࠱ࠢడ")) as outfile:
    json.dump(bstack1l_opy_, outfile)
def bstack1l11lll_opy_(self):
  return
def bstack1ll1lll1l_opy_(self):
  return
def bstack11l11_opy_(self):
  from selenium.webdriver.remote.webdriver import WebDriver
  WebDriver.quit(self)
def bstack1l111llll_opy_(self):
  global bstack1l11l1lll_opy_
  global bstack1ll11ll1_opy_
  global bstack1lll_opy_
  try:
    if bstack11l1lll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬఢ") in bstack1l11l1lll_opy_ and self.session_id != None:
      bstack1l1l111l1_opy_ = bstack11l1lll1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ణ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack11l1lll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧత")
      bstack1l1ll_opy_ = bstack111l111l_opy_(bstack11l1lll1_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫథ"), bstack11l1lll1_opy_ (u"ࠩࠪద"), bstack1l1l111l1_opy_, bstack11l1lll1_opy_ (u"ࠪ࠰ࠥ࠭ధ").join(threading.current_thread().bstackTestErrorMessages), bstack11l1lll1_opy_ (u"ࠫࠬన"), bstack11l1lll1_opy_ (u"ࠬ࠭఩"))
      if self != None:
        self.execute_script(bstack1l1ll_opy_)
  except Exception as e:
    logger.debug(bstack11l1lll1_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡲࡧࡲ࡬࡫ࡱ࡫ࠥࡹࡴࡢࡶࡸࡷ࠿ࠦࠢప") + str(e))
  bstack1lll_opy_(self)
  self.session_id = None
def bstack1ll11l111_opy_(self, command_executor,
        desired_capabilities=None, browser_profile=None, proxy=None,
        keep_alive=True, file_detector=None, options=None):
  global CONFIG
  global bstack1ll11ll1_opy_
  global bstack11llll1l_opy_
  global bstack1l1lll1ll_opy_
  global bstack11l1l11ll_opy_
  global bstack1l1l1ll_opy_
  global bstack1l11l1lll_opy_
  global bstack1l1l1l11l_opy_
  global bstack11llll11l_opy_
  global bstack11lll111_opy_
  CONFIG[bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩఫ")] = str(bstack1l11l1lll_opy_) + str(__version__)
  command_executor = bstack1l1l111ll_opy_()
  logger.debug(bstack1111111l_opy_.format(command_executor))
  proxy = bstack1l1l1l1_opy_(CONFIG, proxy)
  bstack111llll1_opy_ = 0 if bstack11llll1l_opy_ < 0 else bstack11llll1l_opy_
  try:
    if bstack11l1l11ll_opy_ is True:
      bstack111llll1_opy_ = int(multiprocessing.current_process().name)
    elif bstack1l1l1ll_opy_ is True:
      bstack111llll1_opy_ = int(threading.current_thread().name)
  except:
    bstack111llll1_opy_ = 0
  bstack111l1ll1_opy_ = bstack111111_opy_(CONFIG, bstack111llll1_opy_)
  logger.debug(bstack11ll11ll1_opy_.format(str(bstack111l1ll1_opy_)))
  if bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬబ") in CONFIG and CONFIG[bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭భ")]:
    bstack11ll11ll_opy_(bstack111l1ll1_opy_)
  if desired_capabilities:
    bstack1l1l1l1l_opy_ = bstack111lllll_opy_(desired_capabilities)
    bstack1l1l1l1l_opy_[bstack11l1lll1_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪమ")] = bstack111llll_opy_(CONFIG)
    bstack11111111_opy_ = bstack111111_opy_(bstack1l1l1l1l_opy_)
    if bstack11111111_opy_:
      bstack111l1ll1_opy_ = update(bstack11111111_opy_, bstack111l1ll1_opy_)
    desired_capabilities = None
  if options:
    bstack11ll11l1_opy_(options, bstack111l1ll1_opy_)
  if not options:
    options = bstack1l1ll1111_opy_(bstack111l1ll1_opy_)
  if proxy and bstack1111lllll_opy_() >= version.parse(bstack11l1lll1_opy_ (u"ࠫ࠹࠴࠱࠱࠰࠳ࠫయ")):
    options.proxy(proxy)
  if options and bstack1111lllll_opy_() >= version.parse(bstack11l1lll1_opy_ (u"ࠬ࠹࠮࠹࠰࠳ࠫర")):
    desired_capabilities = None
  if (
      not options and not desired_capabilities
  ) or (
      bstack1111lllll_opy_() < version.parse(bstack11l1lll1_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬఱ")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack111l1ll1_opy_)
  logger.info(bstack1lll1lll_opy_)
  if bstack1111lllll_opy_() >= version.parse(bstack11l1lll1_opy_ (u"ࠧ࠵࠰࠴࠴࠳࠶ࠧల")):
    bstack1l1l1l11l_opy_(self, command_executor=command_executor,
          options=options, keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1111lllll_opy_() >= version.parse(bstack11l1lll1_opy_ (u"ࠨ࠵࠱࠼࠳࠶ࠧళ")):
    bstack1l1l1l11l_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities, options=options,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1111lllll_opy_() >= version.parse(bstack11l1lll1_opy_ (u"ࠩ࠵࠲࠺࠹࠮࠱ࠩఴ")):
    bstack1l1l1l11l_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive, file_detector=file_detector)
  else:
    bstack1l1l1l11l_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive)
  try:
    bstack1ll1ll1l1_opy_ = bstack11l1lll1_opy_ (u"ࠪࠫవ")
    if bstack1111lllll_opy_() >= version.parse(bstack11l1lll1_opy_ (u"ࠫ࠹࠴࠰࠯࠲ࡥ࠵ࠬశ")):
      bstack1ll1ll1l1_opy_ = self.caps.get(bstack11l1lll1_opy_ (u"ࠧࡵࡰࡵ࡫ࡰࡥࡱࡎࡵࡣࡗࡵࡰࠧష"))
    else:
      bstack1ll1ll1l1_opy_ = self.capabilities.get(bstack11l1lll1_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡱࡦࡲࡈࡶࡤࡘࡶࡱࠨస"))
    if bstack1ll1ll1l1_opy_:
      if bstack1111lllll_opy_() <= version.parse(bstack11l1lll1_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧహ")):
        self.command_executor._url = bstack11l1lll1_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤ఺") + bstack1lllll111_opy_ + bstack11l1lll1_opy_ (u"ࠤ࠽࠼࠵࠵ࡷࡥ࠱࡫ࡹࡧࠨ఻")
      else:
        self.command_executor._url = bstack11l1lll1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳఼ࠧ") + bstack1ll1ll1l1_opy_ + bstack11l1lll1_opy_ (u"ࠦ࠴ࡽࡤ࠰ࡪࡸࡦࠧఽ")
      logger.debug(bstack1l1111lll_opy_.format(bstack1ll1ll1l1_opy_))
    else:
      logger.debug(bstack11l1llll1_opy_.format(bstack11l1lll1_opy_ (u"ࠧࡕࡰࡵ࡫ࡰࡥࡱࠦࡈࡶࡤࠣࡲࡴࡺࠠࡧࡱࡸࡲࡩࠨా")))
  except Exception as e:
    logger.debug(bstack11l1llll1_opy_.format(e))
  if bstack11l1lll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬి") in bstack1l11l1lll_opy_:
    bstack11lll111l_opy_(bstack11llll1l_opy_, bstack11lll111_opy_)
  bstack1ll11ll1_opy_ = self.session_id
  if bstack11l1lll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧీ") in bstack1l11l1lll_opy_ or bstack11l1lll1_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨు") in bstack1l11l1lll_opy_:
    threading.current_thread().bstack11111l11_opy_ = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
  bstack11llll11l_opy_.append(self)
  if bstack11l1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬూ") in CONFIG and bstack11l1lll1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨృ") in CONFIG[bstack11l1lll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧౄ")][bstack111llll1_opy_]:
    bstack1l1lll1ll_opy_ = CONFIG[bstack11l1lll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ౅")][bstack111llll1_opy_][bstack11l1lll1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫె")]
  logger.debug(bstack1l111l111_opy_.format(bstack1ll11ll1_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    def bstack1ll11llll_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack11ll1_opy_
      if(bstack11l1lll1_opy_ (u"ࠢࡪࡰࡧࡩࡽ࠴ࡪࡴࠤే") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack11l1lll1_opy_ (u"ࠨࢀࠪై")), bstack11l1lll1_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ౉"), bstack11l1lll1_opy_ (u"ࠪ࠲ࡸ࡫ࡳࡴ࡫ࡲࡲ࡮ࡪࡳ࠯ࡶࡻࡸࠬొ")), bstack11l1lll1_opy_ (u"ࠫࡼ࠭ో")) as fp:
          fp.write(bstack11l1lll1_opy_ (u"ࠧࠨౌ"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack11l1lll1_opy_ (u"ࠨࡩ࡯ࡦࡨࡼࡤࡨࡳࡵࡣࡦ࡯࠳ࡰࡳ్ࠣ")))):
          with open(args[1], bstack11l1lll1_opy_ (u"ࠧࡳࠩ౎")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack11l1lll1_opy_ (u"ࠨࡣࡶࡽࡳࡩࠠࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࡢࡲࡪࡽࡐࡢࡩࡨࠬࡨࡵ࡮ࡵࡧࡻࡸ࠱ࠦࡰࡢࡩࡨࠤࡂࠦࡶࡰ࡫ࡧࠤ࠵࠯ࠧ౏") in line), None)
            if index is not None:
                lines.insert(index+2, bstack1l1lll11_opy_)
            lines.insert(1, bstack1l11l11l1_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack11l1lll1_opy_ (u"ࠤ࡬ࡲࡩ࡫ࡸࡠࡤࡶࡸࡦࡩ࡫࠯࡬ࡶࠦ౐")), bstack11l1lll1_opy_ (u"ࠪࡻࠬ౑")) as bstack1l111_opy_:
              bstack1l111_opy_.writelines(lines)
        CONFIG[bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭౒")] = str(bstack1l11l1lll_opy_) + str(__version__)
        bstack111llll1_opy_ = 0 if bstack11llll1l_opy_ < 0 else bstack11llll1l_opy_
        try:
          if bstack11l1l11ll_opy_ is True:
            bstack111llll1_opy_ = int(multiprocessing.current_process().name)
          elif bstack1l1l1ll_opy_ is True:
            bstack111llll1_opy_ = int(threading.current_thread().name)
        except:
          bstack111llll1_opy_ = 0
        CONFIG[bstack11l1lll1_opy_ (u"ࠧࡻࡳࡦ࡙࠶ࡇࠧ౓")] = False
        CONFIG[bstack11l1lll1_opy_ (u"ࠨࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠧ౔")] = True
        bstack111l1ll1_opy_ = bstack111111_opy_(CONFIG, bstack111llll1_opy_)
        logger.debug(bstack11ll11ll1_opy_.format(str(bstack111l1ll1_opy_)))
        if CONFIG[bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ౕࠫ")]:
          bstack11ll11ll_opy_(bstack111l1ll1_opy_)
        if bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶౖࠫ") in CONFIG and bstack11l1lll1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ౗") in CONFIG[bstack11l1lll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ౘ")][bstack111llll1_opy_]:
          bstack1l1lll1ll_opy_ = CONFIG[bstack11l1lll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧౙ")][bstack111llll1_opy_][bstack11l1lll1_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪౚ")]
        args.append(os.path.join(os.path.expanduser(bstack11l1lll1_opy_ (u"࠭ࡾࠨ౛")), bstack11l1lll1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ౜"), bstack11l1lll1_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪౝ")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack111l1ll1_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack11l1lll1_opy_ (u"ࠤ࡬ࡲࡩ࡫ࡸࡠࡤࡶࡸࡦࡩ࡫࠯࡬ࡶࠦ౞"))
      bstack11ll1_opy_ = True
      return bstack11l111ll_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    pass
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack1l1111ll1_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack1ll11ll1_opy_
    global bstack11llll1l_opy_
    global bstack1l1lll1ll_opy_
    global bstack11l1l11ll_opy_
    global bstack1l1l1ll_opy_
    global bstack1l11l1lll_opy_
    global bstack1l1l1l11l_opy_
    CONFIG[bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬ౟")] = str(bstack1l11l1lll_opy_) + str(__version__)
    bstack111llll1_opy_ = 0 if bstack11llll1l_opy_ < 0 else bstack11llll1l_opy_
    try:
      if bstack11l1l11ll_opy_ is True:
        bstack111llll1_opy_ = int(multiprocessing.current_process().name)
      elif bstack1l1l1ll_opy_ is True:
        bstack111llll1_opy_ = int(threading.current_thread().name)
    except:
      bstack111llll1_opy_ = 0
    CONFIG[bstack11l1lll1_opy_ (u"ࠦ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥౠ")] = True
    bstack111l1ll1_opy_ = bstack111111_opy_(CONFIG, bstack111llll1_opy_)
    logger.debug(bstack11ll11ll1_opy_.format(str(bstack111l1ll1_opy_)))
    if CONFIG[bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩౡ")]:
      bstack11ll11ll_opy_(bstack111l1ll1_opy_)
    if bstack11l1lll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩౢ") in CONFIG and bstack11l1lll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬౣ") in CONFIG[bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ౤")][bstack111llll1_opy_]:
      bstack1l1lll1ll_opy_ = CONFIG[bstack11l1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ౥")][bstack111llll1_opy_][bstack11l1lll1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ౦")]
    import urllib
    import json
    bstack1l11111ll_opy_ = bstack11l1lll1_opy_ (u"ࠫࡼࡹࡳ࠻࠱࠲ࡧࡩࡶ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠿ࡤࡣࡳࡷࡂ࠭౧") + urllib.parse.quote(json.dumps(bstack111l1ll1_opy_))
    browser = self.connect(bstack1l11111ll_opy_)
    return browser
except Exception as e:
    pass
def bstack1ll11l11l_opy_():
    global bstack11ll1_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        BrowserType.launch = bstack1l1111ll1_opy_
        bstack11ll1_opy_ = True
    except Exception as e:
        pass
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack1ll11llll_opy_
      bstack11ll1_opy_ = True
    except Exception as e:
      pass
def bstack11ll111_opy_(context, bstack111l1l1ll_opy_):
  try:
    context.page.evaluate(bstack11l1lll1_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨ౨"), bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠪ౩")+ json.dumps(bstack111l1l1ll_opy_) + bstack11l1lll1_opy_ (u"ࠢࡾࡿࠥ౪"))
  except Exception as e:
    logger.debug(bstack11l1lll1_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣࡿࢂࠨ౫"), e)
def bstack1lll11lll_opy_(context, message, level):
  try:
    context.page.evaluate(bstack11l1lll1_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥ౬"), bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨ౭") + json.dumps(message) + bstack11l1lll1_opy_ (u"ࠫ࠱ࠨ࡬ࡦࡸࡨࡰࠧࡀࠧ౮") + json.dumps(level) + bstack11l1lll1_opy_ (u"ࠬࢃࡽࠨ౯"))
  except Exception as e:
    logger.debug(bstack11l1lll1_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡤࡲࡳࡵࡴࡢࡶ࡬ࡳࡳࠦࡻࡾࠤ౰"), e)
def bstack111l111ll_opy_(context, status, message = bstack11l1lll1_opy_ (u"ࠢࠣ౱")):
  try:
    if(status == bstack11l1lll1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ౲")):
      context.page.evaluate(bstack11l1lll1_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥ౳"), bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡵࡩࡦࡹ࡯࡯ࠤ࠽ࠫ౴") + json.dumps(bstack11l1lll1_opy_ (u"ࠦࡘࡩࡥ࡯ࡣࡵ࡭ࡴࠦࡦࡢ࡫࡯ࡩࡩࠦࡷࡪࡶ࡫࠾ࠥࠨ౵") + str(message)) + bstack11l1lll1_opy_ (u"ࠬ࠲ࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠩ౶") + json.dumps(status) + bstack11l1lll1_opy_ (u"ࠨࡽࡾࠤ౷"))
    else:
      context.page.evaluate(bstack11l1lll1_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ౸"), bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠩ౹") + json.dumps(status) + bstack11l1lll1_opy_ (u"ࠤࢀࢁࠧ౺"))
  except Exception as e:
    logger.debug(bstack11l1lll1_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡸࡺࡡࡵࡷࡶࠤࢀࢃࠢ౻"), e)
def bstack11l1ll1ll_opy_(self, url):
  global bstack11l1111ll_opy_
  try:
    bstack1lll11ll1_opy_(url)
  except Exception as err:
    logger.debug(bstack1l1ll1l11_opy_.format(str(err)))
  try:
    bstack11l1111ll_opy_(self, url)
  except Exception as e:
    try:
      bstack1l1ll1l_opy_ = str(e)
      if any(err_msg in bstack1l1ll1l_opy_ for err_msg in bstack1ll11l1l_opy_):
        bstack1lll11ll1_opy_(url, True)
    except Exception as err:
      logger.debug(bstack1l1ll1l11_opy_.format(str(err)))
    raise e
def bstack1ll1l111_opy_(self):
  global bstack1ll1l1l1_opy_
  bstack1ll1l1l1_opy_ = self
  return
def bstack1l1ll11ll_opy_(self):
  global bstack11ll1lll1_opy_
  bstack11ll1lll1_opy_ = self
  return
def bstack111ll1l_opy_(self, test):
  global CONFIG
  global bstack11ll1lll1_opy_
  global bstack1ll1l1l1_opy_
  global bstack1ll11ll1_opy_
  global bstack11l11lll_opy_
  global bstack1l1lll1ll_opy_
  global bstack11_opy_
  global bstack11ll1ll_opy_
  global bstack1l1111l_opy_
  global bstack11llll11l_opy_
  try:
    if not bstack1ll11ll1_opy_:
      with open(os.path.join(os.path.expanduser(bstack11l1lll1_opy_ (u"ࠫࢃ࠭౼")), bstack11l1lll1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ౽"), bstack11l1lll1_opy_ (u"࠭࠮ࡴࡧࡶࡷ࡮ࡵ࡮ࡪࡦࡶ࠲ࡹࡾࡴࠨ౾"))) as f:
        bstack1l1111_opy_ = json.loads(bstack11l1lll1_opy_ (u"ࠢࡼࠤ౿") + f.read().strip() + bstack11l1lll1_opy_ (u"ࠨࠤࡻࠦ࠿ࠦࠢࡺࠤࠪಀ") + bstack11l1lll1_opy_ (u"ࠤࢀࠦಁ"))
        bstack1ll11ll1_opy_ = bstack1l1111_opy_[str(threading.get_ident())]
  except:
    pass
  if bstack11llll11l_opy_:
    for driver in bstack11llll11l_opy_:
      if bstack1ll11ll1_opy_ == driver.session_id:
        if test:
          bstack1ll11l_opy_ = str(test.data)
        if not bstack1ll11l1ll_opy_ and bstack1ll11l_opy_:
          bstack111ll1ll1_opy_ = {
            bstack11l1lll1_opy_ (u"ࠪࡥࡨࡺࡩࡰࡰࠪಂ"): bstack11l1lll1_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬಃ"),
            bstack11l1lll1_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨ಄"): {
              bstack11l1lll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫಅ"): bstack1ll11l_opy_
            }
          }
          bstack111l111_opy_ = bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬಆ").format(json.dumps(bstack111ll1ll1_opy_))
          driver.execute_script(bstack111l111_opy_)
        if bstack11l11lll_opy_:
          bstack11lll1_opy_ = {
            bstack11l1lll1_opy_ (u"ࠨࡣࡦࡸ࡮ࡵ࡮ࠨಇ"): bstack11l1lll1_opy_ (u"ࠩࡤࡲࡳࡵࡴࡢࡶࡨࠫಈ"),
            bstack11l1lll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ಉ"): {
              bstack11l1lll1_opy_ (u"ࠫࡩࡧࡴࡢࠩಊ"): bstack1ll11l_opy_ + bstack11l1lll1_opy_ (u"ࠬࠦࡰࡢࡵࡶࡩࡩࠧࠧಋ"),
              bstack11l1lll1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬಌ"): bstack11l1lll1_opy_ (u"ࠧࡪࡰࡩࡳࠬ಍")
            }
          }
          bstack111ll1ll1_opy_ = {
            bstack11l1lll1_opy_ (u"ࠨࡣࡦࡸ࡮ࡵ࡮ࠨಎ"): bstack11l1lll1_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬಏ"),
            bstack11l1lll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ಐ"): {
              bstack11l1lll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ಑"): bstack11l1lll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬಒ")
            }
          }
          if bstack11l11lll_opy_.status == bstack11l1lll1_opy_ (u"࠭ࡐࡂࡕࡖࠫಓ"):
            bstack1l1l1l11_opy_ = bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬಔ").format(json.dumps(bstack11lll1_opy_))
            driver.execute_script(bstack1l1l1l11_opy_)
            bstack111l111_opy_ = bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭ಕ").format(json.dumps(bstack111ll1ll1_opy_))
            driver.execute_script(bstack111l111_opy_)
          elif bstack11l11lll_opy_.status == bstack11l1lll1_opy_ (u"ࠩࡉࡅࡎࡒࠧಖ"):
            reason = bstack11l1lll1_opy_ (u"ࠥࠦಗ")
            bstack111l1l_opy_ = bstack1ll11l_opy_ + bstack11l1lll1_opy_ (u"ࠫࠥ࡬ࡡࡪ࡮ࡨࡨࠬಘ")
            if bstack11l11lll_opy_.message:
              reason = str(bstack11l11lll_opy_.message)
              bstack111l1l_opy_ = bstack111l1l_opy_ + bstack11l1lll1_opy_ (u"ࠬࠦࡷࡪࡶ࡫ࠤࡪࡸࡲࡰࡴ࠽ࠤࠬಙ") + reason
            bstack11lll1_opy_[bstack11l1lll1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩಚ")] = {
              bstack11l1lll1_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ಛ"): bstack11l1lll1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧಜ"),
              bstack11l1lll1_opy_ (u"ࠩࡧࡥࡹࡧࠧಝ"): bstack111l1l_opy_
            }
            bstack111ll1ll1_opy_[bstack11l1lll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ಞ")] = {
              bstack11l1lll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫಟ"): bstack11l1lll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬಠ"),
              bstack11l1lll1_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭ಡ"): reason
            }
            bstack1l1l1l11_opy_ = bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬಢ").format(json.dumps(bstack11lll1_opy_))
            driver.execute_script(bstack1l1l1l11_opy_)
            bstack111l111_opy_ = bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭ಣ").format(json.dumps(bstack111ll1ll1_opy_))
            driver.execute_script(bstack111l111_opy_)
  elif bstack1ll11ll1_opy_:
    try:
      data = {}
      bstack1ll11l_opy_ = None
      if test:
        bstack1ll11l_opy_ = str(test.data)
      if not bstack1ll11l1ll_opy_ and bstack1ll11l_opy_:
        data[bstack11l1lll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧತ")] = bstack1ll11l_opy_
      if bstack11l11lll_opy_:
        if bstack11l11lll_opy_.status == bstack11l1lll1_opy_ (u"ࠪࡔࡆ࡙ࡓࠨಥ"):
          data[bstack11l1lll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫದ")] = bstack11l1lll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬಧ")
        elif bstack11l11lll_opy_.status == bstack11l1lll1_opy_ (u"࠭ࡆࡂࡋࡏࠫನ"):
          data[bstack11l1lll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ಩")] = bstack11l1lll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨಪ")
          if bstack11l11lll_opy_.message:
            data[bstack11l1lll1_opy_ (u"ࠩࡵࡩࡦࡹ࡯࡯ࠩಫ")] = str(bstack11l11lll_opy_.message)
      user = CONFIG[bstack11l1lll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬಬ")]
      key = CONFIG[bstack11l1lll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧಭ")]
      url = bstack11l1lll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡻࡾ࠼ࡾࢁࡅࡧࡰࡪ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱ࠴ࡧࡵࡵࡱࡰࡥࡹ࡫࠯ࡴࡧࡶࡷ࡮ࡵ࡮ࡴ࠱ࡾࢁ࠳ࡰࡳࡰࡰࠪಮ").format(user, key, bstack1ll11ll1_opy_)
      headers = {
        bstack11l1lll1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡵࡻࡳࡩࠬಯ"): bstack11l1lll1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪರ"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers)
    except Exception as e:
      logger.error(bstack1lllllll1_opy_.format(str(e)))
  if bstack11ll1lll1_opy_:
    bstack11ll1ll_opy_(bstack11ll1lll1_opy_)
  if bstack1ll1l1l1_opy_:
    bstack1l1111l_opy_(bstack1ll1l1l1_opy_)
  bstack11_opy_(self, test)
def bstack111l11l1_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack1l111l_opy_
  bstack1l111l_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack11l11lll_opy_
  bstack11l11lll_opy_ = self._test
def bstack1llll1l11_opy_():
  global bstack1ll1lll_opy_
  try:
    if os.path.exists(bstack1ll1lll_opy_):
      os.remove(bstack1ll1lll_opy_)
  except Exception as e:
    logger.debug(bstack11l1lll1_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡨࡪࡲࡥࡵ࡫ࡱ࡫ࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠤ࡫࡯࡬ࡦ࠼ࠣࠫಱ") + str(e))
def bstack1llll1ll1_opy_():
  global bstack1ll1lll_opy_
  bstack1ll1l11l_opy_ = {}
  try:
    if not os.path.isfile(bstack1ll1lll_opy_):
      with open(bstack1ll1lll_opy_, bstack11l1lll1_opy_ (u"ࠩࡺࠫಲ")):
        pass
      with open(bstack1ll1lll_opy_, bstack11l1lll1_opy_ (u"ࠥࡻ࠰ࠨಳ")) as outfile:
        json.dump({}, outfile)
    if os.path.exists(bstack1ll1lll_opy_):
      bstack1ll1l11l_opy_ = json.load(open(bstack1ll1lll_opy_, bstack11l1lll1_opy_ (u"ࠫࡷࡨࠧ಴")))
  except Exception as e:
    logger.debug(bstack11l1lll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡳࡧࡤࡨ࡮ࡴࡧࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧವ") + str(e))
  finally:
    return bstack1ll1l11l_opy_
def bstack11lll111l_opy_(platform_index, item_index):
  global bstack1ll1lll_opy_
  try:
    bstack1ll1l11l_opy_ = bstack1llll1ll1_opy_()
    bstack1ll1l11l_opy_[item_index] = platform_index
    with open(bstack1ll1lll_opy_, bstack11l1lll1_opy_ (u"ࠨࡷࠬࠤಶ")) as outfile:
      json.dump(bstack1ll1l11l_opy_, outfile)
  except Exception as e:
    logger.debug(bstack11l1lll1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡺࡶ࡮ࡺࡩ࡯ࡩࠣࡸࡴࠦࡲࡰࡤࡲࡸࠥࡸࡥࡱࡱࡵࡸࠥ࡬ࡩ࡭ࡧ࠽ࠤࠬಷ") + str(e))
def bstack1ll11ll1l_opy_(bstack1l111l1ll_opy_):
  global CONFIG
  bstack1lllll_opy_ = bstack11l1lll1_opy_ (u"ࠨࠩಸ")
  if not bstack11l1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬಹ") in CONFIG:
    logger.info(bstack11l1lll1_opy_ (u"ࠪࡒࡴࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠢࡳࡥࡸࡹࡥࡥࠢࡸࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡭ࡥ࡯ࡧࡵࡥࡹ࡫ࠠࡳࡧࡳࡳࡷࡺࠠࡧࡱࡵࠤࡗࡵࡢࡰࡶࠣࡶࡺࡴࠧ಺"))
  try:
    platform = CONFIG[bstack11l1lll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ಻")][bstack1l111l1ll_opy_]
    if bstack11l1lll1_opy_ (u"ࠬࡵࡳࠨ಼") in platform:
      bstack1lllll_opy_ += str(platform[bstack11l1lll1_opy_ (u"࠭࡯ࡴࠩಽ")]) + bstack11l1lll1_opy_ (u"ࠧ࠭ࠢࠪಾ")
    if bstack11l1lll1_opy_ (u"ࠨࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠫಿ") in platform:
      bstack1lllll_opy_ += str(platform[bstack11l1lll1_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬೀ")]) + bstack11l1lll1_opy_ (u"ࠪ࠰ࠥ࠭ು")
    if bstack11l1lll1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨೂ") in platform:
      bstack1lllll_opy_ += str(platform[bstack11l1lll1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠩೃ")]) + bstack11l1lll1_opy_ (u"࠭ࠬࠡࠩೄ")
    if bstack11l1lll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩ೅") in platform:
      bstack1lllll_opy_ += str(platform[bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠪೆ")]) + bstack11l1lll1_opy_ (u"ࠩ࠯ࠤࠬೇ")
    if bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨೈ") in platform:
      bstack1lllll_opy_ += str(platform[bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩ೉")]) + bstack11l1lll1_opy_ (u"ࠬ࠲ࠠࠨೊ")
    if bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧೋ") in platform:
      bstack1lllll_opy_ += str(platform[bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨೌ")]) + bstack11l1lll1_opy_ (u"ࠨ࠮್ࠣࠫ")
  except Exception as e:
    logger.debug(bstack11l1lll1_opy_ (u"ࠩࡖࡳࡲ࡫ࠠࡦࡴࡵࡳࡷࠦࡩ࡯ࠢࡪࡩࡳ࡫ࡲࡢࡶ࡬ࡲ࡬ࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠡࡵࡷࡶ࡮ࡴࡧࠡࡨࡲࡶࠥࡸࡥࡱࡱࡵࡸࠥ࡭ࡥ࡯ࡧࡵࡥࡹ࡯࡯࡯ࠩ೎") + str(e))
  finally:
    if bstack1lllll_opy_[len(bstack1lllll_opy_) - 2:] == bstack11l1lll1_opy_ (u"ࠪ࠰ࠥ࠭೏"):
      bstack1lllll_opy_ = bstack1lllll_opy_[:-2]
    return bstack1lllll_opy_
def bstack1llllllll_opy_(path, bstack1lllll_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack1lll11l11_opy_ = ET.parse(path)
    bstack1llll1l1l_opy_ = bstack1lll11l11_opy_.getroot()
    bstack1l11ll_opy_ = None
    for suite in bstack1llll1l1l_opy_.iter(bstack11l1lll1_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪ೐")):
      if bstack11l1lll1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬ೑") in suite.attrib:
        suite.attrib[bstack11l1lll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ೒")] += bstack11l1lll1_opy_ (u"ࠧࠡࠩ೓") + bstack1lllll_opy_
        bstack1l11ll_opy_ = suite
    bstack1111ll1_opy_ = None
    for robot in bstack1llll1l1l_opy_.iter(bstack11l1lll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ೔")):
      bstack1111ll1_opy_ = robot
    bstack1l1l1111_opy_ = len(bstack1111ll1_opy_.findall(bstack11l1lll1_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨೕ")))
    if bstack1l1l1111_opy_ == 1:
      bstack1111ll1_opy_.remove(bstack1111ll1_opy_.findall(bstack11l1lll1_opy_ (u"ࠪࡷࡺ࡯ࡴࡦࠩೖ"))[0])
      bstack1ll_opy_ = ET.Element(bstack11l1lll1_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪ೗"), attrib={bstack11l1lll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ೘"):bstack11l1lll1_opy_ (u"࠭ࡓࡶ࡫ࡷࡩࡸ࠭೙"), bstack11l1lll1_opy_ (u"ࠧࡪࡦࠪ೚"):bstack11l1lll1_opy_ (u"ࠨࡵ࠳ࠫ೛")})
      bstack1111ll1_opy_.insert(1, bstack1ll_opy_)
      bstack1llll111_opy_ = None
      for suite in bstack1111ll1_opy_.iter(bstack11l1lll1_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨ೜")):
        bstack1llll111_opy_ = suite
      bstack1llll111_opy_.append(bstack1l11ll_opy_)
      bstack1111l1l_opy_ = None
      for status in bstack1l11ll_opy_.iter(bstack11l1lll1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪೝ")):
        bstack1111l1l_opy_ = status
      bstack1llll111_opy_.append(bstack1111l1l_opy_)
    bstack1lll11l11_opy_.write(path)
  except Exception as e:
    logger.debug(bstack11l1lll1_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡰࡢࡴࡶ࡭ࡳ࡭ࠠࡸࡪ࡬ࡰࡪࠦࡧࡦࡰࡨࡶࡦࡺࡩ࡯ࡩࠣࡶࡴࡨ࡯ࡵࠢࡵࡩࡵࡵࡲࡵࠩೞ") + str(e))
def bstack111lllll1_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack111l11111_opy_
  global CONFIG
  if bstack11l1lll1_opy_ (u"ࠧࡶࡹࡵࡪࡲࡲࡵࡧࡴࡩࠤ೟") in options:
    del options[bstack11l1lll1_opy_ (u"ࠨࡰࡺࡶ࡫ࡳࡳࡶࡡࡵࡪࠥೠ")]
  bstack11ll1111_opy_ = bstack1llll1ll1_opy_()
  for bstack1l1ll11l_opy_ in bstack11ll1111_opy_.keys():
    path = os.path.join(os.getcwd(), bstack11l1lll1_opy_ (u"ࠧࡱࡣࡥࡳࡹࡥࡲࡦࡵࡸࡰࡹࡹࠧೡ"), str(bstack1l1ll11l_opy_), bstack11l1lll1_opy_ (u"ࠨࡱࡸࡸࡵࡻࡴ࠯ࡺࡰࡰࠬೢ"))
    bstack1llllllll_opy_(path, bstack1ll11ll1l_opy_(bstack11ll1111_opy_[bstack1l1ll11l_opy_]))
  bstack1llll1l11_opy_()
  return bstack111l11111_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack1l1l11111_opy_(self, ff_profile_dir):
  global bstack1ll111l_opy_
  if not ff_profile_dir:
    return None
  return bstack1ll111l_opy_(self, ff_profile_dir)
def bstack11l1111l1_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack1l11_opy_
  bstack11l111l_opy_ = []
  if bstack11l1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬೣ") in CONFIG:
    bstack11l111l_opy_ = CONFIG[bstack11l1lll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭೤")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack11l1lll1_opy_ (u"ࠦࡨࡵ࡭࡮ࡣࡱࡨࠧ೥")],
      pabot_args[bstack11l1lll1_opy_ (u"ࠧࡼࡥࡳࡤࡲࡷࡪࠨ೦")],
      argfile,
      pabot_args.get(bstack11l1lll1_opy_ (u"ࠨࡨࡪࡸࡨࠦ೧")),
      pabot_args[bstack11l1lll1_opy_ (u"ࠢࡱࡴࡲࡧࡪࡹࡳࡦࡵࠥ೨")],
      platform[0],
      bstack1l11_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack11l1lll1_opy_ (u"ࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡩ࡭ࡱ࡫ࡳࠣ೩")] or [(bstack11l1lll1_opy_ (u"ࠤࠥ೪"), None)]
    for platform in enumerate(bstack11l111l_opy_)
  ]
def bstack111l11ll_opy_(self, datasources, outs_dir, options,
  execution_item, command, verbose, argfile,
  hive=None, processes=0,platform_index=0,bstack11lllll11_opy_=bstack11l1lll1_opy_ (u"ࠪࠫ೫")):
  global bstackl_opy_
  self.platform_index = platform_index
  self.bstack1ll1ll1l_opy_ = bstack11lllll11_opy_
  bstackl_opy_(self, datasources, outs_dir, options,
    execution_item, command, verbose, argfile, hive, processes)
def bstack111l1ll11_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack11l111l11_opy_
  global bstack11l11l11_opy_
  if not bstack11l1lll1_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭೬") in item.options:
    item.options[bstack11l1lll1_opy_ (u"ࠬࡼࡡࡳ࡫ࡤࡦࡱ࡫ࠧ೭")] = []
  for v in item.options[bstack11l1lll1_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨ೮")]:
    if bstack11l1lll1_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡐࡍࡃࡗࡊࡔࡘࡍࡊࡐࡇࡉ࡝࠭೯") in v:
      item.options[bstack11l1lll1_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ೰")].remove(v)
    if bstack11l1lll1_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡅࡏࡍࡆࡘࡇࡔࠩೱ") in v:
      item.options[bstack11l1lll1_opy_ (u"ࠪࡺࡦࡸࡩࡢࡤ࡯ࡩࠬೲ")].remove(v)
  item.options[bstack11l1lll1_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭ೳ")].insert(0, bstack11l1lll1_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡕࡒࡁࡕࡈࡒࡖࡒࡏࡎࡅࡇ࡛࠾ࢀࢃࠧ೴").format(item.platform_index))
  item.options[bstack11l1lll1_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨ೵")].insert(0, bstack11l1lll1_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕ࠾ࢀࢃࠧ೶").format(item.bstack1ll1ll1l_opy_))
  if bstack11l11l11_opy_:
    item.options[bstack11l1lll1_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ೷")].insert(0, bstack11l1lll1_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡅࡏࡍࡆࡘࡇࡔ࠼ࡾࢁࠬ೸").format(bstack11l11l11_opy_))
  return bstack11l111l11_opy_(caller_id, datasources, is_last, item, outs_dir)
def bstack1lll111ll_opy_(command, item_index):
  global bstack11l11l11_opy_
  if bstack11l11l11_opy_:
    command[0] = command[0].replace(bstack11l1lll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ೹"), bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠰ࡷࡩࡱࠠࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠡ࠯࠰ࡦࡸࡺࡡࡤ࡭ࡢ࡭ࡹ࡫࡭ࡠ࡫ࡱࡨࡪࡾࠠࠨ೺") + str(item_index) + bstack11l1lll1_opy_ (u"ࠬࠦࠧ೻") + bstack11l11l11_opy_, 1)
  else:
    command[0] = command[0].replace(bstack11l1lll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ೼"), bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠳ࡳࡥ࡭ࠣࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠤ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡩࡵࡧࡰࡣ࡮ࡴࡤࡦࡺࠣࠫ೽") + str(item_index), 1)
def bstack11l1l1ll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack11l1l11l_opy_
  bstack1lll111ll_opy_(command, item_index)
  return bstack11l1l11l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
def bstack1l11l1l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack11l1l11l_opy_
  bstack1lll111ll_opy_(command, item_index)
  return bstack11l1l11l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
def bstack11llllll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack11l1l11l_opy_
  bstack1lll111ll_opy_(command, item_index)
  return bstack11l1l11l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
def bstack11l1ll1l_opy_(self, runner, quiet=False, capture=True):
  global bstack1ll1111l1_opy_
  bstack111l1l1l1_opy_ = bstack1ll1111l1_opy_(self, runner, quiet=False, capture=True)
  if self.exception:
    if not hasattr(runner, bstack11l1lll1_opy_ (u"ࠨࡧࡻࡧࡪࡶࡴࡪࡱࡱࡣࡦࡸࡲࠨ೾")):
      runner.exception_arr = []
    if not hasattr(runner, bstack11l1lll1_opy_ (u"ࠩࡨࡼࡨࡥࡴࡳࡣࡦࡩࡧࡧࡣ࡬ࡡࡤࡶࡷ࠭೿")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack111l1l1l1_opy_
def bstack1ll1l1ll_opy_(self, name, context, *args):
  global bstack11l1l11l1_opy_
  if name == bstack11l1lll1_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࡢࡪࡪࡧࡴࡶࡴࡨࠫഀ"):
    bstack11l1l11l1_opy_(self, name, context, *args)
    try:
      if(not bstack1ll11l1ll_opy_):
        bstack111l11ll1_opy_ = threading.current_thread().bstackSessionDriver if bstack1ll1ll111_opy_(bstack11l1lll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪഁ")) else context.browser
        bstack111l1l1ll_opy_ = str(self.feature.name)
        bstack11ll111_opy_(context, bstack111l1l1ll_opy_)
        bstack111l11ll1_opy_.execute_script(bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪം") + json.dumps(bstack111l1l1ll_opy_) + bstack11l1lll1_opy_ (u"࠭ࡽࡾࠩഃ"))
      self.driver_before_scenario = False
    except Exception as e:
      logger.debug(bstack11l1lll1_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡩ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡩࡩࡦࡺࡵࡳࡧ࠽ࠤࢀࢃࠧഄ").format(str(e)))
  elif name == bstack11l1lll1_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡵࡦࡩࡳࡧࡲࡪࡱࠪഅ"):
    bstack11l1l11l1_opy_(self, name, context, *args)
    try:
      if not hasattr(self, bstack11l1lll1_opy_ (u"ࠩࡧࡶ࡮ࡼࡥࡳࡡࡥࡩ࡫ࡵࡲࡦࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠫആ")):
        self.driver_before_scenario = True
      if(not bstack1ll11l1ll_opy_):
        scenario_name = args[0].name
        feature_name = bstack111l1l1ll_opy_ = str(self.feature.name)
        bstack111l1l1ll_opy_ = feature_name + bstack11l1lll1_opy_ (u"ࠪࠤ࠲ࠦࠧഇ") + scenario_name
        bstack111l11ll1_opy_ = threading.current_thread().bstackSessionDriver if bstack1ll1ll111_opy_(bstack11l1lll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪഈ")) else context.browser
        if self.driver_before_scenario:
          bstack11ll111_opy_(context, bstack111l1l1ll_opy_)
          bstack111l11ll1_opy_.execute_script(bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪഉ") + json.dumps(bstack111l1l1ll_opy_) + bstack11l1lll1_opy_ (u"࠭ࡽࡾࠩഊ"))
    except Exception as e:
      logger.debug(bstack11l1lll1_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡩ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡶࡧࡪࡴࡡࡳ࡫ࡲ࠾ࠥࢁࡽࠨഋ").format(str(e)))
  elif name == bstack11l1lll1_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠩഌ"):
    try:
      bstack1llll111l_opy_ = args[0].status.name
      bstack111l11ll1_opy_ = threading.current_thread().bstackSessionDriver if bstack11l1lll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨ഍") in threading.current_thread().__dict__.keys() else context.browser
      if str(bstack1llll111l_opy_).lower() == bstack11l1lll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪഎ"):
        bstack1l11l1ll1_opy_ = bstack11l1lll1_opy_ (u"ࠫࠬഏ")
        bstack111111l_opy_ = bstack11l1lll1_opy_ (u"ࠬ࠭ഐ")
        bstack11l11ll1_opy_ = bstack11l1lll1_opy_ (u"࠭ࠧ഑")
        try:
          import traceback
          bstack1l11l1ll1_opy_ = self.exception.__class__.__name__
          bstack1111ll1l_opy_ = traceback.format_tb(self.exc_traceback)
          bstack111111l_opy_ = bstack11l1lll1_opy_ (u"ࠧࠡࠩഒ").join(bstack1111ll1l_opy_)
          bstack11l11ll1_opy_ = bstack1111ll1l_opy_[-1]
        except Exception as e:
          logger.debug(bstack1lllll1l_opy_.format(str(e)))
        bstack1l11l1ll1_opy_ += bstack11l11ll1_opy_
        bstack1lll11lll_opy_(context, json.dumps(str(args[0].name) + bstack11l1lll1_opy_ (u"ࠣࠢ࠰ࠤࡋࡧࡩ࡭ࡧࡧࠥࡡࡴࠢഓ") + str(bstack111111l_opy_)), bstack11l1lll1_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣഔ"))
        if self.driver_before_scenario:
          bstack111l111ll_opy_(context, bstack11l1lll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥക"), bstack1l11l1ll1_opy_)
          bstack111l11ll1_opy_.execute_script(bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩഖ") + json.dumps(str(args[0].name) + bstack11l1lll1_opy_ (u"ࠧࠦ࠭ࠡࡈࡤ࡭ࡱ࡫ࡤࠢ࡞ࡱࠦഗ") + str(bstack111111l_opy_)) + bstack11l1lll1_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦࡪࡸࡲࡰࡴࠥࢁࢂ࠭ഘ"))
        if self.driver_before_scenario:
          bstack111l11ll1_opy_.execute_script(bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡳࡵࡣࡷࡹࡸࠨ࠺ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ࠮ࠣࠦࡷ࡫ࡡࡴࡱࡱࠦ࠿ࠦࠧങ") + json.dumps(bstack11l1lll1_opy_ (u"ࠣࡕࡦࡩࡳࡧࡲࡪࡱࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧച") + str(bstack1l11l1ll1_opy_)) + bstack11l1lll1_opy_ (u"ࠩࢀࢁࠬഛ"))
      else:
        bstack1lll11lll_opy_(context, bstack11l1lll1_opy_ (u"ࠥࡔࡦࡹࡳࡦࡦࠤࠦജ"), bstack11l1lll1_opy_ (u"ࠦ࡮ࡴࡦࡰࠤഝ"))
        if self.driver_before_scenario:
          bstack111l111ll_opy_(context, bstack11l1lll1_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧഞ"))
        bstack111l11ll1_opy_.execute_script(bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫട") + json.dumps(str(args[0].name) + bstack11l1lll1_opy_ (u"ࠢࠡ࠯ࠣࡔࡦࡹࡳࡦࡦࠤࠦഠ")) + bstack11l1lll1_opy_ (u"ࠨ࠮ࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡩ࡯ࡨࡲࠦࢂࢃࠧഡ"))
        if self.driver_before_scenario:
          bstack111l11ll1_opy_.execute_script(bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡵࡷࡥࡹࡻࡳࠣ࠼ࠥࡴࡦࡹࡳࡦࡦࠥࢁࢂ࠭ഢ"))
    except Exception as e:
      logger.debug(bstack11l1lll1_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦ࡭ࡢࡴ࡮ࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷࠥ࡯࡮ࠡࡣࡩࡸࡪࡸࠠࡧࡧࡤࡸࡺࡸࡥ࠻ࠢࡾࢁࠬണ").format(str(e)))
  elif name == bstack11l1lll1_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡪࡪࡧࡴࡶࡴࡨࠫത"):
    try:
      bstack111l11ll1_opy_ = threading.current_thread().bstackSessionDriver if bstack1ll1ll111_opy_(bstack11l1lll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫഥ")) else context.browser
      if context.failed is True:
        bstack111lll1l1_opy_ = []
        bstack11lll11ll_opy_ = []
        bstack1ll111_opy_ = []
        bstack1l11ll1l1_opy_ = bstack11l1lll1_opy_ (u"࠭ࠧദ")
        try:
          import traceback
          for exc in self.exception_arr:
            bstack111lll1l1_opy_.append(exc.__class__.__name__)
          for exc_tb in self.exc_traceback_arr:
            bstack1111ll1l_opy_ = traceback.format_tb(exc_tb)
            bstack11ll111l1_opy_ = bstack11l1lll1_opy_ (u"ࠧࠡࠩധ").join(bstack1111ll1l_opy_)
            bstack11lll11ll_opy_.append(bstack11ll111l1_opy_)
            bstack1ll111_opy_.append(bstack1111ll1l_opy_[-1])
        except Exception as e:
          logger.debug(bstack1lllll1l_opy_.format(str(e)))
        bstack1l11l1ll1_opy_ = bstack11l1lll1_opy_ (u"ࠨࠩന")
        for i in range(len(bstack111lll1l1_opy_)):
          bstack1l11l1ll1_opy_ += bstack111lll1l1_opy_[i] + bstack1ll111_opy_[i] + bstack11l1lll1_opy_ (u"ࠩ࡟ࡲࠬഩ")
        bstack1l11ll1l1_opy_ = bstack11l1lll1_opy_ (u"ࠪࠤࠬപ").join(bstack11lll11ll_opy_)
        if not self.driver_before_scenario:
          bstack1lll11lll_opy_(context, bstack1l11ll1l1_opy_, bstack11l1lll1_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥഫ"))
          bstack111l111ll_opy_(context, bstack11l1lll1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧബ"), bstack1l11l1ll1_opy_)
          bstack111l11ll1_opy_.execute_script(bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫഭ") + json.dumps(bstack1l11ll1l1_opy_) + bstack11l1lll1_opy_ (u"ࠧ࠭ࠢࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠤࠧ࡫ࡲࡳࡱࡵࠦࢂࢃࠧമ"))
          bstack111l11ll1_opy_.execute_script(bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠤࡩࡥ࡮ࡲࡥࡥࠤ࠯ࠤࠧࡸࡥࡢࡵࡲࡲࠧࡀࠠࠨയ") + json.dumps(bstack11l1lll1_opy_ (u"ࠤࡖࡳࡲ࡫ࠠࡴࡥࡨࡲࡦࡸࡩࡰࡵࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࡡࡴࠢര") + str(bstack1l11l1ll1_opy_)) + bstack11l1lll1_opy_ (u"ࠪࢁࢂ࠭റ"))
      else:
        if not self.driver_before_scenario:
          bstack1lll11lll_opy_(context, bstack11l1lll1_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩ࠿ࠦࠢല") + str(self.feature.name) + bstack11l1lll1_opy_ (u"ࠧࠦࡰࡢࡵࡶࡩࡩࠧࠢള"), bstack11l1lll1_opy_ (u"ࠨࡩ࡯ࡨࡲࠦഴ"))
          bstack111l111ll_opy_(context, bstack11l1lll1_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪࠢവ"))
          bstack111l11ll1_opy_.execute_script(bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭ശ") + json.dumps(bstack11l1lll1_opy_ (u"ࠤࡉࡩࡦࡺࡵࡳࡧ࠽ࠤࠧഷ") + str(self.feature.name) + bstack11l1lll1_opy_ (u"ࠥࠤࡵࡧࡳࡴࡧࡧࠥࠧസ")) + bstack11l1lll1_opy_ (u"ࠫ࠱ࠦࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠡࠤ࡬ࡲ࡫ࡵࠢࡾࡿࠪഹ"))
          bstack111l11ll1_opy_.execute_script(bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡸࡺࡡࡵࡷࡶࠦ࠿ࠨࡰࡢࡵࡶࡩࡩࠨࡽࡾࠩഺ"))
    except Exception as e:
      logger.debug(bstack11l1lll1_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡰࡥࡷࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳࠡ࡫ࡱࠤࡦ࡬ࡴࡦࡴࠣࡪࡪࡧࡴࡶࡴࡨ࠾ࠥࢁࡽࠨ഻").format(str(e)))
  else:
    bstack11l1l11l1_opy_(self, name, context, *args)
  if name in [bstack11l1lll1_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡦࡦࡣࡷࡹࡷ࡫഼ࠧ"), bstack11l1lll1_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠩഽ")]:
    bstack11l1l11l1_opy_(self, name, context, *args)
    if (name == bstack11l1lll1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡵࡦࡩࡳࡧࡲࡪࡱࠪാ") and self.driver_before_scenario) or (name == bstack11l1lll1_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡩࡩࡦࡺࡵࡳࡧࠪി") and not self.driver_before_scenario):
      try:
        bstack111l11ll1_opy_ = threading.current_thread().bstackSessionDriver if bstack1ll1ll111_opy_(bstack11l1lll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪീ")) else context.browser
        bstack111l11ll1_opy_.quit()
      except Exception:
        pass
def bstack1l1l1lll1_opy_(config, startdir):
  return bstack11l1lll1_opy_ (u"ࠧࡪࡲࡪࡸࡨࡶ࠿ࠦࡻ࠱ࡿࠥു").format(bstack11l1lll1_opy_ (u"ࠨࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠧൂ"))
class Notset:
  def __repr__(self):
    return bstack11l1lll1_opy_ (u"ࠢ࠽ࡐࡒࡘࡘࡋࡔ࠿ࠤൃ")
notset = Notset()
def bstack1l1l11lll_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack11l1111l_opy_
  if str(name).lower() == bstack11l1lll1_opy_ (u"ࠨࡦࡵ࡭ࡻ࡫ࡲࠨൄ"):
    return bstack11l1lll1_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠣ൅")
  else:
    return bstack11l1111l_opy_(self, name, default, skip)
def bstack1111lll11_opy_(item, when):
  global bstack111lll1ll_opy_
  try:
    bstack111lll1ll_opy_(item, when)
  except Exception as e:
    pass
def bstack1lll11111_opy_():
  return
def bstack111l111l_opy_(type, name, status, reason, bstack1l1l11l1l_opy_, bstack1ll1111l_opy_):
  bstack111ll1ll1_opy_ = {
    bstack11l1lll1_opy_ (u"ࠪࡥࡨࡺࡩࡰࡰࠪെ"): type,
    bstack11l1lll1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧേ"): {}
  }
  if type == bstack11l1lll1_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧൈ"):
    bstack111ll1ll1_opy_[bstack11l1lll1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ൉")][bstack11l1lll1_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ൊ")] = bstack1l1l11l1l_opy_
    bstack111ll1ll1_opy_[bstack11l1lll1_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫോ")][bstack11l1lll1_opy_ (u"ࠩࡧࡥࡹࡧࠧൌ")] = json.dumps(str(bstack1ll1111l_opy_))
  if type == bstack11l1lll1_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨ്ࠫ"):
    bstack111ll1ll1_opy_[bstack11l1lll1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧൎ")][bstack11l1lll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ൏")] = name
  if type == bstack11l1lll1_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩ൐"):
    bstack111ll1ll1_opy_[bstack11l1lll1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪ൑")][bstack11l1lll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ൒")] = status
    if status == bstack11l1lll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ൓"):
      bstack111ll1ll1_opy_[bstack11l1lll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ൔ")][bstack11l1lll1_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫൕ")] = json.dumps(str(reason))
  bstack111l111_opy_ = bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪൖ").format(json.dumps(bstack111ll1ll1_opy_))
  return bstack111l111_opy_
def bstack1llll1ll_opy_(item, call, rep):
  global bstack1111l1l1_opy_
  global bstack11llll11l_opy_
  global bstack1ll11l1ll_opy_
  name = bstack11l1lll1_opy_ (u"࠭ࠧൗ")
  try:
    if rep.when == bstack11l1lll1_opy_ (u"ࠧࡤࡣ࡯ࡰࠬ൘"):
      bstack1ll11ll1_opy_ = threading.current_thread().bstack11111l11_opy_
      try:
        if not bstack1ll11l1ll_opy_:
          name = str(rep.nodeid)
          bstack1l1ll_opy_ = bstack111l111l_opy_(bstack11l1lll1_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩ൙"), name, bstack11l1lll1_opy_ (u"ࠩࠪ൚"), bstack11l1lll1_opy_ (u"ࠪࠫ൛"), bstack11l1lll1_opy_ (u"ࠫࠬ൜"), bstack11l1lll1_opy_ (u"ࠬ࠭൝"))
          for driver in bstack11llll11l_opy_:
            if bstack1ll11ll1_opy_ == driver.session_id:
              driver.execute_script(bstack1l1ll_opy_)
      except Exception as e:
        logger.debug(bstack11l1lll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠠࡧࡱࡵࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡵࡨࡷࡸ࡯࡯࡯࠼ࠣࡿࢂ࠭൞").format(str(e)))
      try:
        status = bstack11l1lll1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧൟ") if rep.outcome.lower() == bstack11l1lll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨൠ") else bstack11l1lll1_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩൡ")
        reason = bstack11l1lll1_opy_ (u"ࠪࠫൢ")
        if (reason != bstack11l1lll1_opy_ (u"ࠦࠧൣ")):
          try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
          except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
          threading.current_thread().bstackTestErrorMessages.append(str(reason))
        if status == bstack11l1lll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ൤"):
          reason = rep.longrepr.reprcrash.message
          if (not threading.current_thread().bstackTestErrorMessages):
            threading.current_thread().bstackTestErrorMessages = []
          threading.current_thread().bstackTestErrorMessages.append(reason)
        level = bstack11l1lll1_opy_ (u"࠭ࡩ࡯ࡨࡲࠫ൥") if status == bstack11l1lll1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ൦") else bstack11l1lll1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧ൧")
        data = name + bstack11l1lll1_opy_ (u"ࠩࠣࡴࡦࡹࡳࡦࡦࠤࠫ൨") if status == bstack11l1lll1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ൩") else name + bstack11l1lll1_opy_ (u"ࠫࠥ࡬ࡡࡪ࡮ࡨࡨࠦࠦࠧ൪") + reason
        bstack11l11ll_opy_ = bstack111l111l_opy_(bstack11l1lll1_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧ൫"), bstack11l1lll1_opy_ (u"࠭ࠧ൬"), bstack11l1lll1_opy_ (u"ࠧࠨ൭"), bstack11l1lll1_opy_ (u"ࠨࠩ൮"), level, data)
        for driver in bstack11llll11l_opy_:
          if bstack1ll11ll1_opy_ == driver.session_id:
            driver.execute_script(bstack11l11ll_opy_)
      except Exception as e:
        logger.debug(bstack11l1lll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡣࡰࡰࡷࡩࡽࡺࠠࡧࡱࡵࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡵࡨࡷࡸ࡯࡯࡯࠼ࠣࡿࢂ࠭൯").format(str(e)))
  except Exception as e:
    logger.debug(bstack11l1lll1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡳࡵࡣࡷࡩࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡺࡥࡴࡶࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࢀࢃࠧ൰").format(str(e)))
  bstack1111l1l1_opy_(item, call, rep)
def bstack1lll1l_opy_(framework_name):
  global bstack1l11l1lll_opy_
  global bstack11ll1_opy_
  global bstack1llll11l1_opy_
  bstack1l11l1lll_opy_ = framework_name
  logger.info(bstack1lll1ll11_opy_.format(bstack1l11l1lll_opy_.split(bstack11l1lll1_opy_ (u"ࠫ࠲࠭൱"))[0]))
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    Service.start = bstack1l11lll_opy_
    Service.stop = bstack1ll1lll1l_opy_
    webdriver.Remote.__init__ = bstack1ll11l111_opy_
    webdriver.Remote.get = bstack11l1ll1ll_opy_
    WebDriver.close = bstack11l11_opy_
    WebDriver.quit = bstack1l111llll_opy_
    bstack11ll1_opy_ = True
  except Exception as e:
    pass
  bstack1ll11l11l_opy_()
  if not bstack11ll1_opy_:
    bstack111ll1l11_opy_(bstack11l1lll1_opy_ (u"ࠧࡖࡡࡤ࡭ࡤ࡫ࡪࡹࠠ࡯ࡱࡷࠤ࡮ࡴࡳࡵࡣ࡯ࡰࡪࡪࠢ൲"), bstack1l11l11_opy_)
  if bstack1111ll1ll_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      RemoteConnection._get_proxy_url = bstack111_opy_
    except Exception as e:
      logger.error(bstack111lll11l_opy_.format(str(e)))
  if (bstack11l1lll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ൳") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack1l1l11111_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack1l1ll11ll_opy_
      except Exception as e:
        logger.warn(bstack11l111lll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack1ll1l111_opy_
      except Exception as e:
        logger.debug(bstack1lll1_opy_ + str(e))
    except Exception as e:
      bstack111ll1l11_opy_(e, bstack11l111lll_opy_)
    Output.end_test = bstack111ll1l_opy_
    TestStatus.__init__ = bstack111l11l1_opy_
    QueueItem.__init__ = bstack111l11ll_opy_
    pabot._create_items = bstack11l1111l1_opy_
    try:
      from pabot import __version__ as bstack11lll11l1_opy_
      if version.parse(bstack11lll11l1_opy_) >= version.parse(bstack11l1lll1_opy_ (u"ࠧ࠳࠰࠴࠹࠳࠶ࠧ൴")):
        pabot._run = bstack11llllll_opy_
      elif version.parse(bstack11lll11l1_opy_) >= version.parse(bstack11l1lll1_opy_ (u"ࠨ࠴࠱࠵࠸࠴࠰ࠨ൵")):
        pabot._run = bstack1l11l1l1_opy_
      else:
        pabot._run = bstack11l1l1ll_opy_
    except Exception as e:
      pabot._run = bstack11l1l1ll_opy_
    pabot._create_command_for_execution = bstack111l1ll11_opy_
    pabot._report_results = bstack111lllll1_opy_
  if bstack11l1lll1_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩ൶") in str(framework_name).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack111ll1l11_opy_(e, bstack111lll11_opy_)
    Runner.run_hook = bstack1ll1l1ll_opy_
    Step.run = bstack11l1ll1l_opy_
  if bstack11l1lll1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ൷") in str(framework_name).lower():
    try:
      from pytest_selenium import pytest_selenium
      from _pytest.config import Config
      pytest_selenium.pytest_report_header = bstack1l1l1lll1_opy_
      from pytest_selenium.drivers import browserstack
      browserstack.pytest_selenium_runtest_makereport = bstack1lll11111_opy_
      Config.getoption = bstack1l1l11lll_opy_
    except Exception as e:
      pass
    try:
      from _pytest import runner
      runner._update_current_test_var = bstack1111lll11_opy_
    except Exception as e:
      pass
    try:
      from pytest_bdd import reporting
      reporting.runtest_makereport = bstack1llll1ll_opy_
    except Exception as e:
      pass
def bstack1llll_opy_():
  global CONFIG
  if bstack11l1lll1_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫ൸") in CONFIG and int(CONFIG[bstack11l1lll1_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬ൹")]) > 1:
    logger.warn(bstack111l1lll_opy_)
def bstack11lll1l11_opy_(arg):
  arg.append(bstack11l1lll1_opy_ (u"ࠨ࠭࠮࡫ࡰࡴࡴࡸࡴ࠮࡯ࡲࡨࡪࡃࡩ࡮ࡲࡲࡶࡹࡲࡩࡣࠤൺ"))
  arg.append(bstack11l1lll1_opy_ (u"ࠢ࠮࡙ࠥൻ"))
  arg.append(bstack11l1lll1_opy_ (u"ࠣ࡫ࡪࡲࡴࡸࡥ࠻ࡏࡲࡨࡺࡲࡥࠡࡣ࡯ࡶࡪࡧࡤࡺࠢ࡬ࡱࡵࡵࡲࡵࡧࡧ࠾ࡵࡿࡴࡦࡵࡷ࠲ࡕࡿࡴࡦࡵࡷ࡛ࡦࡸ࡮ࡪࡰࡪࠦർ"))
  arg.append(bstack11l1lll1_opy_ (u"ࠤ࠰࡛ࠧൽ"))
  arg.append(bstack11l1lll1_opy_ (u"ࠥ࡭࡬ࡴ࡯ࡳࡧ࠽ࡘ࡭࡫ࠠࡩࡱࡲ࡯࡮ࡳࡰ࡭ࠤൾ"))
  global CONFIG
  bstack1lll1l_opy_(bstack11llll1_opy_)
  os.environ[bstack11l1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢ࡙ࡘࡋࡒࡏࡃࡐࡉࠬൿ")] = CONFIG[bstack11l1lll1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧ඀")]
  os.environ[bstack11l1lll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡃࡄࡇࡖࡗࡤࡑࡅ࡚ࠩඁ")] = CONFIG[bstack11l1lll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪං")]
  from _pytest.config import main as bstack11llll_opy_
  bstack11llll_opy_(arg)
def bstack1ll11111l_opy_(arg):
  bstack1lll1l_opy_(bstack1lll1ll1l_opy_)
  from behave.__main__ import main as bstack1l111111l_opy_
  bstack1l111111l_opy_(arg)
def bstack11llll1ll_opy_():
  logger.info(bstack1lllll11l_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack11l1lll1_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧඃ"), help=bstack11l1lll1_opy_ (u"ࠩࡊࡩࡳ࡫ࡲࡢࡶࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡧࡴࡴࡦࡪࡩࠪ඄"))
  parser.add_argument(bstack11l1lll1_opy_ (u"ࠪ࠱ࡺ࠭අ"), bstack11l1lll1_opy_ (u"ࠫ࠲࠳ࡵࡴࡧࡵࡲࡦࡳࡥࠨආ"), help=bstack11l1lll1_opy_ (u"ࠬ࡟࡯ࡶࡴࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡸࡷࡪࡸ࡮ࡢ࡯ࡨࠫඇ"))
  parser.add_argument(bstack11l1lll1_opy_ (u"࠭࠭࡬ࠩඈ"), bstack11l1lll1_opy_ (u"ࠧ࠮࠯࡮ࡩࡾ࠭ඉ"), help=bstack11l1lll1_opy_ (u"ࠨ࡛ࡲࡹࡷࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡧࡣࡤࡧࡶࡷࠥࡱࡥࡺࠩඊ"))
  parser.add_argument(bstack11l1lll1_opy_ (u"ࠩ࠰ࡪࠬඋ"), bstack11l1lll1_opy_ (u"ࠪ࠱࠲࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨඌ"), help=bstack11l1lll1_opy_ (u"ࠫ࡞ࡵࡵࡳࠢࡷࡩࡸࡺࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪඍ"))
  bstack1ll111l1_opy_ = parser.parse_args()
  try:
    bstack1l1_opy_ = bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡬࡫࡮ࡦࡴ࡬ࡧ࠳ࡿ࡭࡭࠰ࡶࡥࡲࡶ࡬ࡦࠩඎ")
    if bstack1ll111l1_opy_.framework and bstack1ll111l1_opy_.framework not in (bstack11l1lll1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ඏ"), bstack11l1lll1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴ࠳ࠨඐ")):
      bstack1l1_opy_ = bstack11l1lll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭࠱ࡽࡲࡲ࠮ࡴࡣࡰࡴࡱ࡫ࠧඑ")
    bstack111llll1l_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1l1_opy_)
    bstack111lll1_opy_ = open(bstack111llll1l_opy_, bstack11l1lll1_opy_ (u"ࠩࡵࠫඒ"))
    bstack11l11111l_opy_ = bstack111lll1_opy_.read()
    bstack111lll1_opy_.close()
    if bstack1ll111l1_opy_.username:
      bstack11l11111l_opy_ = bstack11l11111l_opy_.replace(bstack11l1lll1_opy_ (u"ࠪ࡝ࡔ࡛ࡒࡠࡗࡖࡉࡗࡔࡁࡎࡇࠪඓ"), bstack1ll111l1_opy_.username)
    if bstack1ll111l1_opy_.key:
      bstack11l11111l_opy_ = bstack11l11111l_opy_.replace(bstack11l1lll1_opy_ (u"ࠫ࡞ࡕࡕࡓࡡࡄࡇࡈࡋࡓࡔࡡࡎࡉ࡞࠭ඔ"), bstack1ll111l1_opy_.key)
    if bstack1ll111l1_opy_.framework:
      bstack11l11111l_opy_ = bstack11l11111l_opy_.replace(bstack11l1lll1_opy_ (u"ࠬ࡟ࡏࡖࡔࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭ඕ"), bstack1ll111l1_opy_.framework)
    file_name = bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩඖ")
    file_path = os.path.abspath(file_name)
    bstack111lll111_opy_ = open(file_path, bstack11l1lll1_opy_ (u"ࠧࡸࠩ඗"))
    bstack111lll111_opy_.write(bstack11l11111l_opy_)
    bstack111lll111_opy_.close()
    logger.info(bstack1ll1ll11_opy_)
    try:
      os.environ[bstack11l1lll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠪ඘")] = bstack1ll111l1_opy_.framework if bstack1ll111l1_opy_.framework != None else bstack11l1lll1_opy_ (u"ࠤࠥ඙")
      config = yaml.safe_load(bstack11l11111l_opy_)
      config[bstack11l1lll1_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪක")] = bstack11l1lll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱ࠱ࡸ࡫ࡴࡶࡲࠪඛ")
      bstack1l1l11ll1_opy_(bstack1ll1lll11_opy_, config)
    except Exception as e:
      logger.debug(bstack1ll11ll11_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack1l11l1l11_opy_.format(str(e)))
def bstack1l1l11ll1_opy_(bstack111l1l1_opy_, config, bstack1ll1111_opy_ = {}):
  global bstack111ll111l_opy_
  if not config:
    return
  bstack1l1llll_opy_ = bstack111l111l1_opy_ if not bstack111ll111l_opy_ else ( bstack1l11lll1_opy_ if bstack11l1lll1_opy_ (u"ࠬࡧࡰࡱࠩග") in config else bstack11ll1l1ll_opy_ )
  data = {
    bstack11l1lll1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨඝ"): config[bstack11l1lll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩඞ")],
    bstack11l1lll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫඟ"): config[bstack11l1lll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬච")],
    bstack11l1lll1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧඡ"): bstack111l1l1_opy_,
    bstack11l1lll1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧජ"): {
      bstack11l1lll1_opy_ (u"ࠬࡲࡡ࡯ࡩࡸࡥ࡬࡫࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪඣ"): str(config[bstack11l1lll1_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭ඤ")]) if bstack11l1lll1_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧඥ") in config else bstack11l1lll1_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࠤඦ"),
      bstack11l1lll1_opy_ (u"ࠩࡵࡩ࡫࡫ࡲࡳࡧࡵࠫට"): bstack1l1111111_opy_(os.getenv(bstack11l1lll1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠧඨ"), bstack11l1lll1_opy_ (u"ࠦࠧඩ"))),
      bstack11l1lll1_opy_ (u"ࠬࡲࡡ࡯ࡩࡸࡥ࡬࡫ࠧඪ"): bstack11l1lll1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ණ"),
      bstack11l1lll1_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࠨඬ"): bstack1l1llll_opy_,
      bstack11l1lll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫත"): config[bstack11l1lll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬථ")]if config[bstack11l1lll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ද")] else bstack11l1lll1_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࠧධ"),
      bstack11l1lll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧන"): str(config[bstack11l1lll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ඲")]) if bstack11l1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩඳ") in config else bstack11l1lll1_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࠤප"),
      bstack11l1lll1_opy_ (u"ࠩࡲࡷࠬඵ"): sys.platform,
      bstack11l1lll1_opy_ (u"ࠪ࡬ࡴࡹࡴ࡯ࡣࡰࡩࠬබ"): socket.gethostname()
    }
  }
  update(data[bstack11l1lll1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧභ")], bstack1ll1111_opy_)
  try:
    response = bstack1ll11_opy_(bstack11l1lll1_opy_ (u"ࠬࡖࡏࡔࡖࠪම"), bstack11111l_opy_, data, config)
    if response:
      logger.debug(bstack1llll11l_opy_.format(bstack111l1l1_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack1ll111ll1_opy_.format(str(e)))
def bstack1ll11_opy_(type, url, data, config):
  bstack11l1l11_opy_ = bstack1llllll11_opy_.format(url)
  proxies = bstack11ll1l1l1_opy_(config, bstack11l1l11_opy_)
  if type == bstack11l1lll1_opy_ (u"࠭ࡐࡐࡕࡗࠫඹ"):
    response = requests.post(bstack11l1l11_opy_, json=data,
                    headers={bstack11l1lll1_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡖࡼࡴࡪ࠭ය"): bstack11l1lll1_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫර")}, auth=(config[bstack11l1lll1_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫ඼")], config[bstack11l1lll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ල")]), proxies=proxies)
  return response
def bstack1l1111111_opy_(framework):
  return bstack11l1lll1_opy_ (u"ࠦࢀࢃ࠭ࡱࡻࡷ࡬ࡴࡴࡡࡨࡧࡱࡸ࠴ࢁࡽࠣ඾").format(str(framework), __version__) if framework else bstack11l1lll1_opy_ (u"ࠧࡶࡹࡵࡪࡲࡲࡦ࡭ࡥ࡯ࡶ࠲ࡿࢂࠨ඿").format(__version__)
def bstack1ll11lll_opy_():
  global CONFIG
  if bool(CONFIG):
    return
  try:
    bstack1l1llll1_opy_()
    logger.debug(bstack11ll1l_opy_.format(str(CONFIG)))
    bstack1l111ll11_opy_()
    bstack1l11111l1_opy_()
  except Exception as e:
    logger.error(bstack11l1lll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࡻࡰ࠭ࠢࡨࡶࡷࡵࡲ࠻ࠢࠥව") + str(e))
    sys.exit(1)
  sys.excepthook = bstack11llll111_opy_
  atexit.register(bstack1l1l11l_opy_)
  signal.signal(signal.SIGINT, bstack11ll_opy_)
  signal.signal(signal.SIGTERM, bstack11ll_opy_)
def bstack11llll111_opy_(exctype, value, traceback):
  global bstack11llll11l_opy_
  try:
    for driver in bstack11llll11l_opy_:
      driver.execute_script(
        bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡳࡵࡣࡷࡹࡸࠨ࠺ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ࠮ࠣࠦࡷ࡫ࡡࡴࡱࡱࠦ࠿ࠦࠧශ") + json.dumps(bstack11l1lll1_opy_ (u"ࠣࡕࡨࡷࡸ࡯࡯࡯ࠢࡩࡥ࡮ࡲࡥࡥࠢࡺ࡭ࡹ࡮࠺ࠡ࡞ࡱࠦෂ") + str(value)) + bstack11l1lll1_opy_ (u"ࠩࢀࢁࠬස"))
  except Exception:
    pass
  bstack1lllll11_opy_(value)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack1lllll11_opy_(message = bstack11l1lll1_opy_ (u"ࠪࠫහ")):
  global CONFIG
  try:
    if message:
      bstack1ll1111_opy_ = {
        bstack11l1lll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪළ"): str(message)
      }
      bstack1l1l11ll1_opy_(bstack1llllll1l_opy_, CONFIG, bstack1ll1111_opy_)
    else:
      bstack1l1l11ll1_opy_(bstack1llllll1l_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack1l1111l1l_opy_.format(str(e)))
def bstack1l1ll111_opy_(bstack1ll1ll11l_opy_, size):
  bstack11ll1ll1_opy_ = []
  while len(bstack1ll1ll11l_opy_) > size:
    bstack11l1l111l_opy_ = bstack1ll1ll11l_opy_[:size]
    bstack11ll1ll1_opy_.append(bstack11l1l111l_opy_)
    bstack1ll1ll11l_opy_   = bstack1ll1ll11l_opy_[size:]
  bstack11ll1ll1_opy_.append(bstack1ll1ll11l_opy_)
  return bstack11ll1ll1_opy_
def bstack11l11l1ll_opy_(args):
  if bstack11l1lll1_opy_ (u"ࠬ࠳࡭ࠨෆ") in args and bstack11l1lll1_opy_ (u"࠭ࡰࡥࡤࠪ෇") in args:
    return True
  return False
def run_on_browserstack(bstack1l11l1_opy_=None, bstack1l1llll11_opy_=None, bstack11l1ll_opy_=False):
  global CONFIG
  global bstack1lllll111_opy_
  global bstack111l1l11l_opy_
  bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠧࠨ෈")
  if bstack1l11l1_opy_ and isinstance(bstack1l11l1_opy_, str):
    bstack1l11l1_opy_ = eval(bstack1l11l1_opy_)
  if bstack1l11l1_opy_:
    CONFIG = bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠨࡅࡒࡒࡋࡏࡇࠨ෉")]
    bstack1lllll111_opy_ = bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠩࡋ࡙ࡇࡥࡕࡓࡎ්ࠪ")]
    bstack111l1l11l_opy_ = bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠪࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬ෋")]
    bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫ෌")
  if not bstack11l1ll_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack1ll111lll_opy_)
      return
    if sys.argv[1] == bstack11l1lll1_opy_ (u"ࠬ࠳࠭ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ෍")  or sys.argv[1] == bstack11l1lll1_opy_ (u"࠭࠭ࡷࠩ෎"):
      logger.info(bstack11l1lll1_opy_ (u"ࠧࡃࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡐࡺࡶ࡫ࡳࡳࠦࡓࡅࡍࠣࡺࢀࢃࠧා").format(__version__))
      return
    if sys.argv[1] == bstack11l1lll1_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧැ"):
      bstack11llll1ll_opy_()
      return
  args = sys.argv
  bstack1ll11lll_opy_()
  global bstack1111lll1_opy_
  global bstack11l1l11ll_opy_
  global bstack1l1l1ll_opy_
  global bstack11llll1l_opy_
  global bstack1l11_opy_
  global bstack11l11l11_opy_
  global bstack1l1ll1_opy_
  global bstack1llll11l1_opy_
  if not bstack1ll1llll1_opy_:
    if args[1] == bstack11l1lll1_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩෑ") or args[1] == bstack11l1lll1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰ࠶ࠫි"):
      bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫී")
      args = args[2:]
    elif args[1] == bstack11l1lll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫු"):
      bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ෕")
      args = args[2:]
    elif args[1] == bstack11l1lll1_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭ූ"):
      bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧ෗")
      args = args[2:]
    elif args[1] == bstack11l1lll1_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪෘ"):
      bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫෙ")
      args = args[2:]
    elif args[1] == bstack11l1lll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫේ"):
      bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬෛ")
      args = args[2:]
    elif args[1] == bstack11l1lll1_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ො"):
      bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧෝ")
      args = args[2:]
    else:
      if not bstack11l1lll1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫෞ") in CONFIG or str(CONFIG[bstack11l1lll1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬෟ")]).lower() in [bstack11l1lll1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ෠"), bstack11l1lll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱ࠷ࠬ෡")]:
        bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ෢")
        args = args[1:]
      elif str(CONFIG[bstack11l1lll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩ෣")]).lower() == bstack11l1lll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭෤"):
        bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ෥")
        args = args[1:]
      elif str(CONFIG[bstack11l1lll1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬ෦")]).lower() == bstack11l1lll1_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩ෧"):
        bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪ෨")
        args = args[1:]
      elif str(CONFIG[bstack11l1lll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ෩")]).lower() == bstack11l1lll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭෪"):
        bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ෫")
        args = args[1:]
      elif str(CONFIG[bstack11l1lll1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫ෬")]).lower() == bstack11l1lll1_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩ෭"):
        bstack1ll1llll1_opy_ = bstack11l1lll1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪ෮")
        args = args[1:]
      else:
        os.environ[bstack11l1lll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭෯")] = bstack1ll1llll1_opy_
        bstack1lll1l1l_opy_(bstack1lll1l1ll_opy_)
  global bstack11l111ll_opy_
  if bstack1l11l1_opy_:
    try:
      os.environ[bstack11l1lll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧ෰")] = bstack1ll1llll1_opy_
      bstack1l1l11ll1_opy_(bstack11l11ll1l_opy_, CONFIG)
    except Exception as e:
      logger.debug(bstack1l1111l1l_opy_.format(str(e)))
  global bstack1l1l1l11l_opy_
  global bstack1lll_opy_
  global bstack11_opy_
  global bstack1l1111l_opy_
  global bstack11ll1ll_opy_
  global bstack1l111l_opy_
  global bstack1ll111l_opy_
  global bstack11l1l11l_opy_
  global bstackl_opy_
  global bstack11l111l11_opy_
  global bstack11llll1l1_opy_
  global bstack11l1l11l1_opy_
  global bstack1ll1111l1_opy_
  global bstack11l1111ll_opy_
  global bstack11l1l_opy_
  global bstack11l1111l_opy_
  global bstack111lll1ll_opy_
  global bstack111l11111_opy_
  global bstack1111l1l1_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1l1l1l11l_opy_ = webdriver.Remote.__init__
    bstack1lll_opy_ = WebDriver.quit
    bstack11llll1l1_opy_ = WebDriver.close
    bstack11l1111ll_opy_ = WebDriver.get
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack11l111ll_opy_ = Popen.__init__
  except Exception as e:
    pass
  if bstack11ll11111_opy_():
    if bstack1111lllll_opy_() < version.parse(bstack11l1l1ll1_opy_):
      logger.error(bstack1l111lll1_opy_.format(bstack1111lllll_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        bstack11l1l_opy_ = RemoteConnection._get_proxy_url
      except Exception as e:
        logger.error(bstack111lll11l_opy_.format(str(e)))
  if bstack1ll1llll1_opy_ != bstack11l1lll1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭෱") or (bstack1ll1llll1_opy_ == bstack11l1lll1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧෲ") and not bstack1l11l1_opy_):
    bstack11ll1lll_opy_()
  if (bstack1ll1llll1_opy_ in [bstack11l1lll1_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧෳ"), bstack11l1lll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ෴"), bstack11l1lll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫ෵")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack1l1l11111_opy_
        bstack11ll1ll_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warn(bstack11l111lll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack1l1111l_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack1lll1_opy_ + str(e))
    except Exception as e:
      bstack111ll1l11_opy_(e, bstack11l111lll_opy_)
    if bstack1ll1llll1_opy_ != bstack11l1lll1_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬ෶"):
      bstack1llll1l11_opy_()
    bstack11_opy_ = Output.end_test
    bstack1l111l_opy_ = TestStatus.__init__
    bstack11l1l11l_opy_ = pabot._run
    bstackl_opy_ = QueueItem.__init__
    bstack11l111l11_opy_ = pabot._create_command_for_execution
    bstack111l11111_opy_ = pabot._report_results
  if bstack1ll1llll1_opy_ == bstack11l1lll1_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬ෷"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack111ll1l11_opy_(e, bstack111lll11_opy_)
    bstack11l1l11l1_opy_ = Runner.run_hook
    bstack1ll1111l1_opy_ = Step.run
  if bstack1ll1llll1_opy_ == bstack11l1lll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭෸"):
    try:
      from _pytest.config import Config
      bstack11l1111l_opy_ = Config.getoption
      from _pytest import runner
      bstack111lll1ll_opy_ = runner._update_current_test_var
    except Exception as e:
      logger.warn(e, bstack1l111ll1_opy_)
    try:
      from pytest_bdd import reporting
      bstack1111l1l1_opy_ = reporting.runtest_makereport
    except Exception as e:
      logger.debug(bstack11l1lll1_opy_ (u"ࠧࡑ࡮ࡨࡥࡸ࡫ࠠࡪࡰࡶࡸࡦࡲ࡬ࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡺ࡯ࠡࡴࡸࡲࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡩࡸࡺࡳࠨ෹"))
  if bstack1ll1llll1_opy_ == bstack11l1lll1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨ෺"):
    bstack11l1l11ll_opy_ = True
    if bstack1l11l1_opy_ and bstack11l1ll_opy_:
      bstack1l11_opy_ = CONFIG.get(bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭෻"), {}).get(bstack11l1lll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ෼"))
      bstack1lll1l_opy_(bstack1l11l1l_opy_)
    elif bstack1l11l1_opy_:
      bstack1l11_opy_ = CONFIG.get(bstack11l1lll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨ෽"), {}).get(bstack11l1lll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ෾"))
      global bstack11llll11l_opy_
      try:
        if bstack11l11l1ll_opy_(bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෿")]) and multiprocessing.current_process().name == bstack11l1lll1_opy_ (u"ࠧ࠱ࠩ฀"):
          bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫก")].remove(bstack11l1lll1_opy_ (u"ࠩ࠰ࡱࠬข"))
          bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ฃ")].remove(bstack11l1lll1_opy_ (u"ࠫࡵࡪࡢࠨค"))
          bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨฅ")] = bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩฆ")][0]
          with open(bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪง")], bstack11l1lll1_opy_ (u"ࠨࡴࠪจ")) as f:
            bstack11l1111_opy_ = f.read()
          bstack1111lll1l_opy_ = bstack11l1lll1_opy_ (u"ࠤࠥࠦ࡫ࡸ࡯࡮ࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡵࡧ࡯ࠥ࡯࡭ࡱࡱࡵࡸࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣ࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࢀࡥ࠼ࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠ࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡩ࠭ࢁࡽࠪ࠽ࠣࡪࡷࡵ࡭ࠡࡲࡧࡦࠥ࡯࡭ࡱࡱࡵࡸࠥࡖࡤࡣ࠽ࠣࡳ࡬ࡥࡤࡣࠢࡀࠤࡕࡪࡢ࠯ࡦࡲࡣࡧࡸࡥࡢ࡭࠾ࠎࡩ࡫ࡦࠡ࡯ࡲࡨࡤࡨࡲࡦࡣ࡮ࠬࡸ࡫࡬ࡧ࠮ࠣࡥࡷ࡭ࠬࠡࡶࡨࡱࡵࡵࡲࡢࡴࡼࠤࡂࠦ࠰ࠪ࠼ࠍࠤࠥࡺࡲࡺ࠼ࠍࠤࠥࠦࠠࡢࡴࡪࠤࡂࠦࡳࡵࡴࠫ࡭ࡳࡺࠨࡢࡴࡪ࠭࠰࠷࠰ࠪࠌࠣࠤࡪࡾࡣࡦࡲࡷࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡢࡵࠣࡩ࠿ࠐࠠࠡࠢࠣࡴࡦࡹࡳࠋࠢࠣࡳ࡬ࡥࡤࡣࠪࡶࡩࡱ࡬ࠬࡢࡴࡪ࠰ࡹ࡫࡭ࡱࡱࡵࡥࡷࡿࠩࠋࡒࡧࡦ࠳ࡪ࡯ࡠࡤࠣࡁࠥࡳ࡯ࡥࡡࡥࡶࡪࡧ࡫ࠋࡒࡧࡦ࠳ࡪ࡯ࡠࡤࡵࡩࡦࡱࠠ࠾ࠢࡰࡳࡩࡥࡢࡳࡧࡤ࡯ࠏࡖࡤࡣࠪࠬ࠲ࡸ࡫ࡴࡠࡶࡵࡥࡨ࡫ࠨࠪ࡞ࡱࠦࠧࠨฉ").format(str(bstack1l11l1_opy_))
          bstack1l1l1111l_opy_ = bstack1111lll1l_opy_ + bstack11l1111_opy_
          bstack1111l1_opy_ = bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ช")] + bstack11l1lll1_opy_ (u"ࠫࡤࡨࡳࡵࡣࡦ࡯ࡤࡺࡥ࡮ࡲ࠱ࡴࡾ࠭ซ")
          with open(bstack1111l1_opy_, bstack11l1lll1_opy_ (u"ࠬࡽࠧฌ")):
            pass
          with open(bstack1111l1_opy_, bstack11l1lll1_opy_ (u"ࠨࡷࠬࠤญ")) as f:
            f.write(bstack1l1l1111l_opy_)
          import subprocess
          bstack11111lll_opy_ = subprocess.run([bstack11l1lll1_opy_ (u"ࠢࡱࡻࡷ࡬ࡴࡴࠢฎ"), bstack1111l1_opy_])
          if os.path.exists(bstack1111l1_opy_):
            os.unlink(bstack1111l1_opy_)
          os._exit(bstack11111lll_opy_.returncode)
        else:
          if bstack11l11l1ll_opy_(bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫฏ")]):
            bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬฐ")].remove(bstack11l1lll1_opy_ (u"ࠪ࠱ࡲ࠭ฑ"))
            bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧฒ")].remove(bstack11l1lll1_opy_ (u"ࠬࡶࡤࡣࠩณ"))
            bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩด")] = bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪต")][0]
          bstack1lll1l_opy_(bstack1l11l1l_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫถ")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack11l1lll1_opy_ (u"ࠩࡢࡣࡳࡧ࡭ࡦࡡࡢࠫท")] = bstack11l1lll1_opy_ (u"ࠪࡣࡤࡳࡡࡪࡰࡢࡣࠬธ")
          mod_globals[bstack11l1lll1_opy_ (u"ࠫࡤࡥࡦࡪ࡮ࡨࡣࡤ࠭น")] = os.path.abspath(bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨบ")])
          exec(open(bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩป")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack11l1lll1_opy_ (u"ࠧࡄࡣࡸ࡫࡭ࡺࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰ࠽ࠤࢀࢃࠧผ").format(str(e)))
          for driver in bstack11llll11l_opy_:
            bstack1l1llll11_opy_.append({
              bstack11l1lll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ฝ"): bstack1l11l1_opy_[bstack11l1lll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬพ")],
              bstack11l1lll1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩฟ"): str(e),
              bstack11l1lll1_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪภ"): multiprocessing.current_process().name
            })
            driver.execute_script(
              bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡸࡺࡡࡵࡷࡶࠦ࠿ࠨࡦࡢ࡫࡯ࡩࡩࠨࠬࠡࠤࡵࡩࡦࡹ࡯࡯ࠤ࠽ࠤࠬม") + json.dumps(bstack11l1lll1_opy_ (u"ࠨࡓࡦࡵࡶ࡭ࡴࡴࠠࡧࡣ࡬ࡰࡪࡪࠠࡸ࡫ࡷ࡬࠿ࠦ࡜࡯ࠤย") + str(e)) + bstack11l1lll1_opy_ (u"ࠧࡾࡿࠪร"))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack11llll11l_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      bstack111l1l11_opy_()
      bstack1llll_opy_()
      bstack1l11ll11_opy_ = {
        bstack11l1lll1_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫฤ"): args[0],
        bstack11l1lll1_opy_ (u"ࠩࡆࡓࡓࡌࡉࡈࠩล"): CONFIG,
        bstack11l1lll1_opy_ (u"ࠪࡌ࡚ࡈ࡟ࡖࡔࡏࠫฦ"): bstack1lllll111_opy_,
        bstack11l1lll1_opy_ (u"ࠫࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭ว"): bstack111l1l11l_opy_
      }
      if bstack11l1lll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨศ") in CONFIG:
        bstack1ll1ll1_opy_ = []
        manager = multiprocessing.Manager()
        bstack111ll11_opy_ = manager.list()
        if bstack11l11l1ll_opy_(args):
          for index, platform in enumerate(CONFIG[bstack11l1lll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩษ")]):
            if index == 0:
              bstack1l11ll11_opy_[bstack11l1lll1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪส")] = args
            bstack1ll1ll1_opy_.append(multiprocessing.Process(name=str(index),
                                          target=run_on_browserstack, args=(bstack1l11ll11_opy_, bstack111ll11_opy_)))
        else:
          for index, platform in enumerate(CONFIG[bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫห")]):
            bstack1ll1ll1_opy_.append(multiprocessing.Process(name=str(index),
                                          target=run_on_browserstack, args=(bstack1l11ll11_opy_, bstack111ll11_opy_)))
        for t in bstack1ll1ll1_opy_:
          t.start()
        for t in bstack1ll1ll1_opy_:
          t.join()
        bstack1l1ll1_opy_ = list(bstack111ll11_opy_)
      else:
        if bstack11l11l1ll_opy_(args):
          bstack1l11ll11_opy_[bstack11l1lll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬฬ")] = args
          test = multiprocessing.Process(name=str(0),
                                        target=run_on_browserstack, args=(bstack1l11ll11_opy_,))
          test.start()
          test.join()
        else:
          bstack1lll1l_opy_(bstack1l11l1l_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack11l1lll1_opy_ (u"ࠪࡣࡤࡴࡡ࡮ࡧࡢࡣࠬอ")] = bstack11l1lll1_opy_ (u"ࠫࡤࡥ࡭ࡢ࡫ࡱࡣࡤ࠭ฮ")
          mod_globals[bstack11l1lll1_opy_ (u"ࠬࡥ࡟ࡧ࡫࡯ࡩࡤࡥࠧฯ")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack1ll1llll1_opy_ == bstack11l1lll1_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬะ") or bstack1ll1llll1_opy_ == bstack11l1lll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ั"):
    try:
      from pabot import pabot
    except Exception as e:
      bstack111ll1l11_opy_(e, bstack11l111lll_opy_)
    bstack111l1l11_opy_()
    bstack1lll1l_opy_(bstack1l1111ll_opy_)
    if bstack11l1lll1_opy_ (u"ࠨ࠯࠰ࡴࡷࡵࡣࡦࡵࡶࡩࡸ࠭า") in args:
      i = args.index(bstack11l1lll1_opy_ (u"ࠩ࠰࠱ࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠧำ"))
      args.pop(i)
      args.pop(i)
    args.insert(0, str(bstack1111lll1_opy_))
    args.insert(0, str(bstack11l1lll1_opy_ (u"ࠪ࠱࠲ࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨิ")))
    pabot.main(args)
  elif bstack1ll1llll1_opy_ == bstack11l1lll1_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬี"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack111ll1l11_opy_(e, bstack11l111lll_opy_)
    for a in args:
      if bstack11l1lll1_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡕࡒࡁࡕࡈࡒࡖࡒࡏࡎࡅࡇ࡛ࠫึ") in a:
        bstack11llll1l_opy_ = int(a.split(bstack11l1lll1_opy_ (u"࠭࠺ࠨื"))[1])
      if bstack11l1lll1_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕุࠫ") in a:
        bstack1l11_opy_ = str(a.split(bstack11l1lll1_opy_ (u"ࠨ࠼ูࠪ"))[1])
      if bstack11l1lll1_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡅࡏࡍࡆࡘࡇࡔฺࠩ") in a:
        bstack11l11l11_opy_ = str(a.split(bstack11l1lll1_opy_ (u"ࠪ࠾ࠬ฻"))[1])
    bstack11ll1ll11_opy_ = None
    if bstack11l1lll1_opy_ (u"ࠫ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡩࡵࡧࡰࡣ࡮ࡴࡤࡦࡺࠪ฼") in args:
      i = args.index(bstack11l1lll1_opy_ (u"ࠬ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡪࡶࡨࡱࡤ࡯࡮ࡥࡧࡻࠫ฽"))
      args.pop(i)
      bstack11ll1ll11_opy_ = args.pop(i)
    if bstack11ll1ll11_opy_ is not None:
      global bstack11lll111_opy_
      bstack11lll111_opy_ = bstack11ll1ll11_opy_
    bstack1lll1l_opy_(bstack1l1111ll_opy_)
    run_cli(args)
  elif bstack1ll1llll1_opy_ == bstack11l1lll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭฾"):
    try:
      from _pytest.config import _prepareconfig
      from _pytest.config import Config
      from _pytest import runner
      import importlib
      bstack11l11l1_opy_ = importlib.find_loader(bstack11l1lll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠩ฿"))
    except Exception as e:
      logger.warn(e, bstack1l111ll1_opy_)
    bstack111l1l11_opy_()
    try:
      if bstack11l1lll1_opy_ (u"ࠨ࠯࠰ࡨࡷ࡯ࡶࡦࡴࠪเ") in args:
        i = args.index(bstack11l1lll1_opy_ (u"ࠩ࠰࠱ࡩࡸࡩࡷࡧࡵࠫแ"))
        args.pop(i+1)
        args.pop(i)
      if bstack11l1lll1_opy_ (u"ࠪ࠱࠲ࡶ࡬ࡶࡩ࡬ࡲࡸ࠭โ") in args:
        i = args.index(bstack11l1lll1_opy_ (u"ࠫ࠲࠳ࡰ࡭ࡷࡪ࡭ࡳࡹࠧใ"))
        args.pop(i+1)
        args.pop(i)
      if bstack11l1lll1_opy_ (u"ࠬ࠳ࡰࠨไ") in args:
        i = args.index(bstack11l1lll1_opy_ (u"࠭࠭ࡱࠩๅ"))
        args.pop(i+1)
        args.pop(i)
      if bstack11l1lll1_opy_ (u"ࠧ࠮࠯ࡱࡹࡲࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨๆ") in args:
        i = args.index(bstack11l1lll1_opy_ (u"ࠨ࠯࠰ࡲࡺࡳࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩ็"))
        args.pop(i+1)
        args.pop(i)
      if bstack11l1lll1_opy_ (u"ࠩ࠰ࡲ่ࠬ") in args:
        i = args.index(bstack11l1lll1_opy_ (u"ࠪ࠱ࡳ้࠭"))
        args.pop(i+1)
        args.pop(i)
    except Exception as exc:
      logger.error(str(exc))
    config = _prepareconfig(args)
    bstack11l1l111_opy_ = config.args
    bstack11l_opy_ = config.invocation_params.args
    bstack11l_opy_ = list(bstack11l_opy_)
    bstack11ll1l11l_opy_ = [os.path.normpath(item) for item in bstack11l1l111_opy_]
    bstack1l11l11ll_opy_ = [os.path.normpath(item) for item in bstack11l_opy_]
    bstack1l11llll_opy_ = [item for item in bstack1l11l11ll_opy_ if item not in bstack11ll1l11l_opy_]
    if bstack11l1lll1_opy_ (u"ࠫ࠲࠳ࡣࡢࡥ࡫ࡩ࠲ࡩ࡬ࡦࡣࡵ๊ࠫ") not in bstack1l11llll_opy_:
      bstack1l11llll_opy_.append(bstack11l1lll1_opy_ (u"ࠬ࠳࠭ࡤࡣࡦ࡬ࡪ࠳ࡣ࡭ࡧࡤࡶ๋ࠬ"))
    import platform as pf
    if pf.system().lower() == bstack11l1lll1_opy_ (u"࠭ࡷࡪࡰࡧࡳࡼࡹࠧ์"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack11l1l111_opy_ = [str(PurePosixPath(PureWindowsPath(bstack1l1l_opy_)))
                    for bstack1l1l_opy_ in bstack11l1l111_opy_]
    if (bstack1ll11l1ll_opy_):
      bstack1l11llll_opy_.append(bstack11l1lll1_opy_ (u"ࠧ࠮࠯ࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫํ"))
      bstack1l11llll_opy_.append(bstack11l1lll1_opy_ (u"ࠨࡖࡵࡹࡪ࠭๎"))
    try:
      from pytest_bdd import reporting
      bstack1llll11l1_opy_ = True
    except Exception as e:
      pass
    if (not bstack1llll11l1_opy_):
      bstack1l11llll_opy_.append(bstack11l1lll1_opy_ (u"ࠩ࠰ࡴࠬ๏"))
      bstack1l11llll_opy_.append(bstack11l1lll1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࡢࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡲ࡯ࡹ࡬࡯࡮ࠨ๐"))
    bstack1l11llll_opy_.append(bstack11l1lll1_opy_ (u"ࠫ࠲࠳ࡤࡳ࡫ࡹࡩࡷ࠭๑"))
    bstack1l11llll_opy_.append(bstack11l1lll1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬ๒"))
    bstack1ll1l11l1_opy_ = []
    for spec in bstack11l1l111_opy_:
      bstack11l1l1l_opy_ = []
      bstack11l1l1l_opy_.append(spec)
      bstack11l1l1l_opy_ += bstack1l11llll_opy_
      bstack1ll1l11l1_opy_.append(bstack11l1l1l_opy_)
    bstack1l1l1ll_opy_ = True
    bstack1ll11l1l1_opy_ = 1
    if bstack11l1lll1_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭๓") in CONFIG:
      bstack1ll11l1l1_opy_ = CONFIG[bstack11l1lll1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ๔")]
    bstack1l1l1lll_opy_ = int(bstack1ll11l1l1_opy_)*int(len(CONFIG[bstack11l1lll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ๕")]))
    execution_items = []
    for bstack11l1l1l_opy_ in bstack1ll1l11l1_opy_:
      for index, _ in enumerate(CONFIG[bstack11l1lll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ๖")]):
        item = {}
        item[bstack11l1lll1_opy_ (u"ࠪࡥࡷ࡭ࠧ๗")] = bstack11l1l1l_opy_
        item[bstack11l1lll1_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪ๘")] = index
        execution_items.append(item)
    bstack1l1lll_opy_ = bstack1l1ll111_opy_(execution_items, bstack1l1l1lll_opy_)
    for execution_item in bstack1l1lll_opy_:
      bstack1ll1ll1_opy_ = []
      for item in execution_item:
        bstack1ll1ll1_opy_.append(bstack1l1llllll_opy_(name=str(item[bstack11l1lll1_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫ๙")]),
                                            target=bstack11lll1l11_opy_,
                                            args=(item[bstack11l1lll1_opy_ (u"࠭ࡡࡳࡩࠪ๚")],)))
      for t in bstack1ll1ll1_opy_:
        t.start()
      for t in bstack1ll1ll1_opy_:
        t.join()
  elif bstack1ll1llll1_opy_ == bstack11l1lll1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧ๛"):
    try:
      from behave.__main__ import main as bstack1l111111l_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack111ll1l11_opy_(e, bstack111lll11_opy_)
    bstack111l1l11_opy_()
    bstack1l1l1ll_opy_ = True
    bstack1ll11l1l1_opy_ = 1
    if bstack11l1lll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ๜") in CONFIG:
      bstack1ll11l1l1_opy_ = CONFIG[bstack11l1lll1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ๝")]
    bstack1l1l1lll_opy_ = int(bstack1ll11l1l1_opy_)*int(len(CONFIG[bstack11l1lll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭๞")]))
    config = Configuration(args)
    bstack1l11l1l1l_opy_ = config.paths
    if len(bstack1l11l1l1l_opy_) == 0:
      import glob
      pattern = bstack11l1lll1_opy_ (u"ࠫ࠯࠰࠯ࠫ࠰ࡩࡩࡦࡺࡵࡳࡧࠪ๟")
      bstack11lllll1_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack11lllll1_opy_)
      config = Configuration(args)
      bstack1l11l1l1l_opy_ = config.paths
    bstack11l1l111_opy_ = [os.path.normpath(item) for item in bstack1l11l1l1l_opy_]
    bstack1l1l11_opy_ = [os.path.normpath(item) for item in args]
    bstack111ll1_opy_ = [item for item in bstack1l1l11_opy_ if item not in bstack11l1l111_opy_]
    import platform as pf
    if pf.system().lower() == bstack11l1lll1_opy_ (u"ࠬࡽࡩ࡯ࡦࡲࡻࡸ࠭๠"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack11l1l111_opy_ = [str(PurePosixPath(PureWindowsPath(bstack1l1l_opy_)))
                    for bstack1l1l_opy_ in bstack11l1l111_opy_]
    bstack1ll1l11l1_opy_ = []
    for spec in bstack11l1l111_opy_:
      bstack11l1l1l_opy_ = []
      bstack11l1l1l_opy_ += bstack111ll1_opy_
      bstack11l1l1l_opy_.append(spec)
      bstack1ll1l11l1_opy_.append(bstack11l1l1l_opy_)
    execution_items = []
    for bstack11l1l1l_opy_ in bstack1ll1l11l1_opy_:
      for index, _ in enumerate(CONFIG[bstack11l1lll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ๡")]):
        item = {}
        item[bstack11l1lll1_opy_ (u"ࠧࡢࡴࡪࠫ๢")] = bstack11l1lll1_opy_ (u"ࠨࠢࠪ๣").join(bstack11l1l1l_opy_)
        item[bstack11l1lll1_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨ๤")] = index
        execution_items.append(item)
    bstack1l1lll_opy_ = bstack1l1ll111_opy_(execution_items, bstack1l1l1lll_opy_)
    for execution_item in bstack1l1lll_opy_:
      bstack1ll1ll1_opy_ = []
      for item in execution_item:
        bstack1ll1ll1_opy_.append(bstack1l1llllll_opy_(name=str(item[bstack11l1lll1_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩ๥")]),
                                            target=bstack1ll11111l_opy_,
                                            args=(item[bstack11l1lll1_opy_ (u"ࠫࡦࡸࡧࠨ๦")],)))
      for t in bstack1ll1ll1_opy_:
        t.start()
      for t in bstack1ll1ll1_opy_:
        t.join()
  else:
    bstack1lll1l1l_opy_(bstack1lll1l1ll_opy_)
  if not bstack1l11l1_opy_:
    bstack11ll11l_opy_()
def browserstack_initialize(bstack11ll1l1l_opy_=None):
  run_on_browserstack(bstack11ll1l1l_opy_, None, True)
def bstack11ll11l_opy_():
  [bstack111lll_opy_, bstack11l11l1l1_opy_] = bstack11l11l11l_opy_()
  if bstack111lll_opy_ is not None and bstack11l11llll_opy_() != -1:
    sessions = bstack1lll1ll_opy_(bstack111lll_opy_)
    bstack1ll11l11_opy_(sessions, bstack11l11l1l1_opy_)
def bstack1llllll1_opy_(bstack11l1l1lll_opy_):
    if bstack11l1l1lll_opy_:
        return bstack11l1l1lll_opy_.capitalize()
    else:
        return bstack11l1l1lll_opy_
def bstack1l1ll11l1_opy_(bstack1l111l1l1_opy_):
    if bstack11l1lll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ๧") in bstack1l111l1l1_opy_ and bstack1l111l1l1_opy_[bstack11l1lll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ๨")] != bstack11l1lll1_opy_ (u"ࠧࠨ๩"):
        return bstack1l111l1l1_opy_[bstack11l1lll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭๪")]
    else:
        bstack1ll11l_opy_ = bstack11l1lll1_opy_ (u"ࠤࠥ๫")
        if bstack11l1lll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪ๬") in bstack1l111l1l1_opy_ and bstack1l111l1l1_opy_[bstack11l1lll1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫ๭")] != None:
            bstack1ll11l_opy_ += bstack1l111l1l1_opy_[bstack11l1lll1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬ๮")] + bstack11l1lll1_opy_ (u"ࠨࠬࠡࠤ๯")
            if bstack1l111l1l1_opy_[bstack11l1lll1_opy_ (u"ࠧࡰࡵࠪ๰")] == bstack11l1lll1_opy_ (u"ࠣ࡫ࡲࡷࠧ๱"):
                bstack1ll11l_opy_ += bstack11l1lll1_opy_ (u"ࠤ࡬ࡓࡘࠦࠢ๲")
            bstack1ll11l_opy_ += (bstack1l111l1l1_opy_[bstack11l1lll1_opy_ (u"ࠪࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ๳")] or bstack11l1lll1_opy_ (u"ࠫࠬ๴"))
            return bstack1ll11l_opy_
        else:
            bstack1ll11l_opy_ += bstack1llllll1_opy_(bstack1l111l1l1_opy_[bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࠭๵")]) + bstack11l1lll1_opy_ (u"ࠨࠠࠣ๶") + (bstack1l111l1l1_opy_[bstack11l1lll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ๷")] or bstack11l1lll1_opy_ (u"ࠨࠩ๸")) + bstack11l1lll1_opy_ (u"ࠤ࠯ࠤࠧ๹")
            if bstack1l111l1l1_opy_[bstack11l1lll1_opy_ (u"ࠪࡳࡸ࠭๺")] == bstack11l1lll1_opy_ (u"ࠦ࡜࡯࡮ࡥࡱࡺࡷࠧ๻"):
                bstack1ll11l_opy_ += bstack11l1lll1_opy_ (u"ࠧ࡝ࡩ࡯ࠢࠥ๼")
            bstack1ll11l_opy_ += bstack1l111l1l1_opy_[bstack11l1lll1_opy_ (u"࠭࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠪ๽")] or bstack11l1lll1_opy_ (u"ࠧࠨ๾")
            return bstack1ll11l_opy_
def bstack11lll1l_opy_(bstack11l111ll1_opy_):
    if bstack11l111ll1_opy_ == bstack11l1lll1_opy_ (u"ࠣࡦࡲࡲࡪࠨ๿"):
        return bstack11l1lll1_opy_ (u"ࠩ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾࡬ࡸࡥࡦࡰ࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦ࡬ࡸࡥࡦࡰࠥࡂࡈࡵ࡭ࡱ࡮ࡨࡸࡪࡪ࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬ຀")
    elif bstack11l111ll1_opy_ == bstack11l1lll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥກ"):
        return bstack11l1lll1_opy_ (u"ࠫࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࡲࡦࡦ࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦࡷ࡫ࡤࠣࡀࡉࡥ࡮ࡲࡥࡥ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧຂ")
    elif bstack11l111ll1_opy_ == bstack11l1lll1_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧ຃"):
        return bstack11l1lll1_opy_ (u"࠭࠼ࡵࡦࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࡩࡵࡩࡪࡴ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡩࡵࡩࡪࡴࠢ࠿ࡒࡤࡷࡸ࡫ࡤ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ຄ")
    elif bstack11l111ll1_opy_ == bstack11l1lll1_opy_ (u"ࠢࡦࡴࡵࡳࡷࠨ຅"):
        return bstack11l1lll1_opy_ (u"ࠨ࠾ࡷࡨࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽ࡶࡪࡪ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡴࡨࡨࠧࡄࡅࡳࡴࡲࡶࡁ࠵ࡦࡰࡰࡷࡂࡁ࠵ࡴࡥࡀࠪຆ")
    elif bstack11l111ll1_opy_ == bstack11l1lll1_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࠥງ"):
        return bstack11l1lll1_opy_ (u"ࠪࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿ࠩࡥࡦࡣ࠶࠶࠻ࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࠤࡧࡨࡥ࠸࠸࠶ࠣࡀࡗ࡭ࡲ࡫࡯ࡶࡶ࠿࠳࡫ࡵ࡮ࡵࡀ࠿࠳ࡹࡪ࠾ࠨຈ")
    elif bstack11l111ll1_opy_ == bstack11l1lll1_opy_ (u"ࠦࡷࡻ࡮࡯࡫ࡱ࡫ࠧຉ"):
        return bstack11l1lll1_opy_ (u"ࠬࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࡣ࡮ࡤࡧࡰࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࡣ࡮ࡤࡧࡰࠨ࠾ࡓࡷࡱࡲ࡮ࡴࡧ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ຊ")
    else:
        return bstack11l1lll1_opy_ (u"࠭࠼ࡵࡦࠣࡥࡱ࡯ࡧ࡯࠿ࠥࡧࡪࡴࡴࡦࡴࠥࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࡥࡰࡦࡩ࡫࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࡥࡰࡦࡩ࡫ࠣࡀࠪ຋")+bstack1llllll1_opy_(bstack11l111ll1_opy_)+bstack11l1lll1_opy_ (u"ࠧ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ຌ")
def bstack1ll1ll_opy_(session):
    return bstack11l1lll1_opy_ (u"ࠨ࠾ࡷࡶࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡸ࡯ࡸࠤࡁࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠥࡹࡥࡴࡵ࡬ࡳࡳ࠳࡮ࡢ࡯ࡨࠦࡃࡂࡡࠡࡪࡵࡩ࡫ࡃࠢࡼࡿࠥࠤࡹࡧࡲࡨࡧࡷࡁࠧࡥࡢ࡭ࡣࡱ࡯ࠧࡄࡻࡾ࠾࠲ࡥࡃࡂ࠯ࡵࡦࡁࡿࢂࢁࡽ࠽ࡶࡧࠤࡦࡲࡩࡨࡰࡀࠦࡨ࡫࡮ࡵࡧࡵࠦࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࡂࢀࢃ࠼࠰ࡶࡧࡂࡁࡺࡤࠡࡣ࡯࡭࡬ࡴ࠽ࠣࡥࡨࡲࡹ࡫ࡲࠣࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢ࠿ࡽࢀࡀ࠴ࡺࡤ࠿࠾ࡷࡨࠥࡧ࡬ࡪࡩࡱࡁࠧࡩࡥ࡯ࡶࡨࡶࠧࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࡃࢁࡽ࠽࠱ࡷࡨࡃࡂࡴࡥࠢࡤࡰ࡮࡭࡮࠾ࠤࡦࡩࡳࡺࡥࡳࠤࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࡀࡾࢁࡁ࠵ࡴࡥࡀ࠿࠳ࡹࡸ࠾ࠨຍ").format(session[bstack11l1lll1_opy_ (u"ࠩࡳࡹࡧࡲࡩࡤࡡࡸࡶࡱ࠭ຎ")],bstack1l1ll11l1_opy_(session), bstack11lll1l_opy_(session[bstack11l1lll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡶࡸࡦࡺࡵࡴࠩຏ")]), bstack11lll1l_opy_(session[bstack11l1lll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫຐ")]), bstack1llllll1_opy_(session[bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࠭ຑ")] or session[bstack11l1lll1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭ຒ")] or bstack11l1lll1_opy_ (u"ࠧࠨຓ")) + bstack11l1lll1_opy_ (u"ࠣࠢࠥດ") + (session[bstack11l1lll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫຕ")] or bstack11l1lll1_opy_ (u"ࠪࠫຖ")), session[bstack11l1lll1_opy_ (u"ࠫࡴࡹࠧທ")] + bstack11l1lll1_opy_ (u"ࠧࠦࠢຘ") + session[bstack11l1lll1_opy_ (u"࠭࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠪນ")], session[bstack11l1lll1_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࠩບ")] or bstack11l1lll1_opy_ (u"ࠨࠩປ"), session[bstack11l1lll1_opy_ (u"ࠩࡦࡶࡪࡧࡴࡦࡦࡢࡥࡹ࠭ຜ")] if session[bstack11l1lll1_opy_ (u"ࠪࡧࡷ࡫ࡡࡵࡧࡧࡣࡦࡺࠧຝ")] else bstack11l1lll1_opy_ (u"ࠫࠬພ"))
def bstack1ll11l11_opy_(sessions, bstack11l11l1l1_opy_):
  try:
    bstack1ll11lll1_opy_ = bstack11l1lll1_opy_ (u"ࠧࠨຟ")
    if not os.path.exists(bstack11lll1lll_opy_):
      os.mkdir(bstack11lll1lll_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11l1lll1_opy_ (u"࠭ࡡࡴࡵࡨࡸࡸ࠵ࡲࡦࡲࡲࡶࡹ࠴ࡨࡵ࡯࡯ࠫຠ")), bstack11l1lll1_opy_ (u"ࠧࡳࠩມ")) as f:
      bstack1ll11lll1_opy_ = f.read()
    bstack1ll11lll1_opy_ = bstack1ll11lll1_opy_.replace(bstack11l1lll1_opy_ (u"ࠨࡽࠨࡖࡊ࡙ࡕࡍࡖࡖࡣࡈࡕࡕࡏࡖࠨࢁࠬຢ"), str(len(sessions)))
    bstack1ll11lll1_opy_ = bstack1ll11lll1_opy_.replace(bstack11l1lll1_opy_ (u"ࠩࡾࠩࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠥࡾࠩຣ"), bstack11l11l1l1_opy_)
    bstack1ll11lll1_opy_ = bstack1ll11lll1_opy_.replace(bstack11l1lll1_opy_ (u"ࠪࡿࠪࡈࡕࡊࡎࡇࡣࡓࡇࡍࡆࠧࢀࠫ຤"), sessions[0].get(bstack11l1lll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢࡲࡦࡳࡥࠨລ")) if sessions[0] else bstack11l1lll1_opy_ (u"ࠬ࠭຦"))
    with open(os.path.join(bstack11lll1lll_opy_, bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠲ࡸࡥࡱࡱࡵࡸ࠳࡮ࡴ࡮࡮ࠪວ")), bstack11l1lll1_opy_ (u"ࠧࡸࠩຨ")) as stream:
      stream.write(bstack1ll11lll1_opy_.split(bstack11l1lll1_opy_ (u"ࠨࡽࠨࡗࡊ࡙ࡓࡊࡑࡑࡗࡤࡊࡁࡕࡃࠨࢁࠬຩ"))[0])
      for session in sessions:
        stream.write(bstack1ll1ll_opy_(session))
      stream.write(bstack1ll11lll1_opy_.split(bstack11l1lll1_opy_ (u"ࠩࡾࠩࡘࡋࡓࡔࡋࡒࡒࡘࡥࡄࡂࡖࡄࠩࢂ࠭ສ"))[1])
    logger.info(bstack11l1lll1_opy_ (u"ࠪࡋࡪࡴࡥࡳࡣࡷࡩࡩࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡨࡵࡪ࡮ࡧࠤࡦࡸࡴࡪࡨࡤࡧࡹࡹࠠࡢࡶࠣࡿࢂ࠭ຫ").format(bstack11lll1lll_opy_));
  except Exception as e:
    logger.debug(bstack11lll_opy_.format(str(e)))
def bstack1lll1ll_opy_(bstack111lll_opy_):
  global CONFIG
  try:
    host = bstack11l1lll1_opy_ (u"ࠫࡦࡶࡩ࠮ࡥ࡯ࡳࡺࡪࠧຬ") if bstack11l1lll1_opy_ (u"ࠬࡧࡰࡱࠩອ") in CONFIG else bstack11l1lll1_opy_ (u"࠭ࡡࡱ࡫ࠪຮ")
    user = CONFIG[bstack11l1lll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩຯ")]
    key = CONFIG[bstack11l1lll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫະ")]
    bstack1ll1_opy_ = bstack11l1lll1_opy_ (u"ࠩࡤࡴࡵ࠳ࡡࡶࡶࡲࡱࡦࡺࡥࠨັ") if bstack11l1lll1_opy_ (u"ࠪࡥࡵࡶࠧາ") in CONFIG else bstack11l1lll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ຳ")
    url = bstack11l1lll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡻࡾ࠼ࡾࢁࡅࢁࡽ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࢀࢃ࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿ࠲ࡷࡪࡹࡳࡪࡱࡱࡷ࠳ࡰࡳࡰࡰࠪິ").format(user, key, host, bstack1ll1_opy_, bstack111lll_opy_)
    headers = {
      bstack11l1lll1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡵࡻࡳࡩࠬີ"): bstack11l1lll1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪຶ"),
    }
    proxies = bstack11ll1l1l1_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.json():
      return list(map(lambda session: session[bstack11l1lll1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ື")], response.json()))
  except Exception as e:
    logger.debug(bstack11l1lll11_opy_.format(str(e)))
def bstack11l11l11l_opy_():
  global CONFIG
  try:
    if bstack11l1lll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩຸࠬ") in CONFIG:
      host = bstack11l1lll1_opy_ (u"ࠪࡥࡵ࡯࠭ࡤ࡮ࡲࡹࡩູ࠭") if bstack11l1lll1_opy_ (u"ࠫࡦࡶࡰࠨ຺") in CONFIG else bstack11l1lll1_opy_ (u"ࠬࡧࡰࡪࠩົ")
      user = CONFIG[bstack11l1lll1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨຼ")]
      key = CONFIG[bstack11l1lll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪຽ")]
      bstack1ll1_opy_ = bstack11l1lll1_opy_ (u"ࠨࡣࡳࡴ࠲ࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ຾") if bstack11l1lll1_opy_ (u"ࠩࡤࡴࡵ࠭຿") in CONFIG else bstack11l1lll1_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩࠬເ")
      url = bstack11l1lll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࢁࡽ࠻ࡽࢀࡄࢀࢃ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡿࢂ࠵ࡢࡶ࡫࡯ࡨࡸ࠴ࡪࡴࡱࡱࠫແ").format(user, key, host, bstack1ll1_opy_)
      headers = {
        bstack11l1lll1_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡴࡺࡲࡨࠫໂ"): bstack11l1lll1_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩໃ"),
      }
      if bstack11l1lll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩໄ") in CONFIG:
        params = {bstack11l1lll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭໅"):CONFIG[bstack11l1lll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬໆ")], bstack11l1lll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭໇"):CONFIG[bstack11l1lll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ່࠭")]}
      else:
        params = {bstack11l1lll1_opy_ (u"ࠬࡴࡡ࡮ࡧ້ࠪ"):CONFIG[bstack11l1lll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦ໊ࠩ")]}
      proxies = bstack11ll1l1l1_opy_(CONFIG, url)
      response = requests.get(url, params=params, headers=headers, proxies=proxies)
      if response.json():
        bstack1l1lll1l1_opy_ = response.json()[0][bstack11l1lll1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡧࡻࡩ࡭ࡦ໋ࠪ")]
        if bstack1l1lll1l1_opy_:
          bstack11l11l1l1_opy_ = bstack1l1lll1l1_opy_[bstack11l1lll1_opy_ (u"ࠨࡲࡸࡦࡱ࡯ࡣࡠࡷࡵࡰࠬ໌")].split(bstack11l1lll1_opy_ (u"ࠩࡳࡹࡧࡲࡩࡤ࠯ࡥࡹ࡮ࡲࡤࠨໍ"))[0] + bstack11l1lll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡵ࠲ࠫ໎") + bstack1l1lll1l1_opy_[bstack11l1lll1_opy_ (u"ࠫ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ໏")]
          logger.info(bstack1111l_opy_.format(bstack11l11l1l1_opy_))
          bstack11l1l1l1l_opy_ = CONFIG[bstack11l1lll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ໐")]
          if bstack11l1lll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ໑") in CONFIG:
            bstack11l1l1l1l_opy_ += bstack11l1lll1_opy_ (u"ࠧࠡࠩ໒") + CONFIG[bstack11l1lll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ໓")]
          if bstack11l1l1l1l_opy_!= bstack1l1lll1l1_opy_[bstack11l1lll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ໔")]:
            logger.debug(bstack1ll1l1l_opy_.format(bstack1l1lll1l1_opy_[bstack11l1lll1_opy_ (u"ࠪࡲࡦࡳࡥࠨ໕")], bstack11l1l1l1l_opy_))
          return [bstack1l1lll1l1_opy_[bstack11l1lll1_opy_ (u"ࠫ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ໖")], bstack11l11l1l1_opy_]
    else:
      logger.warn(bstack1l11lllll_opy_)
  except Exception as e:
    logger.debug(bstack1111l11_opy_.format(str(e)))
  return [None, None]
def bstack1lll11ll1_opy_(url, bstack11l1ll11_opy_=False):
  global CONFIG
  global bstack1l1111l1_opy_
  if not bstack1l1111l1_opy_:
    hostname = bstack1llll1111_opy_(url)
    is_private = bstack11111ll1_opy_(hostname)
    if (bstack11l1lll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ໗") in CONFIG and not CONFIG[bstack11l1lll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ໘")]) and (is_private or bstack11l1ll11_opy_):
      bstack1l1111l1_opy_ = hostname
def bstack1llll1111_opy_(url):
  return urlparse(url).hostname
def bstack11111ll1_opy_(hostname):
  for bstack111l1_opy_ in bstack1lll111l1_opy_:
    regex = re.compile(bstack111l1_opy_)
    if regex.match(hostname):
      return True
  return False
def bstack1ll1ll111_opy_(key_name):
  return True if key_name in threading.current_thread().__dict__.keys() else False