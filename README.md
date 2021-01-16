# clipanda

京都大学サイバーラーニングスペースPandAのCLIアプリケーションです。一部の手間のかかる処理を自動で行います。

## インストール

### using system installed python
`requests`モジュールに依存しています。pipなどを用いて予めインストールしておいて下さい。

```
$ python3 -m pip install requests
$ python3 clipanda.py -h
```

### using runtime included binary
[こちら](https://github.com/face0u0/clipanda/releases)からダウンロードして下さい。（linuxのみ）

```
$ chmod u+x ./clipanda
$ ./clipanda -h
```

## 使い方

オプションは`-h`オプションを指定して確認することも可能です。
```
$ clipanda -h
$ clipanda sites -h
```

### ログイン
ほとんどの操作でログインが必要なため、`clipanda login`コマンドを用いてcookieを書き出します。

認証が必要なページは書き出されたcookieを指定することでアクセスが可能です。

```
$ clipanda login -u {ecs-id} -o
Password:
```
`-o`オプションは引数にファイル名を指定しますが、引数がないとき、デフォルトで`.cookies`に保存されます。`-p`オプションを用いてそのままパスワードを指定することも可能です。
```
$ clipanda login -u {ecs-id} -p {password} -o
```

### サイト一覧を表示
```
$ clipanda sites [-c {cookie-file}]
```
`--site-type`を指定することで絞り込みが可能です。例えば`course`を指定すると通常の講義のみが出力されます。
```
$ clipanda sites [-c {cookie-file}] --site-type course
```
`--only-site-id`は`site-id`のみを出力します。

### 授業資料をダウンロード
各サイト（講義）の資料の一括ダウンロードが可能です。
```
$ clipanda resources-dl [-c {cookie-file}] -s {site-id}
```
`site-id`は`clipanda sites`コマンドを用いて取得します。
`-d`オプションを指定することでダウンロード先のディレクトリを指定できます。

### 課題ファイルをダウンロード
各サイト（講義）の課題の一括ダウンロードも可能です。
```
$ clipanda assignments-dl [-c {cookie-file}] -s {site-id}
```
オプションは`clipanda resources-dl`とほぼ同じです。
