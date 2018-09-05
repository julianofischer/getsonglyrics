from bs4 import BeautifulSoup
import html2text, sys, requests


def main():
    url = sys.argv[1]

    splitted = url.split("/")
    output_name = splitted[-3] + "-" + splitted[-2]

    page = requests.get(url)
    page_text = page.text

    soup = BeautifulSoup(page_text, "html.parser")
    lyric = soup.find('article')
    
    text = html2text.html2text(lyric.prettify())

    with open(output_name, 'w') as f:
        f.write(text)


if __name__ == "__main__":
    main()