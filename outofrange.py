# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from lxml import html
from pprint import pprint
import re
import csv
import collections
import time

# ランキングデータをパースして圏外のポケモンをリスト化する処理
def search_ranking():
    url = 'https://sv.pokedb.tokyo/pokemon/list'
    res = requests.get(url)

    soup = BeautifulSoup(res.text, 'html.parser')

    # すべてのランキングからポケモンに関するdivのみ抽出
    elems = soup.find_all('div',attrs={'class': 'column is-one-fifth-widescreen is-one-quarter-tablet is-half-mobile'})

    # 圏外のポケモンを格納するリストを作成
    oor_list = []

    # ランキングが圏外であればリストに格納
    for elem in elems:
        #print(elem)
        if "圏外" in elem.text:
            # 個別ページへのurlを導出
            poke_url = 'https://sv.pokedb.tokyo' + elem.find('a').get('href')
            poke_num = re.search(r'\d{4}-\d{2}',poke_url).group()
            # 個別urlをリストへ格納
            oor_list.append(poke_url)

    # シーズンと集計期間を取得する
    season = "-"
    for sel in soup.find_all('select'):
        if sel['name'] == 'season':
            for opt in sel.find_all('option'):
                if re.search(r'selected',str(opt)):
                    season = re.sub(r'(\d{4}/\d{1,2}/\d{1,2}-\d{4}/\d{1,2}/\d{1,2})$',r' \1',re.sub(r'\s','',opt.text))
                    print(season)

    # 更新日を取得する
    lxml_data = html.fromstring(str(soup))
    update_time = '更新日: ' + lxml_data.xpath('/html/body/main/div/div[1]/div[1]/div/div/span[2]')[0].text
    print(update_time)
    #print(season)
    #pprint(oor_list)
    return oor_list,season,update_time

