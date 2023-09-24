import unittest
from mongolian2ipa import mongolian2ipa
from mongolian2ipa.helpers import check_male_female_word, WordGender, check_first_level_vowel


class MongoliaIPATest(unittest.TestCase):
    def test_a(self):
        result = mongolian2ipa('a')
        self.assertEqual(result, 'a')

    def test_aa(self):
        result = mongolian2ipa('аа')
        self.assertEqual(result, 'aː')

    def test_ai(self):
        result = mongolian2ipa('ай')
        self.assertEqual(result, 'æː')

    def test_a_with_i_ii(self):
        result = mongolian2ipa('ань')
        self.assertEqual(result[0], 'æ')

    def test_male(self):
        result = check_male_female_word('машин')
        self.assertEqual(result, WordGender.MALE)

    def test_female(self):
        result = check_male_female_word('ээж')
        self.assertEqual(result, WordGender.FEMALE)

    def test_first_vowel(self):
        result = check_first_level_vowel('намар', 1)
        self.assertEqual(result, True)

    def test_not_first_vowel(self):
        result = check_first_level_vowel('намар', 3)
        self.assertEqual(result, False)

    def test_amsar(self):
        result = mongolian2ipa('амсар')
        self.assertEqual(result, 'amsər')

    def test_aimag(self):
        result = mongolian2ipa('айраг')
        self.assertEqual(result, 'æːrək')

    def test_darlagdsan(self):
        result = mongolian2ipa('дарлагсад')
        self.assertEqual(result, 'tarɬəksət')

    def test_ijil(self):
        result = mongolian2ipa('ижил')
        self.assertEqual(result, 'iʧəɬ')

    def test_ishig(self):
        result = mongolian2ipa('ишиг')
        self.assertEqual(result, 'iʃək')

    def test_ulger(self):
        result = mongolian2ipa('үлгэр')
        self.assertEqual(result, 'uɬkər')

    def test_niigem(self):
        result = mongolian2ipa('нийлмэл')
        self.assertEqual(result, 'niːɬməɬ')

    def test_omog(self):
        result = mongolian2ipa('омог')
        self.assertEqual(result, 'ɔmək')

    def test_oodon(self):
        result = mongolian2ipa('оодон')
        self.assertEqual(result, 'ɔːtəŋ')

    def test_orlog(self):
        result = mongolian2ipa('өрлөг')
        self.assertEqual(result, 'өrɬək')

    def test_horog(self):
        result = mongolian2ipa('хөрөг')
        self.assertEqual(result, 'xөrək')

    def test_gueg(self):
        result = mongolian2ipa('гүег')
        self.assertEqual(result, 'kujək')

    def test_jayg(self):
        result = mongolian2ipa('жаяг')
        self.assertEqual(result, 'ʧajək')

    def test_hayg(self):
        result = mongolian2ipa('хаяг')
        self.assertEqual(result, 'χajək')

    def test_aagim(self):
        result = mongolian2ipa('аагим')
        self.assertEqual(result, 'æːqəm')

    def test_aavgui(self):
        result = mongolian2ipa('аавгүй')
        self.assertEqual(result, 'aːwkui')

    def test_aagarhah(self):
        result = mongolian2ipa('аагархах')
        self.assertEqual(result, 'aːqərχəχ')

    def test_aadaih(self):
        result = mongolian2ipa('аадайх')
        self.assertEqual(result, 'aːtæːχ')

    def test_aajim(self):
        result = mongolian2ipa('аажим')
        self.assertEqual(result, 'æːʧəm')

    def test_aandaa(self):
        result = mongolian2ipa('аандаа')
        self.assertEqual(result, 'aːntaː')

    def test_aarnig(self):
        result = mongolian2ipa('аарниг')
        self.assertEqual(result, 'aːrnək')

    def test_hil(self):
        result = mongolian2ipa('хил')
        self.assertEqual(result, 'xiɬ')

    def test_ijil(self):
        result = mongolian2ipa('ижил')
        self.assertEqual(result, 'iʧəɬ')

    def test_shim(self):
        result = mongolian2ipa('шим')
        self.assertEqual(result, 'ʃim')

    def test_hel(self):
        result = mongolian2ipa('хэл')
        self.assertEqual(result, 'xeɬ')

    def test_em(self):
        result = mongolian2ipa('эм')
        self.assertEqual(result, 'em')

    def test_hal(self):
        result = mongolian2ipa('хал')
        self.assertEqual(result, 'χaɬ')

    def test_hali(self):
        result = mongolian2ipa('халь')
        self.assertEqual(result, 'χæɬ')

    def test_agi(self):
        result = mongolian2ipa('агь')
        self.assertEqual(result, 'æk')

    def test_hol(self):
        result = mongolian2ipa('хол')
        self.assertEqual(result, 'χɔɬ')

    def test_och(self):
        result = mongolian2ipa('оч')
        self.assertEqual(result, 'ɔʧʰ')

    def test_holi(self):
        result = mongolian2ipa('холь')
        self.assertEqual(result, 'χœɬ')

    def test_mori(self):
        result = mongolian2ipa('морь')
        self.assertEqual(result, 'mœr')

    def test_hul(self):
        result = mongolian2ipa('хул')
        self.assertEqual(result, 'χoɬ')

    def test_us(self):
        result = mongolian2ipa('ус')
        self.assertEqual(result, 'os')

    def test_huli(self):
        result = mongolian2ipa('хуль')
        self.assertEqual(result, 'χʏɬ')

    def test_uri(self):
        result = mongolian2ipa('урь')
        self.assertEqual(result, 'ʏr')

    def test_hol2(self):
        result = mongolian2ipa('хөл')
        self.assertEqual(result, 'xөɬ')

    def test_onor(self):
        result = mongolian2ipa('өнөр')
        self.assertEqual(result, 'өnər')

    def test_hul2(self):
        result = mongolian2ipa('хүл')
        self.assertEqual(result, 'xuɬ')

    def test_sur(self):
        result = mongolian2ipa('сүр')
        self.assertEqual(result, 'sur')

    def test_hiil(self):
        result = mongolian2ipa('xийл')
        self.assertEqual(result, 'xiːɬ')

    def test_niilmel(self):
        result = mongolian2ipa('нийлмэл')
        self.assertEqual(result, 'niːɬməɬ')

    def test_heel(self):
        result = mongolian2ipa('хээл')
        self.assertEqual(result, 'xeːɬ')

    def test_ireerei(self):
        result = mongolian2ipa('ирээрэй')
        self.assertEqual(result, 'ireːreː')

    def test_aaruul(self):
        result = mongolian2ipa('ааруул')
        self.assertEqual(result, 'aːroːɬ')

    def test_aali(self):
        result = mongolian2ipa('ааль')
        self.assertEqual(result, 'æːɬ')

    def test_ail(self):
        result = mongolian2ipa('айл')
        self.assertEqual(result, 'æːɬ')

    def test_hool(self):
        result = mongolian2ipa('хоол')
        self.assertEqual(result, 'χɔːɬ')

    def test_ooli(self):
        result = mongolian2ipa('ойл')
        self.assertEqual(result, 'œːɬ')

    def test_noiton(self):
        result = mongolian2ipa('нойтон')
        self.assertEqual(result, 'nœːtʰəŋ')

    def test_uurag(self):
        result = mongolian2ipa('уураг')
        self.assertEqual(result, 'oːrək')

    def test_huuli(self):
        result = mongolian2ipa('хууль')
        self.assertEqual(result, 'χʏːɬ')

    def test_dugui(self):
        result = mongolian2ipa('дугуй')
        self.assertEqual(result, 'toqoi')

    def test_hodoo(self):
        result = mongolian2ipa('хөдөө')
        self.assertEqual(result, 'xөtөː')

    def test_suu(self):
        result = mongolian2ipa('сүү')
        self.assertEqual(result, 'suː')

    def test_zuitei(self):
        result = mongolian2ipa('зүйтэй')
        self.assertEqual(result, 'ʦuitʰeː')

    def test_ymbuu(self):
        result = mongolian2ipa('ембүү')
        self.assertEqual(result, 'jempuː')

    def test_yeven(self):
        result = mongolian2ipa('еэвэн')
        self.assertEqual(result, 'jeːwəŋ')

    def test_yrool(self):
        result = mongolian2ipa('ерөөл')
        self.assertEqual(result, 'jөrөːɬ')

    def test_hoyo(self):
        result = mongolian2ipa('хөеө')
        self.assertEqual(result, 'xөjөː')

    def test_yndan(self):
        result = mongolian2ipa('яндан')
        self.assertEqual(result, 'jantəŋ')

    def test_yam(self):
        result = mongolian2ipa('яам')
        self.assertEqual(result, 'jaːm')

    def test_yri(self):
        result = mongolian2ipa('ярь')
        self.assertEqual(result, 'jær')

    def test_yirah(self):
        result = mongolian2ipa('яйрах')
        self.assertEqual(result, 'jæːrəχ')

    def test_yorool(self):
        result = mongolian2ipa('ёроол')
        self.assertEqual(result, 'jɔrɔːɬ')

    def test_yoton(self):
        result = mongolian2ipa('ёотон')
        self.assertEqual(result, 'jɔːtʰəŋ')

    def test_yonhigor(self):
        result = mongolian2ipa('ёнхигор')
        self.assertEqual(result, 'jœŋχəqər')

    def test_ym(self):
        result = mongolian2ipa('юм')
        self.assertEqual(result, 'jom')

    def test_yuhan(self):
        result = mongolian2ipa('юухан')
        self.assertEqual(result, 'joːχəŋ')

    def test_guanz(self):
        result = mongolian2ipa('гуанз')
        self.assertEqual(result, 'qwaːnʦ')

    def test_guai(self):
        result = mongolian2ipa('гуай')
        self.assertEqual(result, 'qwæː')

    def test_baruun(self):
        result = mongolian2ipa('баруун')
        self.assertEqual(result, 'paroːŋ')

    def test_pal(self):
        result = mongolian2ipa('пал')
        self.assertEqual(result, 'pʰaɬ')

    def test_tal(self):
        result = mongolian2ipa('тал')
        self.assertEqual(result, 'tʰaɬ')

    def test_aduu(self):
        result = mongolian2ipa('адуу')
        self.assertEqual(result, 'atoː')

    def test_lham(self):
        result = mongolian2ipa('Лхам')
        self.assertEqual(result, 'ɬʰam')


if __name__ == '__main__':
    unittest.main()
