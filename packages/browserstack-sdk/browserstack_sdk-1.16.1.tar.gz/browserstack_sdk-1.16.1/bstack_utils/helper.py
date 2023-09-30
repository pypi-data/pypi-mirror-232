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
import os
import re
import subprocess
import git
import requests
from bstack_utils.config import Config
from bstack_utils.constants import bstack1ll11l11l1_opy_
from bstack_utils.proxy import bstack1l1l1111_opy_
bstack1l11l1ll1_opy_ = Config.get_instance()
def bstack1ll1111ll1_opy_(config):
    return config[bstack1l1l11l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ໸")]
def bstack1l1llll111_opy_(config):
    return config[bstack1l1l11l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ໹")]
def bstack1ll111ll11_opy_(obj):
    values = []
    bstack1l1lll1lll_opy_ = re.compile(bstack1l1l11l_opy_ (u"ࡷࠨ࡞ࡄࡗࡖࡘࡔࡓ࡟ࡕࡃࡊࡣࡡࡪࠫࠥࠤ໺"), re.I)
    for key in obj.keys():
        if bstack1l1lll1lll_opy_.match(key):
            values.append(obj[key])
    return values
def bstack1l1lll1ll1_opy_(config):
    tags = []
    tag = config.get(bstack1l1l11l_opy_ (u"ࠨࡣࡶࡵࡷࡳࡲ࡚ࡡࡨࠤ໻")) or os.environ.get(bstack1l1l11l_opy_ (u"ࠢࡄࡗࡖࡘࡔࡓ࡟ࡕࡃࡊࠦ໼"))
    if tag:
        tags.append(tag)
    tags.extend(bstack1ll111ll11_opy_(os.environ))
    tags.extend(bstack1ll111ll11_opy_(config))
    return tags
def bstack1ll11111l1_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack1ll111l111_opy_(bstack1l1lll11ll_opy_):
    if not bstack1l1lll11ll_opy_:
        return bstack1l1l11l_opy_ (u"ࠨࠩ໽")
    return bstack1l1l11l_opy_ (u"ࠤࡾࢁࠥ࠮ࡻࡾࠫࠥ໾").format(bstack1l1lll11ll_opy_.name, bstack1l1lll11ll_opy_.email)
def bstack1l1llll1ll_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack1l1lll1l1l_opy_ = repo.common_dir
        info = {
            bstack1l1l11l_opy_ (u"ࠥࡷ࡭ࡧࠢ໿"): repo.head.commit.hexsha,
            bstack1l1l11l_opy_ (u"ࠦࡸ࡮࡯ࡳࡶࡢࡷ࡭ࡧࠢༀ"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack1l1l11l_opy_ (u"ࠧࡨࡲࡢࡰࡦ࡬ࠧ༁"): repo.active_branch.name,
            bstack1l1l11l_opy_ (u"ࠨࡴࡢࡩࠥ༂"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack1l1l11l_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡴࡦࡴࠥ༃"): bstack1ll111l111_opy_(repo.head.commit.committer),
            bstack1l1l11l_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡵࡧࡵࡣࡩࡧࡴࡦࠤ༄"): repo.head.commit.committed_datetime.isoformat(),
            bstack1l1l11l_opy_ (u"ࠤࡤࡹࡹ࡮࡯ࡳࠤ༅"): bstack1ll111l111_opy_(repo.head.commit.author),
            bstack1l1l11l_opy_ (u"ࠥࡥࡺࡺࡨࡰࡴࡢࡨࡦࡺࡥࠣ༆"): repo.head.commit.authored_datetime.isoformat(),
            bstack1l1l11l_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡣࡲ࡫ࡳࡴࡣࡪࡩࠧ༇"): repo.head.commit.message,
            bstack1l1l11l_opy_ (u"ࠧࡸ࡯ࡰࡶࠥ༈"): repo.git.rev_parse(bstack1l1l11l_opy_ (u"ࠨ࠭࠮ࡵ࡫ࡳࡼ࠳ࡴࡰࡲ࡯ࡩࡻ࡫࡬ࠣ༉")),
            bstack1l1l11l_opy_ (u"ࠢࡤࡱࡰࡱࡴࡴ࡟ࡨ࡫ࡷࡣࡩ࡯ࡲࠣ༊"): bstack1l1lll1l1l_opy_,
            bstack1l1l11l_opy_ (u"ࠣࡹࡲࡶࡰࡺࡲࡦࡧࡢ࡫࡮ࡺ࡟ࡥ࡫ࡵࠦ་"): subprocess.check_output([bstack1l1l11l_opy_ (u"ࠤࡪ࡭ࡹࠨ༌"), bstack1l1l11l_opy_ (u"ࠥࡶࡪࡼ࠭ࡱࡣࡵࡷࡪࠨ།"), bstack1l1l11l_opy_ (u"ࠦ࠲࠳ࡧࡪࡶ࠰ࡧࡴࡳ࡭ࡰࡰ࠰ࡨ࡮ࡸࠢ༎")]).strip().decode(
                bstack1l1l11l_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫ༏")),
            bstack1l1l11l_opy_ (u"ࠨ࡬ࡢࡵࡷࡣࡹࡧࡧࠣ༐"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack1l1l11l_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡳࡠࡵ࡬ࡲࡨ࡫࡟࡭ࡣࡶࡸࡤࡺࡡࡨࠤ༑"): repo.git.rev_list(
                bstack1l1l11l_opy_ (u"ࠣࡽࢀ࠲࠳ࢁࡽࠣ༒").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack1ll11111ll_opy_ = []
        for remote in remotes:
            bstack1ll111111l_opy_ = {
                bstack1l1l11l_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ༓"): remote.name,
                bstack1l1l11l_opy_ (u"ࠥࡹࡷࡲࠢ༔"): remote.url,
            }
            bstack1ll11111ll_opy_.append(bstack1ll111111l_opy_)
        return {
            bstack1l1l11l_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ༕"): bstack1l1l11l_opy_ (u"ࠧ࡭ࡩࡵࠤ༖"),
            **info,
            bstack1l1l11l_opy_ (u"ࠨࡲࡦ࡯ࡲࡸࡪࡹࠢ༗"): bstack1ll11111ll_opy_
        }
    except Exception as err:
        print(bstack1l1l11l_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡰࡲࡸࡰࡦࡺࡩ࡯ࡩࠣࡋ࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡺ࡭ࡹ࡮ࠠࡦࡴࡵࡳࡷࡀࠠࡼࡿ༘ࠥ").format(err))
        return {}
def bstack1ll1111lll_opy_():
    env = os.environ
    if (bstack1l1l11l_opy_ (u"ࠣࡌࡈࡒࡐࡏࡎࡔࡡࡘࡖࡑࠨ༙") in env and len(env[bstack1l1l11l_opy_ (u"ࠤࡍࡉࡓࡑࡉࡏࡕࡢ࡙ࡗࡒࠢ༚")]) > 0) or (
            bstack1l1l11l_opy_ (u"ࠥࡎࡊࡔࡋࡊࡐࡖࡣࡍࡕࡍࡆࠤ༛") in env and len(env[bstack1l1l11l_opy_ (u"ࠦࡏࡋࡎࡌࡋࡑࡗࡤࡎࡏࡎࡇࠥ༜")]) > 0):
        return {
            bstack1l1l11l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥ༝"): bstack1l1l11l_opy_ (u"ࠨࡊࡦࡰ࡮࡭ࡳࡹࠢ༞"),
            bstack1l1l11l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥ༟"): env.get(bstack1l1l11l_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦ༠")),
            bstack1l1l11l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦ༡"): env.get(bstack1l1l11l_opy_ (u"ࠥࡎࡔࡈ࡟ࡏࡃࡐࡉࠧ༢")),
            bstack1l1l11l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥ༣"): env.get(bstack1l1l11l_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦ༤"))
        }
    if env.get(bstack1l1l11l_opy_ (u"ࠨࡃࡊࠤ༥")) == bstack1l1l11l_opy_ (u"ࠢࡵࡴࡸࡩࠧ༦") and env.get(bstack1l1l11l_opy_ (u"ࠣࡅࡌࡖࡈࡒࡅࡄࡋࠥ༧")) == bstack1l1l11l_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ༨"):
        return {
            bstack1l1l11l_opy_ (u"ࠥࡲࡦࡳࡥࠣ༩"): bstack1l1l11l_opy_ (u"ࠦࡈ࡯ࡲࡤ࡮ࡨࡇࡎࠨ༪"),
            bstack1l1l11l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ༫"): env.get(bstack1l1l11l_opy_ (u"ࠨࡃࡊࡔࡆࡐࡊࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤ༬")),
            bstack1l1l11l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤ༭"): env.get(bstack1l1l11l_opy_ (u"ࠣࡅࡌࡖࡈࡒࡅࡠࡌࡒࡆࠧ༮")),
            bstack1l1l11l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣ༯"): env.get(bstack1l1l11l_opy_ (u"ࠥࡇࡎࡘࡃࡍࡇࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࠨ༰"))
        }
    if env.get(bstack1l1l11l_opy_ (u"ࠦࡈࡏࠢ༱")) == bstack1l1l11l_opy_ (u"ࠧࡺࡲࡶࡧࠥ༲") and env.get(bstack1l1l11l_opy_ (u"ࠨࡔࡓࡃ࡙ࡍࡘࠨ༳")) == bstack1l1l11l_opy_ (u"ࠢࡵࡴࡸࡩࠧ༴"):
        return {
            bstack1l1l11l_opy_ (u"ࠣࡰࡤࡱࡪࠨ༵"): bstack1l1l11l_opy_ (u"ࠤࡗࡶࡦࡼࡩࡴࠢࡆࡍࠧ༶"),
            bstack1l1l11l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨ༷"): env.get(bstack1l1l11l_opy_ (u"࡙ࠦࡘࡁࡗࡋࡖࡣࡇ࡛ࡉࡍࡆࡢ࡛ࡊࡈ࡟ࡖࡔࡏࠦ༸")),
            bstack1l1l11l_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫༹ࠢ"): env.get(bstack1l1l11l_opy_ (u"ࠨࡔࡓࡃ࡙ࡍࡘࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣ༺")),
            bstack1l1l11l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ༻"): env.get(bstack1l1l11l_opy_ (u"ࠣࡖࡕࡅ࡛ࡏࡓࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢ༼"))
        }
    if env.get(bstack1l1l11l_opy_ (u"ࠤࡆࡍࠧ༽")) == bstack1l1l11l_opy_ (u"ࠥࡸࡷࡻࡥࠣ༾") and env.get(bstack1l1l11l_opy_ (u"ࠦࡈࡏ࡟ࡏࡃࡐࡉࠧ༿")) == bstack1l1l11l_opy_ (u"ࠧࡩ࡯ࡥࡧࡶ࡬࡮ࡶࠢཀ"):
        return {
            bstack1l1l11l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦཁ"): bstack1l1l11l_opy_ (u"ࠢࡄࡱࡧࡩࡸ࡮ࡩࡱࠤག"),
            bstack1l1l11l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦགྷ"): None,
            bstack1l1l11l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦང"): None,
            bstack1l1l11l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤཅ"): None
        }
    if env.get(bstack1l1l11l_opy_ (u"ࠦࡇࡏࡔࡃࡗࡆࡏࡊ࡚࡟ࡃࡔࡄࡒࡈࡎࠢཆ")) and env.get(bstack1l1l11l_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡅࡒࡑࡒࡏࡔࠣཇ")):
        return {
            bstack1l1l11l_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦ཈"): bstack1l1l11l_opy_ (u"ࠢࡃ࡫ࡷࡦࡺࡩ࡫ࡦࡶࠥཉ"),
            bstack1l1l11l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦཊ"): env.get(bstack1l1l11l_opy_ (u"ࠤࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡍࡉࡕࡡࡋࡘ࡙ࡖ࡟ࡐࡔࡌࡋࡎࡔࠢཋ")),
            bstack1l1l11l_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧཌ"): None,
            bstack1l1l11l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥཌྷ"): env.get(bstack1l1l11l_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢཎ"))
        }
    if env.get(bstack1l1l11l_opy_ (u"ࠨࡃࡊࠤཏ")) == bstack1l1l11l_opy_ (u"ࠢࡵࡴࡸࡩࠧཐ") and env.get(bstack1l1l11l_opy_ (u"ࠣࡆࡕࡓࡓࡋࠢད")) == bstack1l1l11l_opy_ (u"ࠤࡷࡶࡺ࡫ࠢདྷ"):
        return {
            bstack1l1l11l_opy_ (u"ࠥࡲࡦࡳࡥࠣན"): bstack1l1l11l_opy_ (u"ࠦࡉࡸ࡯࡯ࡧࠥཔ"),
            bstack1l1l11l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣཕ"): env.get(bstack1l1l11l_opy_ (u"ࠨࡄࡓࡑࡑࡉࡤࡈࡕࡊࡎࡇࡣࡑࡏࡎࡌࠤབ")),
            bstack1l1l11l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤབྷ"): None,
            bstack1l1l11l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢམ"): env.get(bstack1l1l11l_opy_ (u"ࠤࡇࡖࡔࡔࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢཙ"))
        }
    if env.get(bstack1l1l11l_opy_ (u"ࠥࡇࡎࠨཚ")) == bstack1l1l11l_opy_ (u"ࠦࡹࡸࡵࡦࠤཛ") and env.get(bstack1l1l11l_opy_ (u"࡙ࠧࡅࡎࡃࡓࡌࡔࡘࡅࠣཛྷ")) == bstack1l1l11l_opy_ (u"ࠨࡴࡳࡷࡨࠦཝ"):
        return {
            bstack1l1l11l_opy_ (u"ࠢ࡯ࡣࡰࡩࠧཞ"): bstack1l1l11l_opy_ (u"ࠣࡕࡨࡱࡦࡶࡨࡰࡴࡨࠦཟ"),
            bstack1l1l11l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧའ"): env.get(bstack1l1l11l_opy_ (u"ࠥࡗࡊࡓࡁࡑࡊࡒࡖࡊࡥࡏࡓࡉࡄࡒࡎࡠࡁࡕࡋࡒࡒࡤ࡛ࡒࡍࠤཡ")),
            bstack1l1l11l_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨར"): env.get(bstack1l1l11l_opy_ (u"࡙ࠧࡅࡎࡃࡓࡌࡔࡘࡅࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥལ")),
            bstack1l1l11l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧཤ"): env.get(bstack1l1l11l_opy_ (u"ࠢࡔࡇࡐࡅࡕࡎࡏࡓࡇࡢࡎࡔࡈ࡟ࡊࡆࠥཥ"))
        }
    if env.get(bstack1l1l11l_opy_ (u"ࠣࡅࡌࠦས")) == bstack1l1l11l_opy_ (u"ࠤࡷࡶࡺ࡫ࠢཧ") and env.get(bstack1l1l11l_opy_ (u"ࠥࡋࡎ࡚ࡌࡂࡄࡢࡇࡎࠨཨ")) == bstack1l1l11l_opy_ (u"ࠦࡹࡸࡵࡦࠤཀྵ"):
        return {
            bstack1l1l11l_opy_ (u"ࠧࡴࡡ࡮ࡧࠥཪ"): bstack1l1l11l_opy_ (u"ࠨࡇࡪࡶࡏࡥࡧࠨཫ"),
            bstack1l1l11l_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥཬ"): env.get(bstack1l1l11l_opy_ (u"ࠣࡅࡌࡣࡏࡕࡂࡠࡗࡕࡐࠧ཭")),
            bstack1l1l11l_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦ཮"): env.get(bstack1l1l11l_opy_ (u"ࠥࡇࡎࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣ཯")),
            bstack1l1l11l_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥ཰"): env.get(bstack1l1l11l_opy_ (u"ࠧࡉࡉࡠࡌࡒࡆࡤࡏࡄཱࠣ"))
        }
    if env.get(bstack1l1l11l_opy_ (u"ࠨࡃࡊࠤི")) == bstack1l1l11l_opy_ (u"ࠢࡵࡴࡸࡩཱིࠧ") and env.get(bstack1l1l11l_opy_ (u"ࠣࡄࡘࡍࡑࡊࡋࡊࡖࡈུࠦ")) == bstack1l1l11l_opy_ (u"ࠤࡷࡶࡺ࡫ཱུࠢ"):
        return {
            bstack1l1l11l_opy_ (u"ࠥࡲࡦࡳࡥࠣྲྀ"): bstack1l1l11l_opy_ (u"ࠦࡇࡻࡩ࡭ࡦ࡮࡭ࡹ࡫ࠢཷ"),
            bstack1l1l11l_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣླྀ"): env.get(bstack1l1l11l_opy_ (u"ࠨࡂࡖࡋࡏࡈࡐࡏࡔࡆࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧཹ")),
            bstack1l1l11l_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤེ"): env.get(bstack1l1l11l_opy_ (u"ࠣࡄࡘࡍࡑࡊࡋࡊࡖࡈࡣࡑࡇࡂࡆࡎཻࠥ")) or env.get(bstack1l1l11l_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡖࡉࡑࡇࡏࡍࡓࡋ࡟ࡏࡃࡐࡉོࠧ")),
            bstack1l1l11l_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤཽ"): env.get(bstack1l1l11l_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡎࡍ࡙ࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨཾ"))
        }
    if env.get(bstack1l1l11l_opy_ (u"࡚ࠧࡆࡠࡄࡘࡍࡑࡊࠢཿ")) == bstack1l1l11l_opy_ (u"ࠨࡔࡳࡷࡨྀࠦ"):
        return {
            bstack1l1l11l_opy_ (u"ࠢ࡯ࡣࡰࡩཱྀࠧ"): bstack1l1l11l_opy_ (u"ࠣࡘ࡬ࡷࡺࡧ࡬ࠡࡕࡷࡹࡩ࡯࡯ࠡࡖࡨࡥࡲࠦࡓࡦࡴࡹ࡭ࡨ࡫ࡳࠣྂ"),
            bstack1l1l11l_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧྃ"): bstack1ll111l11l_opy_ (u"ࠥࡿࡪࡴࡶ࠯ࡩࡨࡸ࠭࠭ࡓ࡚ࡕࡗࡉࡒࡥࡔࡆࡃࡐࡊࡔ࡛ࡎࡅࡃࡗࡍࡔࡔࡓࡆࡔ࡙ࡉࡗ࡛ࡒࡊࠩࠬࢁࢀ࡫࡮ࡷ࠰ࡪࡩࡹ࠮ࠧࡔ࡛ࡖࡘࡊࡓ࡟ࡕࡇࡄࡑࡕࡘࡏࡋࡇࡆࡘࡎࡊࠧࠪࡿ྄ࠥ"),
            bstack1l1l11l_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ྅"): env.get(bstack1l1l11l_opy_ (u"࡙࡙ࠧࡔࡖࡈࡑࡤࡊࡅࡇࡋࡑࡍ࡙ࡏࡏࡏࡋࡇࠦ྆")),
            bstack1l1l11l_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ྇"): env.get(bstack1l1l11l_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡎࡊࠢྈ"))
        }
    return {bstack1l1l11l_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢྉ"): None}
def get_host_info():
    uname = os.uname()
    return {
        bstack1l1l11l_opy_ (u"ࠤ࡫ࡳࡸࡺ࡮ࡢ࡯ࡨࠦྊ"): uname.nodename,
        bstack1l1l11l_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࠧྋ"): uname.sysname,
        bstack1l1l11l_opy_ (u"ࠦࡹࡿࡰࡦࠤྌ"): uname.machine,
        bstack1l1l11l_opy_ (u"ࠧࡼࡥࡳࡵ࡬ࡳࡳࠨྍ"): uname.version,
        bstack1l1l11l_opy_ (u"ࠨࡡࡳࡥ࡫ࠦྎ"): uname.machine
    }
def bstack1l1llll11l_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack1ll1111111_opy_():
    if bstack1l11l1ll1_opy_.get_property(bstack1l1l11l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨྏ")):
        return bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧྐ")
    return bstack1l1l11l_opy_ (u"ࠩࡸࡲࡰࡴ࡯ࡸࡰࡢ࡫ࡷ࡯ࡤࠨྑ")
def bstack1l1lll1l11_opy_(driver):
    info = {
        bstack1l1l11l_opy_ (u"ࠪࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩྒ"): driver.capabilities,
        bstack1l1l11l_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡯ࡤࠨྒྷ"): driver.session_id,
        bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࠭ྔ"): driver.capabilities[bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫྕ")],
        bstack1l1l11l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩྖ"): driver.capabilities[bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩྗ")],
        bstack1l1l11l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࠫ྘"): driver.capabilities[bstack1l1l11l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠩྙ")],
    }
    if bstack1ll1111111_opy_() == bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪྚ"):
        info[bstack1l1l11l_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹ࠭ྛ")] = bstack1l1l11l_opy_ (u"࠭ࡡࡱࡲ࠰ࡥࡺࡺ࡯࡮ࡣࡷࡩࠬྜ") if bstack1l11l1ll1_opy_.get_property(bstack1l1l11l_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ྜྷ")) else bstack1l1l11l_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵࡧࠪྞ")
    return info
