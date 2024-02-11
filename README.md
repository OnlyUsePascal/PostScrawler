# PostScrawler
## About project

A Python script for scraping blogs from Blockchain-related websites.

Tools: Python + Selenium

### Note
- Site that are easy to break
  - okx: recommend to reduce endpoints
  - blockwork: have to turn off advertisement float
  - decrypt: have to turn off advertisement float
  - coinbase: cloudflare block

- recommend to use vpn (1.1.1.1)
- Check error at the `logs` directory if any
- Please check the [update log](./updateLog.md) for more infor

### Structure
```
.
├── scrawlerSelenium.py (main)
├── test.csv (output)
├── globals.py (global variables)
├── README.md
├── Utils
│   ├── correct_time_offset.py
│   ├── driver_options.py
│   ├── error_handler.py
│   └── write_to_list.py
└── WebScrapers
    ├── [site to scrape].py
    ├── ...
```

A list of scraped sites can be found [here](WebScrapers/__init__.py)


## How to use
```bash
$ git clone https://github.com/OnlyUsePascal/PostScrawler.git

$ cd PostScrawler/

$ pip install -r requirements.txt

# scrape default 1 week
$ python scrawlerSelenium.py

# scrape 10 week
$ python scrawlerSelenium.py 10
```
### Output structure
output file is named `test.csv`

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

## Customize
Toggle scraping site by comment/ uncomment function call in `scrawlerSelenium.py` 

```python

# everything start here
def webscrape(targetNumWeek=1):
    ...

    #start scrape
    # scrapeAcademyBinance(targetNumWeek)
    scrapeChainlink(targetNumWeek)
    # scrapeOpenAI(targetNumWeek)
    scrapeGoogleBlogAI(targetNumWeek)
    ...
```

## Contribution
<a href="https://github.com/OnlyUsePascal/PostScrawler/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=OnlyUsePascal/PostScrawler" />
</a>

