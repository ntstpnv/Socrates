from bisect import insort_left
from datetime import datetime
from itertools import chain

from requests import Session
from streamlit import json, set_page_config, sidebar


URL_RAW = f"https://raw.githubusercontent.com/ntstpnv/Socrates/main/"

with Session() as s1:
    catalog = s1.get(f"{URL_RAW}catalog.json").json()


def get_log() -> dict:
    with Session() as s2:
        return s2.get(f"{URL_RAW}log.json").json()


set_page_config(layout="wide")

log = get_log()

last = sidebar.toggle("Новые результаты", value=True)
if last:
    ft_list = [(0, ""), (0, ""), (0, ""), (0, ""), (0, "")]
    for g, g_dict in log.items():
        for n, ti_dict in g_dict.items():
            for ti, r_list in ti_dict.items():
                for r in r_list:
                    ft, _, p, _ = r.split("=")
                    ft = int(ft)
                    if ft > ft_list[0][0]:
                        r = f"{g} = {n} = {catalog[ti]} = {p} из 30"
                        insort_left(ft_list, (ft, r))
                        del ft_list[0]
    json(
        {
            datetime.fromtimestamp(ft).strftime("%H:%M %d.%m.%y"): r
            for ft, r in reversed(ft_list)
        }
    )

group = sidebar.selectbox(
    "Учебная группа", None if last else log, index=None, placeholder="Надо выбрать"
)
if group:
    tn = sidebar.selectbox(
        "Название теста",
        {
            catalog[ti]
            for ti in chain.from_iterable(
                ti_dict.keys() for ti_dict in log[group].values()
            )
        },
        index=None,
        placeholder="Надо выбрать",
    )

    best, results = sidebar.toggle("Только лучшие попытки", value=True), {}
    if best:
        for n, ti_dict in log[group].items():
            ft_, et_min, p_max, m_ = None, 0, 0, None
            for ti, r_list in ti_dict.items():
                if catalog[ti] == tn:
                    for r in r_list:
                        ft, et, p, m = r.split("=")
                        ft, et, p = int(ft), int(et), int(p)
                        if p_max < p or p_max == p and et_min > et:
                            ft_, et_min, p_max, m_ = ft, et, p, m
            if ft_:
                results[n] = f"{p_max} из 30"
    else:
        for n, ti_dict in log[group].items():
            for ti, r_list in ti_dict.items():
                if catalog[ti] == tn:
                    for r in r_list:
                        ft, et, p, m = r.split("=")
                        ft, et = int(ft), int(et)
                        results.setdefault(n, {})
                        ft = datetime.fromtimestamp(ft).strftime("%H:%M %d.%m.%y")
                        et = f"{et // 60}:{et % 60:02}"
                        results[n][f"{ft} = {et} = {p} из 30"] = m
    json(results)
