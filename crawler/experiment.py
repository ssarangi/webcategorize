from crawler import *
from malcontent import *

if __name__ == '__main__':
    #http://www.free-daily-jigsaw-puzzles.com/
    #seed = {'www.free-daily-jigsaw-puzzles.com':['http://www.free-daily-jigsaw-puzzles.com/']}
    #http://69.42.67.28/traffic2/?VFJDSz0xMjcz
    seed = { 'www.bramasol.com':['http://www.bramasol.com/'],
             'www.code.google.com' : ['http://www.code.google.com/']}
    #seed = {'localhost':['http://localhost']}
    #seed = {'www.msnbc.msn.com': ['http://www.msnbc.msn.com/']}
    #seed = {'www.fetishtoons.biz':['http://www.fetishtoons.biz']}
    #seed = ['http://www.bitoffun.com/Cool_links.htm']
    #seed = ['http://localhost']
    #seed = ['http://www.easywarez.com/']
    reMap = {'((\%3C)|<)((\%2F)|\/)*[a-z0-9\%]+((\%3E)|>)' : ('CSS', ['regular', 'image', 'iframe'], Rule.EVIL),
             '((\%3C)|<)((\%69)|i|(\%49))((\%6D)|m|(\%4D))((\%67)|g|(\%47))[^\n]+((\%3E)|>)' : 
                 ('CSS image', ['regular', 'image', 'iframe'], Rule.EVIL)}
    cssRule = LinkRule(reMap)
    reMap2 = {'window\s*\.\s*open.+window\s*\.\s*focus': ('Pop under', Rule.MAY_BE_EVIL),
              "unescape\s*\(\s*'[^']*\%3C\%69\%66\%72\%61\%6D\%65[^']*'\s*\)": ('JS/Wonka', Rule.MAY_BE_EVIL)}
    popUnderRule = ContentRule(reMap2)
    u = Crawler(seed, 5, 10000, 15, 2, Malcontent, [[cssRule, popUnderRule, ExternalIframeRule()]])
    u.crawl()
