# -*- coding: utf-8 -*-
"""uchinokocheck - うちの子チェックシート。

オリジナルキャラクター（うちの子）の設定を、フォーム入力とタグのチェックで
1枚の設定シートにまとめる単一ファイルFlaskアプリ。
入力内容はブラウザの localStorage にだけ保存され、サーバーには送信されない。
"""
import json

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# チェックリストのタグ定義（カテゴリごとに、重複のないタグ一覧を持つ）
TAG_GROUPS = [
{
"category": "外見の特徴",
"tags": [
"ロングヘア", "ショートヘア", "ツインテール", "ポニーテール",
"眼鏡", "ほくろ", "八重歯", "タレ目", "三白眼", "アホ毛",
"獣耳", "リボン",
],
},
{
"category": "性格",
"tags": [
"明るい", "クール", "天然", "努力家", "マイペース", "照れ屋",
"毒舌", "世話焼き", "元気", "おっとり", "しっかり者", "ツンデレ",
],
},
{
"category": "雰囲気・属性",
"tags": [
"不思議系", "王道主人公", "ライバル", "妹・弟系",
"お姉さん・お兄さん系", "ダーク", "ほんわか", "ミステリアス",
"かっこいい系", "かわいい系", "天才肌", "ヒーロー気質",
],
},
]

CSS = """
* { box-sizing: border-box;}
html, body { margin: 0; padding: 0;}
body {
background: #fdf6ef; color: #38303a;
font-family: "Hiragino Maru Gothic ProN", "Hiragino Sans", "Yu Gothic", sans-serif;
line-height: 1.7;
}
header { text-align: center; padding: 2rem 1rem 0.2rem;}
header h1 { font-size: 1.6rem; margin: 0; letter-spacing: 0.08em;}
header p { color: #97879b; font-size: 0.85rem; margin: 0.3rem 0 0;}
main { max-width: 1080px; margin: 0 auto; padding: 1.2rem 1rem 3rem;}
.layout { display: grid; grid-template-columns: 1fr 1fr; gap: 1.4rem; align-items: start;}
@media (max-width: 860px) {.layout { grid-template-columns: 1fr;}}
.panel {
background: #fff; border: 1px solid #ecdfe4; border-radius: 14px;
padding: 1.2rem 1.3rem 1.4rem;
}
.panel h2 { font-size: 1.05rem; margin: 0 0 0.8rem; letter-spacing: 0.06em;}
.field { margin-bottom: 0.85rem;}
.field label { display: block; font-size: 0.85rem; font-weight: bold; color: #6d5a70; margin-bottom: 0.25rem;}
.field input[type="text"],.field select,.field textarea {
width: 100%; font: inherit; font-size: 0.95rem; padding: 0.45rem 0.6rem;
border: 1px solid #d9c6cf; border-radius: 8px; background: #fffdfb; color: inherit;
}
.field textarea { min-height: 5.5rem; resize: vertical;}
.field input[type="color"] { width: 4.2rem; height: 2.2rem; border: 1px solid #d9c6cf; border-radius: 8px; background: #fff; padding: 0.15rem; cursor: pointer;}
fieldset { border: 1px dashed #d9b8c6; border-radius: 10px; margin: 0 0 1rem; padding: 0.7rem 0.8rem 0.9rem;}
legend { font-size: 0.9rem; font-weight: bold; color: #a04a72; padding: 0 0.4rem;}
label.tag {
display: inline-block; border: 1px solid #d9c6cf; border-radius: 999px;
padding: 0.12rem 0.7rem 0.12rem 0.5rem; margin: 0.18rem 0.15rem; font-size: 0.88rem;
cursor: pointer; background: #fffdfb; user-select: none;
}
label.tag input { margin-right: 0.3rem; accent-color: #d1588a;}
label.tag:has(input:checked) { background: #fdeef5; border-color: #d1588a; color: #a02c5e; font-weight: bold;}
.hint { font-size: 0.8rem; color: #97879b; margin-top: 0.4rem;}
.sticky { position: sticky; top: 0.8rem;}
@media (max-width: 860px) {.sticky { position: static;}}
.sheet {
--theme: #e88bb0;
background: #fff; border: 2px solid var(--theme); border-radius: 14px; overflow: hidden;
}
.sheet-band { height: 14px; background: var(--theme);}
.sheet-inner { padding: 1.1rem 1.3rem 1.3rem;}
.sheet-furigana { font-size: 0.8rem; letter-spacing: 0.35em; color: #97879b; min-height: 1.2em;}
.sheet-name { font-size: 1.7rem; font-weight: bold; line-height: 1.3; margin: 0.1rem 0 0.8rem;}
table.info { width: 100%; border-collapse: collapse; font-size: 0.92rem; margin-bottom: 1rem;}
table.info th, table.info td { border: 1px solid #eee0e6; padding: 0.35rem 0.6rem; text-align: left; vertical-align: top;}
table.info th { background: #fdf3f7; color: #6d5a70; width: 6.5rem; font-weight: bold; white-space: nowrap;}
.empty { color: #c4b3bd;}
.swatch { display: inline-block; width: 0.95em; height: 0.95em; border-radius: 4px; border: 1px solid #d9c6cf; vertical-align: -0.1em; margin-right: 0.4rem;}
.sheet h3 { font-size: 0.95rem; margin: 1rem 0 0.4rem; color: #a04a72; letter-spacing: 0.05em;}
.chips { min-height: 1.6em;}
.chip {
display: inline-block; border: 1px solid var(--theme); border-radius: 999px;
background: #fdf3f7; padding: 0.05rem 0.65rem; margin: 0.15rem 0.12rem; font-size: 0.85rem;
}
.section-text { white-space: pre-wrap; font-size: 0.93rem; margin: 0;}
.actions { margin-top: 1rem; display: flex; gap: 0.6rem; flex-wrap: wrap;}
button {
font: inherit; font-size: 0.92rem; cursor: pointer; border-radius: 999px;
padding: 0.5rem 1.2rem; border: 1px solid #d1588a; background: #d1588a; color: #fff;
}
button.sub { background: #fff; color: #a02c5e;}
button:hover { opacity: 0.88;}
footer { text-align: center; color: #b3a1ad; font-size: 0.8rem; padding: 0 1rem 2rem;}
"""

