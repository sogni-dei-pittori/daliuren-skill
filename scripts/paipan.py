# -*- coding: utf-8 -*-
"""大六壬排盘器（标准法）
铁律：第一课的下神 = 日干本身（寄宫只用于定位干上神）。
取将：某传支所乘之将 = 该天盘支所临地盘宫里的将。
用法：python paipan.py --day 辛亥 --jiang 辰 --shi 亥 [--ming 申] [--xingnian 子]
"""
import argparse, io, sys


def _wrap(stream):
    try:
        enc = (stream.encoding or 'utf-8') if stream.isatty() else 'utf-8'
    except Exception:
        enc = 'utf-8'
    try:
        return io.TextIOWrapper(stream.buffer, encoding=enc, errors='replace')
    except Exception:
        return stream


sys.stdout = _wrap(sys.stdout)
sys.stderr = _wrap(sys.stderr)

Z = "子丑寅卯辰巳午未申酉戌亥"
G = "甲乙丙丁戊己庚辛壬癸"
JIGONG = {'甲': '寅', '乙': '辰', '丙': '巳', '戊': '巳', '丁': '未', '己': '未', '庚': '申', '辛': '戌', '壬': '亥', '癸': '丑'}
WX = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水',
      '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
GUI = {'甲': ('丑', '未'), '戊': ('丑', '未'), '庚': ('丑', '未'), '乙': ('子', '申'), '己': ('子', '申'),
       '丙': ('亥', '酉'), '丁': ('亥', '酉'), '壬': ('巳', '卯'), '癸': ('巳', '卯'), '辛': ('午', '寅')}
JS = "贵蛇朱合勾龙空虎常玄阴后"
JN = "贵后阴玄常虎空龙勾合朱蛇"
XING = {'子': '卯', '卯': '子', '寅': '巳', '巳': '申', '申': '寅', '丑': '戌', '戌': '未', '未': '丑',
        '辰': '辰', '午': '午', '酉': '酉', '亥': '亥'}
YIMA = {'申': '寅', '子': '寅', '辰': '寅', '寅': '申', '午': '申', '戌': '申',
        '巳': '亥', '酉': '亥', '丑': '亥', '亥': '巳', '卯': '巳', '未': '巳'}
XUNDING = {'甲子': '卯', '甲戌': '丑', '甲申': '亥', '甲午': '酉', '甲辰': '未', '甲寅': '巳'}
DAY_HOURS = [3, 4, 5, 6, 7, 8]  # 卯辰巳午未申


def liuqin(gan, zhi):
    a, b = WX[gan], WX[zhi]
    if a == b: return '兄弟'
    if SHENG[b] == a: return '父母'
    if SHENG[a] == b: return '子孙'
    if KE[b] == a: return '官鬼'
    return '妻财'


def kezei(gan, dz, k):
    lowers = [gan, k[0], dz, k[2]]
    out = []
    for up, low in zip(k, lowers):
        a, b = WX[up], WX[low]
        if KE[a] == b: out.append(('克', up))
        elif KE[b] == a: out.append(('贼', up))
        else: out.append(('比', up))
    return out


def shehai(cands, d):
    def depth(x):
        cur = (Z.index(x) - d) % 12
        wx = WX[x]
        cnt = 0
        for _ in range(12):
            cur = (cur + 1) % 12
            if KE[WX[Z[cur]]] == wx:
                cnt += 1
            if cur == Z.index(x):
                break
        return cnt
    ds = {x: depth(x) for x in cands}
    best = max(ds.values())
    ties = [x for x in cands if ds[x] == best]
    if len(ties) == 1:
        return ties[0], '涉害(受克深)'
    for grp, tag in (('寅申巳亥', '见机(取孟)'), ('子午卯酉', '察微(取仲)')):
        sel = [x for x in ties if Z[(Z.index(x) - d) % 12] in grp]
        if len(sel) == 1:
            return sel[0], tag
        if sel:
            ties = sel
    return ties[0], '涉害(先见)'


def bimu(cands, gan, d):
    cands = list(dict.fromkeys(cands))
    want = 0 if G.index(gan) % 2 == 0 else 1
    pick = [c for c in cands if Z.index(c) % 2 == want]
    if len(pick) == 1:
        return pick[0], '比用(知一)'
    return shehai(pick if pick else cands, d)


