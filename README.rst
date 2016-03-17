Intro
=====

This is a news crawler based on `Scrapy <http://scrapy.org>`_. Use the script "run.py" to run it. See file "config.yml" for the rss sources.

Configuration
=============

The settings and configuration related to Scrapy is still located in files "scrapy.cfg" and "newscrawler/settings.py". Other configuration including which rss sources to crawl is located in "config.yml".

config.yml
----------

The format of "config.yml" is YAML. The field "sources" in the file control which spiders (see :mod:`newscrawler.spiders.newsspiders`) and sources to used. For example, if the "sources" field is defined as::

        sources:
            general:
                - http://feeds.bbci.co.uk/news/rss.xml
                - http://feeds.bbci.co.uk/news/world/rss.xml

Then, the spider "general" (see :class:`GeneralSpider`) will be used to crawl the two urls.

Spiders
=======

Spiders are defined in :mod:`newscrawler.spiders.newsspiders`. All spiders should be defined as subclasses of :class:`_MySpider` so that configuration in "config.yml" will be honored.

:class:`SimpleGeneralSpider` downloads rss pages and extracts news items. It is possible that for some website, this spider cannot correctly parse and extracts the items. In this case, we can write new sub-classes and override methods `extract_...`.

:class:`GeneralSpider` is a subclass of :class:`SimpleGeneralSpider` which also download the web pages of news. Also, it stores news in MongoDB (for convenience, I didn't use Scrapy "Pipeline" to handle this).

Include more sources
====================

To include more news sources, you can just add more urls in "config.yml" (see `config.yml`_). But remember to make sure that the spider(s) for the new urls can correctly parse the rss document. If you want to check whether :class:`GeneralSpider` can be used, you can use :class:`SimpleGeneralSpider` instead and print the crawl items on screen so that checking is easier and the data will not be stored in database.

If all the spiders defined cannot be used. You need to either update the classes or define new classes (see `Spiders`_).
