__author__ = 'patrick'

import numpy as np

pound_to_euro = 1.2618898
dollar_to_euro = 1

def dollar(value):
    return value*dollar_to_euro

def pound(value):
    return value*pound_to_euro

def million(value):
    return value * 1000 * 1000

def billion(value):
    return 1000 * million(value)

##############################################################################

# BASE CALCULATIONS
# Taken from the Globecom paper we can perfectly encode a Blue-ray video in 32768 kBit/s that is 4096 kByte/s
# Suppose every movie is 90 minutes long we have 90*60*4096, which is 22.1184 Gigabyte
# Average movie size does not exceed 22.1184 GB
_movie_size = 22.1184  # in GB

# Let's assume a user watches 2 videos on demand per week = ~ 8 per month (so, if the user only uses it for this purpose, we can divide
# the monthly costs by 8 (or lower depending on data caps)
_usages = 8

# MARGINS

# BT profit margin of 11.92 % in March, 2014 http://ycharts.com/companies/BT/profit_margin
# Comcast profit margin of 10.75 % in March, 2014 http://ycharts.com/companies/CMCSA/profit_margin
# Due to profitable extra services this may be on the high side
#######################################################################################

_nsp_margin = (0.1192+0.1075)/2
_nsp_cost_lv = 1.0 - _nsp_margin

# Wuaki TV: 18.8% profit marin according to http://www.axonpartnersgroup.com/index.php/project/wuaki-tv/
# Netflix profit margin: 4.18% in March 2014 http://ycharts.com/companies/NFLX/profit_margin

_vod_cost_lv= 1 - 0.188 # content costs plus network transmission costs. Let's find some better estimates.
_vod_flat_cost_lv= 1 - 0.0418 # content costs plus network transmission costs. Let's find some better estimates.

# Transit constants:
# 1 Mbps is up to 305.939 GB per month
# 30 Mbps is up to 9178.17 per month
mbps_price_to_GB = 1/305.939

_transit_price = dollar(1.57)    # Dr. Peering projection for 2013
_transit_price_per_GB = _transit_price * mbps_price_to_GB
_transit_movie_price = _transit_price_per_GB*_movie_size

# PLAYER COUNT
_number_of_tier1_players = 13
_number_of_CDNS = 23
_number_of_transit_players = _number_of_tier1_players + _number_of_CDNS
_number_of_accessUSplayers = 3
_number_of_accessUKplayers = 11
_number_of_EC_subscribers = million(1.7) # Q4 2013; according to http://point-topic.com/free-analysis/global-iptv-subscriber-numbers-q4-2013/
_number_of_vod_players = 12 # includes rental substitutes


# DEP. FROM FUNGIBILITY (see spreadsheet)
_dep_fung_payment = 0           # Money or equivalent
_dep_fung_accessuk_ec = 0.8       # Network connectivity (Internet access to be precise) provided to the end customer
_dep_fung_US_access = 0.6      # Network connectivity provider to a content provider (e.g. VoD Platform)
_dep_fung_UK_access_termination = 0.6   # Termination service by the access NSP in the UK provided to the transit
_dep_fung_vod_ec = 0.8
_dep_fung_transit = 0.4

# ENTITY SIZES / MARKET SIZES

UK_VoD_size = pound(million(200))          # TODO: Seems only subscription-based for now. Maybe other data?. Commecial data from statista would exist, but access not purchased.
Global_VoD_size = dollar(billion(21.08))
Access_US_size = pound(billion(32))         # Ofcom -> POUNDS
Transit_size = dollar(billion(2.1+3.71))    # globally transit including CDN
Access_UK_size = pound(billion(4))          # Ofcom -> POUNDS

# Approach: Use Global size data for the VoD platform (they are global players) and the UK data for the EC market

entity_sizes = [UK_VoD_size, Global_VoD_size, Access_US_size, Transit_size, Access_UK_size]


## TRANSIT
_nsp_margin = (0.1192+0.1075)/2
_nsp_cost_lv = 1 -_nsp_margin

classical_transit_prices = [_transit_movie_price] * _number_of_tier1_players # Create a list of Tier-1 Transit prices, i.e., all the same prices here