def paipan(day_gan, day_zhi, jiang, shi, ming=None, xingnian=None, year_zhi=None):
    d = (Z.index(jiang) - Z.index(shi)) % 12
    top = lambda i: (i + d) % 12
    gong = Z.index(JIGONG[day_gan])
    k = [Z[top(gong)], Z[top(top(gong))], Z[top(Z.index(day_zhi))], Z[top(top(Z.index(day_zhi)))]]
    kz = kezei(day_gan, day_zhi, k)
    zei = [x[1] for x in kz if x[0] == '贼']
    ke = [x[1] for x in kz if x[0] == '克']
    yang_day = G.index(day_gan) % 2 == 0
    method, chuan = '', []

    if d == 0:  # 伏吟
        if day_gan == '癸':
            method, chuan = '伏吟-有克(癸取丑戌未)', ['丑', '戌', '未']
        elif day_gan == '乙':
            x = XING[day_zhi]
            if x == day_zhi:
                x = Z[(Z.index(day_zhi) + 6) % 12]
            method, chuan = '伏吟-有克(乙杜传)', [k[0], day_zhi, x]
        else:
            first = k[0] if yang_day else k[2]
            method = '伏吟-' + ('自任' if yang_day else '自信')
            if XING[first] != first:
                second = XING[first]
                third = XING[second] if XING[second] != second else Z[(Z.index(second) + 6) % 12]
            else:
                second = k[2] if yang_day else k[0]
                third = XING[second] if XING[second] != second else Z[(Z.index(second) + 6) % 12]
            chuan = [first, second, third]
    elif d == 6:  # 返吟
        if zei or ke:
            if len(zei) == 1:
                first, tag = zei[0], '重审'
            elif len(zei) > 1:
                first, tag = bimu(zei, day_gan, d)
            elif len(ke) == 1:
                first, tag = ke[0], '元首'
            else:
                first, tag = bimu(ke, day_gan, d)
            method = '返吟-有克:' + tag
            chuan = [first, Z[top(Z.index(first))], Z[top(top(Z.index(first)))]]
        else:
            method = '返吟-无亲(无克)'
            chuan = [YIMA[day_zhi], k[2], k[0]]
    else:
        if len(zei) == 1:
            method, first = '重审', zei[0]
        elif len(zei) > 1:
            first, tag = bimu(zei, day_gan, d); method = tag
        elif len(ke) == 1:
            method, first = '元首', ke[0]
        elif len(ke) > 1:
            first, tag = bimu(ke, day_gan, d); method = tag
        else:
            sunbei = None
            if JIGONG[day_gan] != day_zhi:
                if k[1] == k[2]:
                    sunbei = '阳不备'
                elif k[0] == k[3]:
                    sunbei = '阴不备'
            yao = [x for x in k[1:] if KE[WX[x]] == WX[day_gan]]
            fan = [x for x in k[1:] if KE[WX[day_gan]] == WX[x]]
            if yao:
                first = yao[0] if len(yao) == 1 else bimu(yao, day_gan, d)[0]
                method = '遥克-蒿矢'
            elif fan:
                first = fan[0]; method = '遥克-弹射'
            elif JIGONG[day_gan] == day_zhi:
                first = Z[(Z.index(k[0]) + 2) % 12] if yang_day else Z[(Z.index(k[3]) - 2) % 12]
                method = '八专-无克(数三神)'
            elif sunbei:
                if yang_day:
                    he = {'甲': '己', '丙': '辛', '戊': '癸', '庚': '乙', '壬': '丁'}[day_gan]
                    first = Z[top(Z.index(JIGONG[he]))]
                else:
                    nxt = {'申': '子', '子': '辰', '辰': '申', '亥': '卯', '卯': '未', '未': '亥',
                           '寅': '午', '午': '戌', '戌': '寅', '巳': '酉', '酉': '丑', '丑': '巳'}[day_zhi]
                    first = Z[top(Z.index(nxt))]
                method = '别责(' + sunbei + ')'
            else:
                if yang_day:
                    first = Z[top(9)]; method = '昴星-虎视(阳)'
                else:
                    first = Z[(9 - d) % 12]; method = '昴星-冬蛇掩目(阴)'
            if method.startswith('八专') or method.startswith('别责'):
                chuan = [first, k[0], k[0]]
            elif method.startswith('昴星'):
                chuan = [first, k[2], k[0]] if yang_day else [first, k[0], k[2]]
            else:
                chuan = [first, Z[top(Z.index(first))], Z[top(top(Z.index(first)))]]
        if not chuan:
            chuan = [first, Z[top(Z.index(first))], Z[top(top(Z.index(first)))]]

    xs = (Z.index(day_zhi) - G.index(day_gan)) % 12
    xunshou = Z[xs]
    def dun(zhi):
        off = (Z.index(zhi) - xs) % 12
        return None if off >= 10 else G[off]
    kong = [Z[(xs + 10) % 12], Z[(xs + 11) % 12]]

    day_time = Z.index(shi) in DAY_HOURS
    gui = GUI[day_gan][0 if day_time else 1]
    g = (Z.index(gui) - d) % 12
    shun = Z[g] in '亥子丑寅卯辰'
    seq = JS if shun else JN
    jiang_map = {Z[(g + n) % 12]: seq[n] for n in range(12)}
    jiang_of = lambda z: jiang_map[Z[(Z.index(z) - d) % 12]]

    return dict(d=d, top=[Z[top(i)] for i in range(12)], k=k, kz=kz, chuan=chuan, method=method,
                dun=[dun(x) for x in chuan], lq=[liuqin(day_gan, x) for x in chuan],
                jiang=[jiang_of(x) for x in chuan], kong=kong, xunshou=xunshou, gui=gui, shun=shun,
                jiang_map=jiang_map, yima=YIMA[day_zhi], xingd=XUNDING.get('甲' + xunshou, '-'),
                gongshang=k[0], zhishang=k[2], day_time=day_time, year_zhi=year_zhi)


