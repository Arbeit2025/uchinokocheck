# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app as m


client = m.app.test_client()


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert data["categories"] == len(m.TAG_GROUPS)
    assert data["tags"] == sum(len(g["tags"]) for g in m.TAG_GROUPS)


def test_tag_groups_data_integrity():
    # カテゴリは3つ以上、各カテゴリのタグは8つ以上、カテゴリ内の重複なし
    assert len(m.TAG_GROUPS) >= 3
    categories = [g["category"] for g in m.TAG_GROUPS]
    assert len(categories) == len(set(categories))
    for g in m.TAG_GROUPS:
        assert len(g["tags"]) >= 8
        assert len(g["tags"]) == len(set(g["tags"]))
        assert all(t.strip() for t in g["tags"])
    names = {g["category"] for g in m.TAG_GROUPS}
    assert names == {"外見の特徴", "性格", "雰囲気・属性"}


def test_index_ok_and_form_fields():
    r = client.get("/")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    # フォーム項目のラベル
    for label in ["名前", "ふりがな", "年齢", "性別", "一人称", "身長",
                  "誕生日", "血液型", "テーマカラー", "口癖",
                  "好きなもの", "苦手なもの", "設定メモ"]:
        assert label in html
    # フォーム項目の入力欄
    for fid in ["f-name", "f-furigana", "f-age", "f-gender", "f-pronoun",
                "f-height", "f-birthday", "f-blood", "f-themecolor",
                "f-catchphrase", "f-likes", "f-dislikes", "f-memo"]:
        assert 'id="' + fid + '"' in html
    # 血液型の選択肢
    for blood in ["A型", "B型", "O型", "AB型"]:
        assert blood in html
    # テーマカラーは color input
    assert 'type="color"' in html
    # ボタン
    assert "文章でコピー" in html
    assert "全部消す" in html
    # localStorage のキー
    assert "uchinokocheck-v1" in html


def test_index_contains_all_tag_data():
    html = client.get("/").get_data(as_text=True)
    for g in m.TAG_GROUPS:
        assert g["category"] in html
        for tag in g["tags"]:
            assert tag in html


def test_script_not_escaped():
    # render_template_string で JS が HTML エスケープされると全機能が死ぬ（過去の事故）。
    html = client.get("/").get_data(as_text=True)
    assert "&#39;" not in html
    assert "localStorage.getItem(STORAGE_KEY)" in html
    assert "document.addEventListener('DOMContentLoaded', init)" in html
