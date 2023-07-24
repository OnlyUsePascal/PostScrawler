from WebScrapers import academy_binance, chain_link, open_ai, google_blog_ai, developer_archives, alchemy_blog, decrypt, cointelegraph, coin_desk, hak_research, zkblab, google_lab, apple, forte_lab, ali_abdaal, gfi, bankless, coin98, vitalik
from globals import fileName
import sys


# everything start here
def webscrape(targetNumWeek=1):
    # reset
    with open(fileName, 'w') as file:
        file.flush()

    print(f'scraping weeks: {targetNumWeek}')

    # academy_binance.scrapeAcademyBinance(targetNumWeek)
    # chain_link.scrapeChainlink(targetNumWeek)
    # open_ai.scrapeOpenAI(targetNumWeek)
    # google_blog_ai.scrapeGoogleBlogAI(targetNumWeek)
    # developer_archives.scrapeDevelopersArchives(targetNumWeek)
    # alchemy_blog.scrapeAlchemyBlog(targetNumWeek)
    # decrypt.scrapeDecrypt(targetNumWeek)
    # cointelegraph.scrapeCointelegraph(targetNumWeek)
    # coin_desk.scrapeCoinDesk(targetNumWeek)
    # hak_research.scrapeHakResearch1(targetNumWeek)

    # zkblab.scrapeZkblab(targetNumWeek)
    # google_lab.scrapeGoogleLab(targetNumWeek)
    # apple.scrapeApple(targetNumWeek)
    # forte_lab.scrapeForteLab(targetNumWeek)
    # ali_abdaal.scrapeAliAbdaal(targetNumWeek)
    # gfi.scrapeGfi(targetNumWeek)
    # bankless.scrapeBankless(targetNumWeek)
    # coin98.scrapeCoin98(targetNumWeek)
    # vitalik.scrapeVitalik(targetNumWeek)
    # hak_research.scrapeHakResearch(targetNumWeek)
    print('** done')


# start scraping
if __name__ == '__main__':
    inputWeek = 1

    if (len(sys.argv) > 1):
        inputWeek = int(sys.argv[1])

    webscrape(inputWeek)