def report(day_gan, day_zhi, jiang, shi, ming=None, xingnian=None, year_zhi=None):
    r = paipan(day_gan, day_zhi, jiang, shi, ming, xingnian, year_zhi)
    L = []
    L.append('日课：%s%s日  月将%s  占时%s（%s占）' % (day_gan, day_zhi, jiang, shi, '昼' if r['day_time'] else '夜'))
    L.append('盘型：' + ('返吟' if r['d'] == 6 else ('伏吟' if r['d'] == 0 else '常盘 d=%d' % r['d'])))
    L.append('天盘：' + '  '.join('%s%s' % (Z[i], r['top'][i]) for i in range(12)))
    L.append('四课：上 %s ｜ 下 %s' % (' '.join(r['k']), ' '.join(['日干' + day_gan, r['k'][0], '支' + day_zhi, r['k'][2]])))
    L.append('克贼：' + '，'.join('%s%s' % (t, u) for t, u in r['kz']))
    L.append('三传：%s → %s → %s   （%s）' % (r['chuan'][0], r['chuan'][1], r['chuan'][2], r['method']))
    L.append('六亲：' + '／'.join(r['lq']) + '    遁干：' + '／'.join([x or '空' for x in r['dun']]))
    L.append('天将：' + '／'.join(r['jiang']) + '（贵%s临地盘%s，%s）' % (r['gui'], Z[(Z.index(r['gui']) - r['d']) % 12], '顺布' if r['shun'] else '逆布'))
    L.append('旬首：%s  旬空：%s%s  旬丁：%s  驿马：%s' % (r['xunshou'], r['kong'][0], r['kong'][1], r['xingd'], r['yima']))
    L.append('干上神：%s  支上神：%s' % (r['gongshang'], r['zhishang']))
    if ming: L.append('本命%s上神：%s' % (ming, r['top'][Z.index(ming)]))
    if xingnian: L.append('行年%s上神：%s' % (xingnian, r['top'][Z.index(xingnian)]))
    L.append('课体：' + ('、'.join(keti(day_gan, day_zhi, r['k'], r['chuan'], r, year_zhi)) or '（无自动标签）'))
    L.append('将盘：' + '  '.join('%s%s' % (z, r['jiang_map'][z]) for z in Z))
    return '\n'.join(L)


# ---------------- 课体标签 ----------------
LU = {'甲': '寅', '乙': '卯', '丙': '巳', '戊': '巳', '丁': '午', '己': '午', '庚': '申', '辛': '酉', '壬': '亥', '癸': '子'}
JUE = {'木': '申', '火': '亥', '金': '寅', '水': '巳'}
MU = {'甲': '未', '丙': '戌', '戊': '戌', '庚': '丑', '壬': '辰'}
SANHE = {frozenset('申子辰'): '润下(水局)', frozenset('亥卯未'): '曲直(木局)',
         frozenset('寅午戌'): '炎上(火局)', frozenset('巳酉丑'): '从革(金局)'}