def search_pokemon(oor_list,season,update_time):
    # 空の辞書型、リスト型の宣言
    poke_dict = {}
    all_list = []

    # ヘッダ部分を配列へ格納
    time_list = [season,update_time]
    all_list.append(time_list)
    head_list = ['全国No.','フォルム','ポケモン名','タイプ1','タイプ2','HP','こうげき','ぼうぎょ','とくこう','とくぼう','すばやさ','合計']
    all_list.append(head_list)

    # リストへ格納されているurlを解析する
    for oor_url in oor_list:
        print(oor_url)
        res = requests.get(oor_url)

        soup = BeautifulSoup(res.text, 'html.parser')
        lxml_data = html.fromstring(str(soup))

        # 必要な情報をxpathを指定してパース
        if lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[2]/div[1]/div[1]'):
            hp = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[2]/div[1]/div[1]/div[1]/span')[0].text
            attack = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[2]/div[1]/div[2]/div[1]/span')[0].text
            defense = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[2]/div[1]/div[3]/div[1]/span')[0].text
            sp_attack = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[2]/div[1]/div[4]/div[1]/span')[0].text
            sp_deffense = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[2]/div[1]/div[5]/div[1]/span')[0].text
            speed = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[2]/div[1]/div[6]/div[1]/span')[0].text
            stat_all = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[2]/div[1]/div[7]/div[1]/span')[0].text
            name = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[1]/div[1]/div[2]/div[1]/h1')[0].text
            type0 = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[1]/div[1]/div[2]/div[2]/div/div[1]/span')[0].text
            if lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[1]/div[1]/div[2]/div[2]/div/div[2]/span'):
                type1 = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[1]/div[1]/div[2]/div[2]/div/div[2]/span')[0].text
            else:
                type1 = "-"
            num = re.search(r'\d{4}-\d{2}',oor_url).group()
            number = str(int(num.split("-")[0]))
            form = str(int(num.split("-")[1]))

            # 辞書型の宣言(使ってない)
            poke_dict[num] = {}
            poke_dict[num]['name'] = name
            poke_dict[num]['type0'] = type0
            poke_dict[num]['type1'] = type1
            poke_dict[num]['hp'] = hp
            poke_dict[num]['attack'] = attack
            poke_dict[num]['defense'] = defense
            poke_dict[num]['sp_attack'] = sp_attack
            poke_dict[num]['sp_deffense'] = sp_deffense
            poke_dict[num]['speed'] = speed
            poke_dict[num]['stat_all'] = stat_all

            # 配列へ格納
            poke_list = [number,form,name,type0,type1,hp,attack,defense,sp_attack,sp_deffense,speed,stat_all]
            print(poke_list)

            # 二重配列で格納
            all_list.append(poke_list)

        # 戦闘中にフォルムが変わるポケモンはリスト形式のためxpathが変わる (ex コオリッポ)
        elif lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[2]/div[2]/ul/li'):
            for i in range(len(lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[2]/div[2]/ul/li'))):
                n = str(i + 1)
                hp = lxml_data.xpath(f'//*[@id="pokemon-basic-info"]/div/div[2]/div[2]/ul/li[{n}]/div[2]/div[1]/div[1]/span')[0].text
                attack = lxml_data.xpath(f'//*[@id="pokemon-basic-info"]/div/div[2]/div[2]/ul/li[{n}]/div[2]/div[2]/div[1]/span')[0].text
                defense = lxml_data.xpath(f'//*[@id="pokemon-basic-info"]/div/div[2]/div[2]/ul/li[{n}]/div[2]/div[3]/div[1]/span')[0].text
                sp_attack = lxml_data.xpath(f'//*[@id="pokemon-basic-info"]/div/div[2]/div[2]/ul/li[{n}]/div[2]/div[4]/div[1]/span')[0].text
                sp_deffense = lxml_data.xpath(f'//*[@id="pokemon-basic-info"]/div/div[2]/div[2]/ul/li[{n}]/div[2]/div[5]/div[1]/span')[0].text
                speed = lxml_data.xpath(f'//*[@id="pokemon-basic-info"]/div/div[2]/div[2]/ul/li[{n}]/div[2]/div[6]/div[1]/span')[0].text
                stat_all = lxml_data.xpath(f'//*[@id="pokemon-basic-info"]/div/div[2]/div[2]/ul/li[{n}]/div[2]/div[7]/div[1]/span')[0].text
                name = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[1]/div[1]/div[2]/div[1]/h1')[0].text
                type0 = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[1]/div[1]/div[2]/div[2]/div/div[1]/span')[0].text
                if lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[1]/div[1]/div[2]/div[2]/div/div[2]/span'):
                    type1 = lxml_data.xpath('//*[@id="pokemon-basic-info"]/div/div[1]/div[1]/div[2]/div[2]/div/div[2]/span')[0].text
                else:
                    type1 = "-"
                    num = re.search(r'\d{4}-\d{2}',oor_url).group()
                number = str(int(num.split("-")[0]))
                form = str(i)

                # 辞書型へ格納(使っていない)
                poke_dict[num] = {}
                poke_dict[num]['name'] = name
                poke_dict[num]['type0'] = type0
                poke_dict[num]['type1'] = type1
                poke_dict[num]['hp'] = hp
                poke_dict[num]['attack'] = attack
                poke_dict[num]['defense'] = defense
                poke_dict[num]['sp_attack'] = sp_attack
                poke_dict[num]['sp_deffense'] = sp_deffense
                poke_dict[num]['speed'] = speed
                poke_dict[num]['stat_all'] = stat_all

                # リストへ格納
                poke_list = [number,form,name,type0,type1,hp,attack,defense,sp_attack,sp_deffense,speed,stat_all]
                print(poke_list)
                # そして二重配列へ
                all_list.append(poke_list)

        time.sleep(1)

    #pprint(poke_dict)
    return all_list


def make_csv(pokemon_list):
    # 実行時のカレントディレクトリを参照
    file_path = "./pokemon_exc_rank150.csv"
    with open(file_path,'w') as f:
        writer = csv.writer(f)
        writer.writerows(pokemon_list)

if __name__ == "__main__":
    oor_list,season,update_time = search_ranking()
    all_list = search_pokemon(oor_list,season,update_time)
    print(all_list)
    make_csv(all_list)
