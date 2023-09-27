import requests
from bs4 import BeautifulSoup
from .models import Meaning, MeaningList, WordClass, UseFrequency


class DRAEws:
    def __init__(self, url: str = "https://dle.rae.es/") -> None:
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36"  # noqa
        }
        self.list_meanings: list[Meaning] = []

    def find_word(self, word: str) -> MeaningList:
        return self._get_request(word)

    def _get_request(self, word: str) -> MeaningList:
        url_to_find = self.url + word
        response = requests.get(url=url_to_find, headers=self.headers)
        status_code = response.status_code
        if status_code == 200:
            return self._get_meaning_from_html(response.content)
        raise Exception(f"_get_request failed status code: {status_code}")

    def _get_meaning_from_html(self, content: str)->MeaningList:
        soup = BeautifulSoup(content, "html.parser")
        results = soup.find(id="resultados")
        article = results.article
        if article:
            meanings = article.find_all("p", "j")
            for meaning in meanings:
                meaning_model = self._get_meaning_model(meaning)
                self.list_meanings.append(meaning_model)
        return MeaningList(meanings=self.list_meanings.copy())

        
    def _get_meaning_model(self, html_content: BeautifulSoup):
        word_class, use_frequency = self._handle_abbrs(html_content)        
        meaning = self._handle_meaning_html(html_content,word_class,use_frequency)
        return Meaning(
            meaning=meaning,
            word_class=word_class,
            use_frequency=use_frequency
        )

    def _handle_meaning_html(self, html_content: BeautifulSoup, word_class:WordClass, use_frequency: list[UseFrequency]):
        meaning_text = html_content.get_text()
        meaning = meaning_text.replace(word_class.abbreviation,'')
        meaning = self._replacing_abbrs(meaning,use_frequency=use_frequency)
        meaning = self._replacing_spaces(meaning)
        meaning = self._replacing_nums(meaning, html_content)
        return meaning.strip()

    def _replacing_nums(self, meaning: str, html_content: BeautifulSoup):
        num = html_content.find('span','n_acep')
        num = num.get_text()
        return meaning.replace(num,'')
    
    def _replacing_spaces(self, meaning:str):
        meaning = meaning.replace("   "," ")
        meaning = meaning.replace("  "," ")
        return meaning
    
    def _replacing_abbrs(self,meaning:str, use_frequency: list[UseFrequency]):
        use_freq_text = [element.abbreviation for element in use_frequency]     
        use_freq_text.sort(key=len,reverse=True)
        for element in use_freq_text:
            meaning = meaning.replace(element,'')
        return meaning
    
    def _handle_abbrs(self, html_content: BeautifulSoup):
        abbrs_html = html_content.find_all("abbr")
        word_class = self._word_class(abbrs_html[0])
        use_frequencies = self._use_frequent_classes(abbrs_html[1::])
        return word_class, use_frequencies

    def _word_class(self, class_html: BeautifulSoup) -> WordClass:
        description = class_html["title"]
        abbr = class_html.get_text()
        return WordClass(description=description, abbreviation=abbr)

    def _use_frequent_classes(self, use_frequency_html: list[BeautifulSoup]):
        use_frequency_list: list[UseFrequency] = []
        for element in use_frequency_html:
            description = element["title"]
            abbr = element.get_text()
            use_freq = UseFrequency(
                abbreviation=abbr,
                description=description,
            )
            use_frequency_list.append(use_freq)
        return use_frequency_list

        