def keti(day_gan, day_zhi, k, chuan, r, year_zhi=None):
    L = []
    idx = [Z.index(x) for x in chuan]
    if r['d'] == 0: L.append('伏吟')
    if r['d'] == 6: L.append('返吟')
    if JIGONG[day_gan] == day_zhi: L.append('八专(干支同位)')
    elif k[1] == k[2]: L.append('阳不备(缺支阳)')
    elif k[0] == k[3]: L.append('阴不备(缺支阴)')
    if len(set(chuan)) == 3:
        d1, d2 = (idx[1] - idx[0]) % 12, (idx[2] - idx[1]) % 12
        if (d1, d2) == (1, 1): L.append('进茹(连茹)')
        elif (d1, d2) == (11, 11): L.append('退茹')
        elif (d1, d2) == (2, 2): L.append('进间')
        elif (d1, d2) == (10, 10): L.append('退间')
    if frozenset(chuan) in SANHE: L.append('三合局:' + SANHE[frozenset(chuan)])
    if all(x in '寅申巳亥' for x in chuan): L.append('元胎(三传皆四孟)')
    if all(x in '辰戌丑未' for x in chuan): L.append('稼穑(三传皆四季土)')
    if '巳' in chuan and '戌' in chuan: L.append('铸印(巳戌互见)')
    if any(x in ('辰', '戌') for x in (k[0], k[2])): L.append('斩关(魁罡加日辰)')
    xs = (Z.index(day_zhi) - G.index(day_gan)) % 12
    xunshou, xunwei = Z[xs], Z[(xs + 9) % 12]
    if xunshou in chuan or xunshou == k[0]: L.append('六仪(仪神入传或临干)')
    duns = [d for d in r['dun'] if d]
    if {'乙', '丙', '丁'} <= set(duns): L.append('三奇(传遁乙丙丁)')
    elif set(duns) & {'乙', '丙', '丁'}: L.append('见奇(传遁含奇)')
    if xunwei in chuan or xunwei == k[0]: L.append('闭口(旬尾入传或临干)')
    if G.index(day_gan) % 2 == 1:
        lu = LU[day_gan]; wx = WX[lu]
        if wx in JUE and Z[(Z.index(lu) - r['d']) % 12] == JUE[wx]: L.append('四绝(阴日禄临绝)')
    if G.index(day_gan) % 2 == 0 and k[0] == MU.get(day_gan): L.append('四墓(阳日干上乘墓)')
    if year_zhi:
        g1 = {'亥': '寅', '子': '寅', '丑': '寅', '寅': '巳', '卯': '巳', '辰': '巳',
              '巳': '申', '午': '申', '未': '申', '申': '亥', '酉': '亥', '戌': '亥'}[year_zhi]
        g2 = {'亥': '戌', '子': '戌', '丑': '戌', '寅': '丑', '卯': '丑', '辰': '丑',
              '巳': '辰', '午': '辰', '未': '辰', '申': '未', '酉': '未', '戌': '未'}[year_zhi]
        if g1 in chuan or g1 in (k[0], k[2]): L.append('孤辰(' + g1 + ')')
        if g2 in chuan or g2 in (k[0], k[2]): L.append('寡宿(' + g2 + ')')
    return list(dict.fromkeys(L))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='大六壬排盘（标准法）')
    ap.add_argument('--day', required=True, help='日干支，如 辛亥')
    ap.add_argument('--jiang', required=True, help='月将，如 辰')
    ap.add_argument('--shi', required=True, help='占时，如 亥')
    ap.add_argument('--ming', default=None)
    ap.add_argument('--xingnian', default=None)
    ap.add_argument('--year', default=None, help='年支（孤辰寡宿用，可选）')
    a = ap.parse_args()
    if len(a.day) != 2 or a.day[0] not in G or a.day[1] not in Z or (Z.index(a.day[1]) - G.index(a.day[0])) % 2:
        sys.exit('错误：--day 须为六十甲子之一（如 辛亥、甲子）')
    for name, val in (('--jiang', a.jiang), ('--shi', a.shi), ('--ming', a.ming), ('--xingnian', a.xingnian), ('--year', a.year)):
        if val is not None and (len(val) != 1 or val not in Z):
            sys.exit('错误：' + name + ' 须为单个地支之一（如 子、丑）')
    print(report(a.day[0], a.day[1], a.jiang, a.shi, a.ming, a.xingnian, a.year))