# CDN Substitutes
CDN77 = 47.0/1000*_movie_size # CDN 77
MaxCDN = 50.55/1000*_movie_size # MaxCDN
Akamai = 350.0/1000*_movie_size # Akamai
Edgecase = 202.0/1000*_movie_size # Edgecase
CloudFront = 97.0/1000*_movie_size # CloudFront
Fastly = 97.0/1000*_movie_size # Fastly
Amazon = 97.0/1000*_movie_size # Amazon
Hibernia = 97.0/1000*_movie_size # Hibernia
Leaseweb = 37.59625/1000*_movie_size # Leaseweb

# CDN Substitutes with known prices C1
known_cdn_prices = [CDN77,MaxCDN,Akamai,Edgecase,CloudFront,Fastly,Amazon,Hibernia,Leaseweb]
cdn_prices = []
cdn_prices.extend(known_cdn_prices)     # extra list only used for avoiding mistakes later on

remaining_cdns = 14     # Number of CDNs with unknown prices
#average_cdn_price = 115.3495834 # per TB
#print(average_cdn_price)
#print(str(np.average(known_cdn_prices)))

# CDNs where price is not known
for i in range(0,remaining_cdns,1):
    cdn_prices.append(np.average(known_cdn_prices))
    #cdn_list_payment.append(dao.RelationshipInstance('accessUStoTransit_AVGCDN', (average_cdn_price + _transit_movie_price), 0, 0, 0.0))

# CDN Substitutes with known prices C2
#cdn_list = []


#for i in range(0,remaining_cdns,1):
    #cdn_list.append(dao.RelationshipInstance('TransitToAccessUS_AVGCDN', (average_cdn_price + _transit_movie_price), (_transit_movie_price + _nsp_cost_lv*average_cdn_price), 0, _dep_fung_transit))

# In total we have considered 23 CDNs


## ACCESS US

sum_us_access_price = np.sum([39.99, 70.99, 79.99])

rc_transit = _transit_movie_price * 39.99/sum_us_access_price        # own fee. 39.99 is the access pricing for consumers
tcn_transit = _transit_movie_price * 70.99/sum_us_access_price       # own fee
verizon_transit = _transit_movie_price * 79.99/sum_us_access_price   # own fee

us_access_prices_transitscheme = [rc_transit, tcn_transit, verizon_transit]

## VOD

vod_nowtv_price = pound(3.49)
vod_lovefilm_price = pound(3.49)
vod_blinkbox_price = pound(4.49)
vod_itunes_price = pound(4.49)
vod_wuaki_price = pound(4.49)
vod_google_play = pound(4.49)
vod_unlimited_tv = pound(4.49)
# 3 instances where price tag has not been found -> use average of 4.09 pounds
vod_average = pound(4.20) # Refers to virgincable, btvision, filmflex
vod_netflix_price = pound(6.99)/_usages
vod_lovefilm_alt_price = pound(5.99)/_usages

vod_prices_classic = [vod_nowtv_price, vod_lovefilm_price, vod_blinkbox_price, vod_itunes_price, vod_wuaki_price, vod_unlimited_tv, vod_google_play, vod_average, vod_average , vod_average]
vod_prices_flat = [vod_netflix_price, vod_lovefilm_alt_price]
vod_prices = []
vod_prices.extend(vod_prices_classic)
vod_prices.extend(vod_prices_flat)

# ACCESS UK

#Basic E Values
virgin_cable = pound(26.50/_usages)
sky = pound(35.0/_usages)
plusnet = pound(31.0/_usages)
talktalktalk = pound(22.7/_usages)
ee = pound(37.7/_usages)
directsavetelecom = pound(29.95/_usages)
johnlewis = pound(38.50/_usages)
eclipse = pound(39.95/_usages)
zen = pound(34.94/_usages)
# With data cap
BT = pound(31.0/1) #BT with 20 GB (normal competitor = one movie) ... floor(20/movie_size) would be 0, but it should work in practice.
ee_alt = pound(30.0/1) #EE with 25 GB (Substitute) = one movie

uk_access_prices = [virgin_cable, sky, plusnet, talktalktalk, ee, directsavetelecom, johnlewis, eclipse, zen, BT, ee_alt]