def bstack111111l1_opy_(bstack1l1lllllll_opy_, url, data, config):
    headers = config[bstack1l1l11l_opy_ (u"ࠩ࡫ࡩࡦࡪࡥࡳࡵࠪྟ")]
    proxies = bstack1l1l1111_opy_(config, url)
    auth = config.get(bstack1l1l11l_opy_ (u"ࠪࡥࡺࡺࡨࠨྠ"), None)
    response = requests.request(
        bstack1l1lllllll_opy_,
        url=url,
        headers=headers,
        auth=auth,
        json=data,
        proxies=proxies
    )
    return response
def bstack11ll11ll1_opy_(bstack1ll11ll1l_opy_, size):
    bstack1llll1ll1l_opy_ = []
    while len(bstack1ll11ll1l_opy_) > size:
        bstack11ll1l111_opy_ = bstack1ll11ll1l_opy_[:size]
        bstack1llll1ll1l_opy_.append(bstack11ll1l111_opy_)
        bstack1ll11ll1l_opy_ = bstack1ll11ll1l_opy_[size:]
    bstack1llll1ll1l_opy_.append(bstack1ll11ll1l_opy_)
    return bstack1llll1ll1l_opy_
def bstack1ll1111l1l_opy_(message):
    os.write(1, bytes(message, bstack1l1l11l_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪྡ")))
    os.write(1, bytes(bstack1l1l11l_opy_ (u"ࠬࡢ࡮ࠨྡྷ"), bstack1l1l11l_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬྣ")))
def bstack1ll111l1ll_opy_():
    return os.environ[bstack1l1l11l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠪྤ")].lower() == bstack1l1l11l_opy_ (u"ࠨࡶࡵࡹࡪ࠭ྥ")
def bstack1lll111lll_opy_(bstack1ll111l1l1_opy_):
    return bstack1ll111l11l_opy_ (u"ࠩࡾࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄࡔࡎࡥࡕࡓࡎࢀ࠳ࢀ࡫࡮ࡥࡲࡲ࡭ࡳࡺࡽࠨྦ")
def bstack1lll111ll_opy_():
    return datetime.datetime.utcnow().isoformat() + bstack1l1l11l_opy_ (u"ࠪ࡞ࠬྦྷ")
def bstack1l1lllll11_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack1l1l11l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫྨ")
    else:
        return bstack1l1l11l_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬྩ")
def bstack1ll111lll1_opy_(val):
    return val.__str__().lower() == bstack1l1l11l_opy_ (u"࠭ࡴࡳࡷࡨࠫྪ")
def bstack1l1lllll1l_opy_(val):
    return val.__str__().lower() == bstack1l1l11l_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ྫ")
def bstack1ll1111l11_opy_(bstack1l1llll1l1_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack1l1llll1l1_opy_ as e:
                print(bstack1l1l11l_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࡾࢁࠥ࠳࠾ࠡࡽࢀ࠾ࠥࢁࡽࠣྫྷ").format(func.__name__, bstack1l1llll1l1_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack1ll111ll1l_opy_(bstack1l1llllll1_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack1l1llllll1_opy_(cls, *args, **kwargs)
            except bstack1l1llll1l1_opy_ as e:
                print(bstack1l1l11l_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡿࢂࠦ࠭࠿ࠢࡾࢁ࠿ࠦࡻࡾࠤྭ").format(bstack1l1llllll1_opy_.__name__, bstack1l1llll1l1_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack1ll111ll1l_opy_
    else:
        return decorator
def bstack1lll1111l1_opy_(bstack1ll1l1l111_opy_):
    if bstack1l1l11l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧྮ") in bstack1ll1l1l111_opy_ and bstack1l1lllll1l_opy_(bstack1ll1l1l111_opy_[bstack1l1l11l_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨྯ")]):
        return False
    if bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧྰ") in bstack1ll1l1l111_opy_ and bstack1l1lllll1l_opy_(bstack1ll1l1l111_opy_[bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨྱ")]):
        return False
    return True