SCRIPT = """
var STORAGE_KEY = 'uchinokocheck-v1';
var DEFAULT_THEME = '#e88bb0';
var FIELDS = ['name', 'furigana', 'age', 'gender', 'pronoun', 'height',
'birthday', 'blood', 'themecolor', 'catchphrase', 'likes', 'dislikes', 'memo'];
var state = { fields: {}, tags: {}};

function loadState() {
try {
var raw = localStorage.getItem(STORAGE_KEY);
if (!raw) return;
var parsed = JSON.parse(raw);
if (parsed && parsed.fields) state.fields = parsed.fields;
if (parsed && parsed.tags) state.tags = parsed.tags;
} catch (e) {}
}

function saveState() {
try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state));} catch (e) {}
}

function fieldEl(name) { return document.getElementById('f-' + name);}

function readFields() {
FIELDS.forEach(function (name) {
var el = fieldEl(name);
if (el) state.fields[name] = el.value;
});
}

function applyFields() {
FIELDS.forEach(function (name) {
var el = fieldEl(name);
if (!el) return;
if (typeof state.fields[name] === 'string') el.value = state.fields[name];
});
if (!fieldEl('themecolor').value) fieldEl('themecolor').value = DEFAULT_THEME;
}

function buildTagGroups() {
var wrap = document.getElementById('tag-groups');
TAG_GROUPS.forEach(function (group) {
var fs = document.createElement('fieldset');
var lg = document.createElement('legend');
lg.textContent = group.category;
fs.appendChild(lg);
var selected = state.tags[group.category] || [];
group.tags.forEach(function (tag) {
var label = document.createElement('label');
label.className = 'tag';
var cb = document.createElement('input');
cb.type = 'checkbox';
cb.value = tag;
cb.checked = selected.indexOf(tag) >= 0;
cb.addEventListener('change', function () { onTagChange(group.category);});
label.appendChild(cb);
label.appendChild(document.createTextNode(tag));
fs.appendChild(label);
});
wrap.appendChild(fs);
});
}

function onTagChange(category) {
var boxes = document.querySelectorAll('#tag-groups input[type="checkbox"]');
var picked = [];
boxes.forEach(function (cb) {
var lg = cb.closest('fieldset').querySelector('legend').textContent;
if (lg === category && cb.checked) picked.push(cb.value);
});
state.tags[category] = picked;
saveState();
render();
}

function esc(s) {
return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function val(name) { return (state.fields[name] || '').trim();}

function infoRow(label, valueHtml) {
return '<tr><th>' + label + '</th><td>' + valueHtml + '</td></tr>';
}

function textOrEmpty(v) {
return v? esc(v): '<span class="empty">―</span>';
}

function render() {
var f = state.fields;
var theme = val('themecolor') || DEFAULT_THEME;
var sheet = document.getElementById('sheet');
sheet.style.setProperty('--theme', theme);
document.getElementById('pv-furigana').textContent = val('furigana');
document.getElementById('pv-name').textContent = val('name') || '（名前未入力）';
var rows = '';
rows += infoRow('年齢', textOrEmpty(val('age')));
rows += infoRow('性別', textOrEmpty(val('gender')));
rows += infoRow('一人称', textOrEmpty(val('pronoun')));
rows += infoRow('身長', textOrEmpty(val('height')));
rows += infoRow('誕生日', textOrEmpty(val('birthday')));
rows += infoRow('血液型', textOrEmpty(val('blood')));
rows += infoRow('テーマカラー',
'<span class="swatch" style="background:' + esc(theme) + '"></span>' + esc(theme));
document.getElementById('pv-info').innerHTML = rows;
var tagsHtml = '';
TAG_GROUPS.forEach(function (group) {
var picked = state.tags[group.category] || [];
tagsHtml += '<h3>' + esc(group.category) + '</h3><div class="chips">';
if (picked.length) {
picked.forEach(function (tag) {
tagsHtml += '<span class="chip">' + esc(tag) + '</span>';
});
} else {
tagsHtml += '<span class="empty">（未選択）</span>';
}
tagsHtml += '</div>';
});
document.getElementById('pv-tags').innerHTML = tagsHtml;
var sections = [['口癖', 'catchphrase'], ['好きなもの', 'likes'],
['苦手なもの', 'dislikes'], ['設定メモ', 'memo']];
var secHtml = '';
sections.forEach(function (pair) {
var v = val(pair[1]);
secHtml += '<h3>' + pair[0] + '</h3>';
secHtml += v
? '<p class="section-text">' + esc(v) + '</p>'
: '<p class="section-text empty">―</p>';
});
document.getElementById('pv-sections').innerHTML = secHtml;
}

function buildText() {
var lines = [''];
var name = val('name');
if (name) {
lines.push('名前：' + name + (val('furigana')? '（' + val('furigana') + '）': ''));
}
var basics = [['年齢', 'age'], ['性別', 'gender'], ['一人称', 'pronoun'],
['身長', 'height'], ['誕生日', 'birthday'], ['血液型', 'blood'],
['テーマカラー', 'themecolor']];
basics.forEach(function (pair) {
var v = val(pair[1]);
if (v) lines.push(pair[0] + '：' + v);
});
TAG_GROUPS.forEach(function (group) {
var picked = state.tags[group.category] || [];
if (picked.length) {
lines.push('■' + group.category);
lines.push(picked.join('、'));
}
});
var sections = [['口癖', 'catchphrase'], ['好きなもの', 'likes'],
['苦手なもの', 'dislikes'], ['設定メモ', 'memo']];
sections.forEach(function (pair) {
var v = val(pair[1]);
if (v) lines.push(pair[0] + '：' + v);
});
return lines.join('\\n');
}

function copySheet() {
var text = buildText();
var btn = document.getElementById('copy-btn');
function done() {
var old = btn.textContent;
btn.textContent = 'コピーしました';
setTimeout(function () { btn.textContent = old;}, 1600);
}
if (navigator.clipboard && navigator.clipboard.writeText) {
navigator.clipboard.writeText(text).then(done, done);
} else {
var ta = document.createElement('textarea');
ta.value = text;
document.body.appendChild(ta);
ta.select();
try { document.execCommand('copy');} catch (e) {}
document.body.removeChild(ta);
done();
}
}

function clearAll() {
if (!confirm('入力内容をすべて消します。よろしいですか？')) return;
try { localStorage.removeItem(STORAGE_KEY);} catch (e) {}
state = { fields: {}, tags: {}};
FIELDS.forEach(function (name) {
var el = fieldEl(name);
if (el) el.value = (name === 'themecolor')? DEFAULT_THEME: '';
});
document.querySelectorAll('#tag-groups input[type="checkbox"]').forEach(function (cb) {
cb.checked = false;
});
render();
}

function init() {
loadState();
buildTagGroups();
applyFields();
readFields();
FIELDS.forEach(function (name) {
var el = fieldEl(name);
if (el) el.addEventListener('input', function () { readFields(); saveState(); render();});
if (el) el.addEventListener('change', function () { readFields(); saveState(); render();});
});
document.getElementById('copy-btn').addEventListener('click', copySheet);
document.getElementById('clear-btn').addEventListener('click', clearAll);
render();
}

document.addEventListener('DOMContentLoaded', init);
"""

PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>うちの子チェックシート | uchinokocheck</title>
<style>{{ css|safe}}</style>
</head>
<body>
<header>
<h1>うちの子チェックシート</h1>
<p>uchinokocheck ― オリジナルキャラクターの設定シートを作るツール</p>
</header>
<main>
<div class="layout">
<section class="panel">
<h2>設定を入力する</h2>
<div class="field">
<label for="f-name">名前</label>
<input type="text" id="f-name" placeholder="例：桜井 はな">
</div>
<div class="field">
<label for="f-furigana">ふりがな</label>
<input type="text" id="f-furigana" placeholder="例：さくらい はな">
</div>
<div class="field">
<label for="f-age">年齢</label>
<input type="text" id="f-age" placeholder="例：16歳">
</div>
<div class="field">
<label for="f-gender">性別</label>
<input type="text" id="f-gender" placeholder="例：女">
</div>
<div class="field">
<label for="f-pronoun">一人称</label>
<input type="text" id="f-pronoun" placeholder="例：わたし">
</div>
<div class="field">
<label for="f-height">身長</label>
<input type="text" id="f-height" placeholder="例：158cm">
</div>
<div class="field">
<label for="f-birthday">誕生日</label>
<input type="text" id="f-birthday" placeholder="例：4月3日">
</div>
<div class="field">
<label for="f-blood">血液型</label>
<select id="f-blood">
<option value="">（未選択）</option>
<option value="A型">A型</option>
<option value="B型">B型</option>
<option value="O型">O型</option>
<option value="AB型">AB型</option>
<option value="不明">不明</option>
</select>
</div>
<div class="field">
<label for="f-themecolor">テーマカラー</label>
<input type="color" id="f-themecolor" value="#e88bb0">
</div>
<div class="field">
<label for="f-catchphrase">口癖</label>
<input type="text" id="f-catchphrase" placeholder="例：〜なのだ">
</div>
<div class="field">
<label for="f-likes">好きなもの</label>
<input type="text" id="f-likes" placeholder="例：甘いもの、昼寝">
</div>
<div class="field">
<label for="f-dislikes">苦手なもの</label>
<input type="text" id="f-dislikes" placeholder="例：早起き、辛いもの">
</div>
<h2>チェックリスト</h2>
<div id="tag-groups"></div>
<div class="field">
<label for="f-memo">設定メモ</label>
<textarea id="f-memo" placeholder="生い立ち、関係性、物語での役割など、自由にどうぞ"></textarea>
</div>
<p class="hint">入力内容はこのブラウザに自動保存されます（サーバーには送信されません）。</p>
</section>
<section class="sticky">
<div class="sheet" id="sheet">
<div class="sheet-band"></div>
<div class="sheet-inner">
<div class="sheet-furigana" id="pv-furigana"></div>
<div class="sheet-name" id="pv-name">（名前未入力）</div>
<table class="info"><tbody id="pv-info"></tbody></table>
<div id="pv-tags"></div>
<div id="pv-sections"></div>
</div>
</div>
<div class="actions">
<button id="copy-btn" type="button">文章でコピー</button>
<button id="clear-btn" type="button" class="sub">全部消す</button>
</div>
</section>
</div>
</main>
<footer>入力した設定はブラウザ内（localStorage）にのみ保存されます。</footer>
<script>
var TAG_GROUPS = {{ tag_groups_json|safe }};
{{ script|safe }}
</script>
</body>
</html>
"""


@app.route("/healthz")
def healthz():
    return jsonify({
        "status": "ok",
        "categories": len(TAG_GROUPS),
        "tags": sum(len(g["tags"]) for g in TAG_GROUPS),
    })


@app.route("/")
def index():
    return render_template_string(
        PAGE,
        css=CSS,
        script=SCRIPT,
        tag_groups_json=json.dumps(TAG_GROUPS, ensure_ascii=False),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
