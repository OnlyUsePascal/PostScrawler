## Structure

```
def scrapeSite1(targetNumWeek):
    #your code here 

def scrapeSite2(targetNumWeek):
    #...

def webscrape(targetNumWeek=1):
    ...
    scrapeSite1(targetNumWeek)
    scrapeSite2(targetNumWeek)

# scrape the last 2 week
webscrape(2)
```

## How to use
```bash
$ git clone https://github.com/OnlyUsePascal/PostScrawler.git

$ cd PostScrawler/

# scrape default 1 week
$ python scrawlerSelenium.py

# scrape 10 week
$ python scrawlerSelenium.py 10
```
### Output structure
- this is shown when everything is done
  
    ```
    ** done
    ```
- output file is named `test.csv`

    ```
    === Chainlink ===
    2023-06-26,Announcing the Chainlink Spring 2023 Hackathon Winners,https://blog.chain.link/spring-2023-hackathon-winners/
    2023-06-21,Chainlink Economics 2.0: One-Year Update,https://blog.chain.link/chainlink-economics-2-0-one-year-update/
    2023-06-20,The Best Blockchain Course to Learn Solidity in 2023,https://blog.chain.link/blockchain-course-learn-solidity-web3/
    2023-06-19,Chainlink Product Update: Q2 2023,https://blog.chain.link/product-update-q2-2023/

    === Apple ===
    2023-06-22,Developer tools to create spatial experiences for Apple Vision Pro now available,https://www.apple.com/au/newsroom/2023/06/developer-tools-to-create-spatial-experiences-for-apple-vision-pro-now-available/
    ...
    ```

### Customize
Comment / Uncomment function callers to disable scraping:

```python
def webscrape(targetNumWeek=1):
    ...

    #start scrape
    # scrapeAcademyBinance(targetNumWeek)
    scrapeChainlink(targetNumWeek)
    # scrapeOpenAI(targetNumWeek)
    scrapeGoogleBlogAI(targetNumWeek)

    scrapeZkblab(targetNumWeek)
    # scrapeGoogleLab(targetNumWeek)
    scrapeApple(targetNumWeek)
    # scrapeForteLab(targetNumWeek)
    # scrapeAliAbdaal(targetNumWeek)
    # scrapeGfi(targetNumWeek)

    ...
```